import calendar
from datetime import datetime, date, timedelta
import json
from django.db import connection
from froxa.utils.connectors.libra_connector import OracleConnector
from froxa.utils.utilities.funcions_file import get_short_date
from produccion.models import DetalleEntradasEquivCC, EquivalentsHead
from produccion.repository.equivalents_price.upload_data_file import upload_csv
from produccion.utils.get_me_stock_file import consumo_pasado, get_last_changed_value, get_me_stock_now, obtener_dias_restantes_del_mes, obtener_rangos_meses, obtener_rangos_meses7, pedidos_pendientes, verificar_mes
from dateutil.relativedelta import relativedelta

from produccion.utils.sent_email_file import aviso_expediente_sin_precio

def recalculate_equiv_with_contaner(request):

    id = request.GET.get('id')
    equiv_data = []
    oracle     = OracleConnector()
    oracle.connect()
    
    if id and id.isdigit() and int(id) > 0:
        equiv = EquivalentsHead.objects.filter(id=id).values('id', 'article_name', 'alternative').order_by()
    else:
        equiv = EquivalentsHead.objects.all().values('id', 'article_name', 'alternative').order_by('id')
    equiv = list(equiv)

    for eq in equiv:
        listArtEquiv = json.loads(eq['alternative'])
        only_code    = []
        for article in listArtEquiv:
            only_code += [str(article['code'])]
        equiv_data += [
            {
                'id'                        : eq['id'],
                'padre_name'                : eq['article_name'],
                'articles'                  : only_code,
                'consiste_de_alternativos'  : [],
                'costes_fecha'              : [],
                'expediente_sin_precios'    : [],
            }
        ]

    # we hare looking current stock and price for each article

    for eq1 in equiv_data:
        estado_actual = []
        listadoArticulos = eq1['articles']
        for codeArt in listadoArticulos:
            stockPrice = get_me_stock_now(codeArt, oracle)
            estado_actual += [stockPrice]
        eq1['consiste_de_alternativos'] = estado_actual

    
    # calculate the common of price and stock of the equivalents

    for eq2 in equiv_data:
        formula_top_ud   = 0
        unidades_stock   = 0
        suma_precios     = 0
        i = 0
        lineas_array  = eq2['consiste_de_alternativos']

        if len(eq2['consiste_de_alternativos']) == 0:
            eq2['padre_valoracion_actual'] = {'precio_kg': 0, 'stock_kg': 0 }

        for customArticle in lineas_array:
            # ignoro los que tienen stock y precio 0
            if float(customArticle[0]['stock'] or 0) > 0 and float(customArticle[0]['precio'] or 0) == 0:
                continue
            i += 1
            formula_top_ud += float(customArticle[0]['stock'] or 0) * float(customArticle[0]['precio'] or 0)
            unidades_stock += float(customArticle[0]['stock'] or 0)
            suma_precios   += float(customArticle[0]['precio'] or 0)
               
            if unidades_stock == 0:
                eq2['padre_valoracion_actual'] = {'precio_kg': suma_precios / i, 'stock_kg': unidades_stock }
            else:
                eq2['padre_valoracion_actual'] = {'precio_kg': formula_top_ud /  unidades_stock, 'stock_kg': unidades_stock }
           

    EXPEDIENTES_SIN_PRECIO_FINAL = []
    
    # obtain range months
    rango_meses = obtener_rangos_meses()
    for eq3 in equiv_data:
        fechas_desde_hasta = []
        for rango in rango_meses:
            fechas_desde_hasta += [{'desde':rango[0], 'hasta':rango[1], 'info_suma_llegadas': 0, 'info_suma_consumo':0}]
        eq3['rango'] = fechas_desde_hasta


    # I iterante the data ranges and search for  arrivals WITCHOUT CONTAINER AND WITH CONTAINER
    LAST_CHANGE_VAL      = get_last_changed_value(oracle)
    for eq4 in equiv_data:
        arr_codigos_erp = eq4['articles']
        iterations = 0

        for r_fechas in eq4['rango']:
            r_fechas['llegadas'] = pedidos_pendientes(oracle, arr_codigos_erp, r_fechas, EXPEDIENTES_SIN_PRECIO_FINAL, iterations, LAST_CHANGE_VAL)
            r_fechas['consumo']  = consumo_pasado(oracle, arr_codigos_erp, r_fechas) 
            iterations += 1

    oracle.close()

    # 9. STOCK AND PRICE
    for eq5 in equiv_data:
        PRECIO    = float(eq5['padre_valoracion_actual']['precio_kg'] or 0)
        STOCK     = float(eq5['padre_valoracion_actual']['stock_kg'] or 0)
 
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


    # 10.
    today = datetime.today()
    mes_actual = (today.replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    mes_mas1   = ((today + relativedelta(months=1)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    mes_mas2   = ((today + relativedelta(months=2)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    mes_mas3   = ((today + relativedelta(months=3)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    mes_mas4   = ((today + relativedelta(months=4)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    mes_mas5   = ((today + relativedelta(months=5)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    mes_mas6   = ((today + relativedelta(months=6)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    mes_mas7   = ((today + relativedelta(months=7)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")

    for itemQ in equiv_data:
        
        eqArt = EquivalentsHead.objects.get(id=itemQ['id'])
        eqArt.kg_act    = float(itemQ['padre_valoracion_actual']['stock_kg'] or 0)
        eqArt.price_act = float(itemQ['padre_valoracion_actual']['precio_kg'] or 0)

        for rango in itemQ['rango']:                                 
            if rango['hasta'] == mes_actual:
               eqArt.kg0    = float(rango['stock_final_rango'] or 0)
               eqArt.price0 = float(rango['precio_con_llegada'] or 0)

            if rango['hasta'] == mes_mas1:
               eqArt.kg1    = float(rango['stock_final_rango'] or 0)
               eqArt.price1 = float(rango['precio_con_llegada'] or 0)

            if rango['hasta'] == mes_mas2:
               eqArt.kg2    = float(rango['stock_final_rango'] or 0)
               eqArt.price2 = float(rango['precio_con_llegada'] or 0)

            if rango['hasta'] == mes_mas3:
               eqArt.kg3    = float(rango['stock_final_rango'] or 0)
               eqArt.price3 = float(rango['precio_con_llegada'] or 0)

            if rango['hasta'] == mes_mas4:
               eqArt.kg4    = float(rango['stock_final_rango'] or 0)
               eqArt.price4 = float(rango['precio_con_llegada'] or 0)

            if rango['hasta'] == mes_mas5:
               eqArt.kg5    = float(rango['stock_final_rango'] or 0)
               eqArt.price5 = float(rango['precio_con_llegada'] or 0)

            if rango['hasta'] == mes_mas6:
               eqArt.kg6    = float(rango['stock_final_rango'] or 0)
               eqArt.price6 = float(rango['precio_con_llegada'] or 0)

            if rango['hasta'] == mes_mas7:
               eqArt.kg7    = float(rango['stock_final_rango'] or 0)
               eqArt.price7 = float(rango['precio_con_llegada'] or 0)

        todayDay = date.today()
        tomorrow = todayDay + timedelta(days=1)
        # precio_estandar_equival price, only recalculate the last day of the month
        if tomorrow.day == 1:
            eqArt.precio_estandar_equival = (eqArt.price_act + eqArt.price1) / 2

        eqArt.save()  


    DetalleEntradasEquivCC.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute("ALTER SEQUENCE produccion_detalleentradasequivcc_id_seq RESTART WITH 1;")

    for eq6 in equiv_data:
        NAME  = eq6['padre_name']
        STOCK = float(eq6['padre_valoracion_actual']['stock_kg'] or 0)
        PRICE = float(eq6['padre_valoracion_actual']['precio_kg'] or 0)

        deecc = DetalleEntradasEquivCC()
        deecc.name         = NAME
        deecc.entrada      = 'Fecha '+get_short_date()+' ESTADO ACTUAL'
        deecc.stock_actual = STOCK
        deecc.pcm_actual   = PRICE
        deecc.save()

        rangos = eq6['rango']
        for rango in rangos:

            if rango['llegadas'] and len(rango['llegadas']) > 0:
                rango['llegadas'].sort(key=lambda x: x["FECHA_PREV_LLEGADA"])

                for llegada in rango['llegadas']:
                    idCont = ''
                    if llegada['ENTIDAD'] == 'EXP': idCont = llegada['NUM_EXPEDIENTE']
                    
                    deecc = DetalleEntradasEquivCC()
                    deecc.name         = NAME
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

            deecc = DetalleEntradasEquivCC()
            deecc.name         = NAME
            deecc.entrada  = 'Fecha '+rango['hasta']+' Resultado mes'
            deecc.consumo_prod = CONSUMO_PROD
            deecc.consumo_vent = CONSUMO_VENT
            deecc.calc_eur = PRICE
            deecc.calc_kg  = STOCK
            deecc.save()

    
    upload_csv('1detalle_entradas_equiv_cc')
    upload_csv('2equivalents_head')
    upload_csv('3proyeccion-costes-con-contenedor')

    aviso_expediente_sin_precio(request, EXPEDIENTES_SIN_PRECIO_FINAL)

    return equiv_data