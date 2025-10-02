import calendar
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import connection
from froxa.utils.connectors.libra_connector import OracleConnector
from froxa.utils.utilities.funcions_file import get_short_date
from produccion.models import EmbarkedIndividualRatingDetail, EmbarkedIndividualRatingHorizontal
from produccion.repository.embarcado_con_sin_cont.articulos_file import get_me_market, give_me_that_are_in_play, llegadas_pendientes
from produccion.repository.equivalents_price.upload_data_file import upload_csv
from produccion.utils.get_me_stock_file import consumo_pasado, get_last_changed_value, get_me_stock_now, obtener_dias_restantes_del_mes, obtener_rangos_meses12, pedidos_pendientes, verificar_mes
from produccion.utils.sent_email_file import aviso_expediente_sin_precio


def embarcado_art_con_sin_cont(request):
    oracle = OracleConnector()
    oracle.connect()

    LAST_CHANGE_VAL      = get_last_changed_value(oracle)
    codigos_art_11_month = give_me_that_are_in_play(oracle)
    
    # we hare looking current stock and price for each article

    for eq1 in codigos_art_11_month:
        eq1['precio_stock'] = get_me_stock_now(eq1['code'], oracle)
   

    # obtain range months
    rango_meses = obtener_rangos_meses12()
    for eq3 in codigos_art_11_month:
        fechas_desde_hasta = []
        for rango in rango_meses:
            fechas_desde_hasta += [{'desde':rango[0], 'hasta':rango[1], 'info_suma_llegadas': 0, 'info_suma_consumo':0}]
        eq3['rango'] = fechas_desde_hasta


    EXPEDIENTES_SIN_PRECIO_FINAL = []


    # I iterante the data ranges and search for  arrivals WITCHOUT CONTAINER AND WITH CONTAINER
    for eq4 in codigos_art_11_month:
        iterations = 0

        for r_fechas in eq4['rango']:
            r_fechas['llegadas'] = llegadas_pendientes(oracle, [eq4['code']], r_fechas, EXPEDIENTES_SIN_PRECIO_FINAL, iterations, LAST_CHANGE_VAL)
            r_fechas['consumo']  = consumo_pasado(oracle, [eq4['code']], r_fechas) 
            iterations += 1

    oracle.close()

    # 9. STOCK AND PRICE
    for eq5 in codigos_art_11_month:
        PRECIO    = float(eq5['precio_stock'][0]['precio'] or 0)
        STOCK     = float(eq5['precio_stock'][0]['stock'] or 0)
 
        for rango_fechasG in eq5['rango']:
            
            # exist arrivals START
            if rango_fechasG['llegadas'] and len(rango_fechasG['llegadas']) > 0:
                for llegadaG in rango_fechasG['llegadas']:
                    PRECIO = ((float(PRECIO) * float(STOCK)) + (float(llegadaG['CANTIDAD'] or 0) * float(llegadaG['PRECIO_EUR'] or 0))) / (float(llegadaG['CANTIDAD'] or 0) + STOCK)
                    rango_fechasG['info_suma_llegadas'] += float(llegadaG['CANTIDAD'] or 0)
                    STOCK                               += float(llegadaG['CANTIDAD'] or 0)
                    
            # exist arrivals FIN
            rango_fechasG['precio_con_llegada'] = PRECIO
            CONSUMO = 0

            # exist consum START
            if rango_fechasG['consumo'] and len(rango_fechasG['consumo']) > 0:     
                for consumA in rango_fechasG['consumo']:
                    CONSUMO += float(consumA['CANTIDAD'])
                
                if verificar_mes(rango_fechasG['hasta']) == "mes actual":
                    fecha_dt = datetime.strptime(rango_fechasG['hasta'], "%Y-%m-%d").date()
                    numero_dias = calendar.monthrange(fecha_dt.year, fecha_dt.month)[1]
                    dias_restantes = obtener_dias_restantes_del_mes()
                    CONSUMO = CONSUMO / numero_dias * dias_restantes
                        
                rango_fechasG['info_suma_consumo'] -= CONSUMO
            # exist consum FIN      
    
            STOCK = STOCK - CONSUMO
            if STOCK < 0:
                STOCK = 0
            rango_fechasG['stock_final_rango'] = STOCK


    EmbarkedIndividualRatingDetail.objects.all().delete()
    EmbarkedIndividualRatingHorizontal.objects.all().delete()

    with connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE produccion_embarketindividualrating_id_seq RESTART WITH 1;")

    # 10.
    # today = datetime.today()
    # mes_actual = (today.replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    # mes_mas1   = ((today + relativedelta(months=1)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    # mes_mas2   = ((today + relativedelta(months=2)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    # mes_mas3   = ((today + relativedelta(months=3)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    # mes_mas4   = ((today + relativedelta(months=4)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    # mes_mas5   = ((today + relativedelta(months=5)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    # mes_mas6   = ((today + relativedelta(months=6)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    # mes_mas7   = ((today + relativedelta(months=7)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d") 
    # mes_mas8   = ((today + relativedelta(months=8)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    # mes_mas9   = ((today + relativedelta(months=9)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    # mes_mas10  = ((today + relativedelta(months=10)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
   

    for x in codigos_art_11_month:     
        NAME  = x['name']
        CODE  = x['code']
        MERCADO, FAMILIA, SUBFAMILIA = get_me_market(oracle, x['code'])
 
  
        embar = EmbarkedIndividualRatingDetail()
        embar.name         = NAME
        embar.code         = CODE
        embar.mercado      = MERCADO
        embar.familia      = FAMILIA
        embar.subfamilia   = SUBFAMILIA
        embar.entrada      = 'Fecha '+get_short_date()+' ESTADO ACTUAL'
        embar.stock_actual = STOCK = float(x['precio_stock'][0]['stock'] or 0)
        embar.pcm_actual   = PRICE = float(x['precio_stock'][0]['precio'] or 0)
        embar.save()

        horinzontal = EmbarkedIndividualRatingHorizontal()
        horinzontal.name       = NAME
        horinzontal.code       = CODE
        horinzontal.mercado    = MERCADO
        horinzontal.familia    = FAMILIA
        horinzontal.subfamilia = SUBFAMILIA
        horinzontal.fecha      = get_short_date()
        horinzontal.stock      = STOCK
        horinzontal.precio     = PRICE
        horinzontal.save()

        rangos = x['rango']
        for rango in rangos:
            if rango['llegadas'] and len(rango['llegadas']) > 0:
                rango['llegadas'].sort(key=lambda x: x["FECHA_PREV_LLEGADA"])

                for llegada in rango['llegadas']:
                    idCont = ''
                    if llegada['ENTIDAD'] == 'EXP': idCont = llegada['NUM_EXPEDIENTE']
                    
                    deecc = EmbarkedIndividualRatingDetail()
                    deecc.name         = NAME
                    deecc.code         = CODE
                    deecc.mercado      = MERCADO
                    deecc.familia      = FAMILIA
                    deecc.subfamilia   = SUBFAMILIA
                    deecc.entrada      = 'Fecha '+str(llegada['FECHA_PREV_LLEGADA'])[:10]+' Art. '+str(llegada['ARTICULO'])+' '+str(llegada['ENTIDAD'])+' '+str(llegada['NUMERO'])+' '+str(idCont)
                    deecc.entrada_kg   = float(llegada['CANTIDAD'] or 0)
                    deecc.entrada_eur  = float(llegada['PRECIO_EUR'] or 0)
                    
                    PRICE              = ((STOCK * PRICE) + ( deecc.entrada_kg *  deecc.entrada_eur)) / (STOCK + deecc.entrada_kg)
                    deecc.calc_eur     = PRICE
                    STOCK             += deecc.entrada_kg
                    deecc.calc_kg      = STOCK
                    deecc.save()

    
            CONSUMO_PROD = 0
            CONSUMO_VENT = 0
            if rango['consumo'] and len(rango['consumo']) > 0:    
                for consumo in rango['consumo']:
                    if consumo['CONSUMO'] == 'P_VENTA':
                        CONSUMO_VENT += float(consumo['CANTIDAD'] or 0)
                    else:
                        CONSUMO_PROD += float(consumo['CANTIDAD'] or 0)

                if verificar_mes(rango['hasta']) == "mes actual":
                    fecha_dt = datetime.strptime(rango_fechasG['hasta'], "%Y-%m-%d").date()
                    numero_dias = calendar.monthrange(fecha_dt.year, fecha_dt.month)[1]
                    dias_restantes = obtener_dias_restantes_del_mes()
                    CONSUMO_VENT = CONSUMO_VENT / numero_dias * dias_restantes
                    CONSUMO_PROD = CONSUMO_PROD / numero_dias * dias_restantes
        
            STOCK = STOCK - CONSUMO_PROD - CONSUMO_VENT
            if STOCK < 0: STOCK = 0

            deecc = EmbarkedIndividualRatingDetail()
            deecc.name         = NAME
            deecc.code         = CODE
            deecc.mercado      = MERCADO
            deecc.familia      = FAMILIA
            deecc.subfamilia   = SUBFAMILIA
            deecc.entrada      = 'Fecha '+rango['hasta']+' Resultado mes'
            deecc.consumo_prod = CONSUMO_PROD
            deecc.consumo_vent = CONSUMO_VENT
            deecc.calc_eur     = PRICE
            deecc.calc_kg      = STOCK
            deecc.save()

            horinzontal = EmbarkedIndividualRatingHorizontal()
            horinzontal.name        = NAME
            horinzontal.code        = CODE
            horinzontal.mercado     = MERCADO
            horinzontal.familia     = FAMILIA
            horinzontal.subfamilia  = SUBFAMILIA
            horinzontal.fecha       = rango['hasta']
            horinzontal.stock       = STOCK
            horinzontal.precio      = PRICE
            horinzontal.save()


    aviso_expediente_sin_precio(request, EXPEDIENTES_SIN_PRECIO_FINAL)
    upload_csv('4entradas-con-sin-contenedor-calculo-precio-stock')
    upload_csv('5entradas-con-sin-contenedor-calculo-precio-stock-horizontal')

    return codigos_art_11_month




def embarcado_get_all(request):
    embs = EmbarkedIndividualRatingDetail.objects.all().values('id', 'name', 'code', 'entrada', 'stock_actual', 'pcm_actual', 'consumo_prod', 'consumo_vent', 'entrada_kg', 'entrada_eur', 'calc_kg', 'calc_eur').order_by('name', 'id')
    embs = list(embs)
    return embs
