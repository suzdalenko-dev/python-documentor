import calendar
import json
from froxa.utils.connectors.libra_connector import OracleConnector
from froxa.utils.utilities.funcions_file import json_encode_all
from froxa.utils.utilities.smailer_file import SMailer
from produccion.models import ArticleCostsHead, ArticleCostsLines, ExcelLinesEditable
from produccion.repository.embarcado_con_sin_cont.embarcado_file import embarcado_art_con_sin_cont
from produccion.repository.equivalents_price.recalc_equi_file import recalculate_equiv_with_contaner
from produccion.utils.get_me_stock_file import consumo_pasado, get_last_changed_value, get_me_stock_now, obtener_dias_restantes_del_mes, obtener_rangos_meses, pedidos_pendientes, verificar_mes
from datetime import datetime
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from produccion.utils.sent_email_file import aviso_expediente_sin_precio

"""
1. comentar si no tengo STOCK se coge asi todo el precio que marca libra
2. hay articulos que tienen precio 0, los mostrare en rojo
3. los expedientes en $ que valor de cambio aplicar y si hay que cambia el valor de cambio que se aplica
4. solo se usan los expedientes que tienen contenedor asignado
5. 
"""

def recalculate_price_projections(request):
    oracle = OracleConnector()
    oracle.connect()

    # 1. FROXA DB going to look for parent articles 
    
    articulos_pardes = None
    code = request.GET.get('code')

    if code and code.isdigit() and int(code) > 0:
        # http://127.0.0.1:8000/produccion/get/0/0/recalculate_price_projections/?code=40141
        articulos_pardes = ArticleCostsHead.objects.filter(article_code=code).values('id', 'article_code','article_name')
    else:
        articulos_pardes = ArticleCostsHead.objects.all().values('id', 'article_code', 'article_name')
    
    # 2. FROXA DB going to look for the ingredientes of parent articles
    
    articulos_data = []
    for a in articulos_pardes:
        lineas = ArticleCostsLines.objects.filter(parent_article=a['article_code']).values('parent_article', 'article_code', 'article_name','percentage','alternative')
        lineas = list(lineas)

        articulos_data += [{
            'id'              : a['id'],
            '__article__erp'  : str(a['article_code']),
            '__article__name' : a['article_name'], 
            'lineas'          : lineas,
            'precio_padre_act': 0,
            'costes_fecha'    : [],
            'expediente_sin_precios': [],
        }]

    # 3. FROXA DB convert erp codes into a string +"codigos_erp": "306302401, 306302431"


    for itemA in articulos_data:
        lineas_array = itemA['lineas']

        for lineas_itemA in lineas_array:
            lineas_itemA['parent_article'] = str(lineas_itemA['parent_article'])
            lineas_itemA['article_code']   = str(lineas_itemA['article_code'])
            codigos   = [str(lineas_itemA['article_code'])]
            alternatives = json.loads(lineas_itemA['alternative'])
            if len(alternatives) > 0:
                for altArtA in alternatives:
                    codigos += [str(altArtA['code'])]
            lineas_itemA['codigos_erp_arr'] = codigos
            lineas_itemA['consiste_de_alternativos'] = []

    # 4. FROXA DB search for prices and stock in all alternative articles 

    for itemB in articulos_data:
        lineas_array = itemB['lineas']
        for lineas_itemB in lineas_array:
            for one_erp_code in lineas_itemB['codigos_erp_arr']:
                stock_price = get_me_stock_now(one_erp_code, oracle)
                lineas_itemB['consiste_de_alternativos'] += [stock_price]
            
    # 5. calculate the price of the alternative article consisting of substitate items 

    for itemC in articulos_data:
        lineas_array  = itemC['lineas'];
        for lineas_itemC in lineas_array:
            formula_top_ud   = 0
            unidades_stock   = 0
            suma_precios     = 0
            percentage       = lineas_itemC['percentage'] or 0
            i = 0
            for infoItemC in lineas_itemC['consiste_de_alternativos']:
                # case sara if there is stock without price we do nothing
                if float(infoItemC[0]['stock'] or 0) > 0 and float(infoItemC[0]['precio'] or 0) == 0:
                    continue
                # case I found I, art 41139, when there are 2 items one only has price and the other price and stock to 0
                if float(infoItemC[0]['stock'] or 0) == 0 and float(infoItemC[0]['precio'] or 0) == 0:
                    continue
                i += 1
                formula_top_ud += float(infoItemC[0]['stock'] or 0) * float(infoItemC[0]['precio'] or 0)
                unidades_stock += float(infoItemC[0]['stock'] or 0)
                suma_precios   += float(infoItemC[0]['precio'] or 0)
            
            if i == 0:
                i = 1
            if unidades_stock == 0:
                lineas_itemC['resumen_alternativos'] = {'precio_kg': suma_precios / i, 'stock_kg': unidades_stock, 'parte_proporcional': suma_precios / i / 100 * float(percentage or 0) }
            else:
                lineas_itemC['resumen_alternativos'] = {'precio_kg': formula_top_ud /  unidades_stock, 'stock_kg': unidades_stock, 'parte_proporcional':  (formula_top_ud / unidades_stock) / 100 * percentage }
           

    # 6. calculate price actuality of parent article PUEDE SER QUE NO HACE FALTA

    for itemJU in articulos_data:
        father_price = 0
        lineas_array  = itemJU['lineas']
        for lineas_itemJUI in lineas_array:
            resum_alternate = lineas_itemJUI['resumen_alternativos']
            father_price   += float(resum_alternate['parte_proporcional'])
         
        itemJU['precio_padre_act'] = father_price
        
    EXPEDIENTES_SIN_PRECIO_FINAL = []
    
    # 7. obtain range months 
    rango_meses = obtener_rangos_meses()
    for itemD in articulos_data:
        lineas_array  = itemD['lineas']
        for lineas_itemD in lineas_array:
            fechas_desde_hasta = []
            for rango in rango_meses:
                fechas_desde_hasta += [{'desde':rango[0], 'hasta':rango[1], 'info_suma_llegadas': 0, 'info_suma_consumo':0}]
            lineas_itemD['rango'] = fechas_desde_hasta
            
    # 8. I iterante the data ranges and search for 1. container arrivals
    LAST_CHANGE_VAL      = get_last_changed_value(oracle)
    for itemF in articulos_data:
        lineas_array  = itemF['lineas'];
        for lineas_itemF in lineas_array:
            arr_codigos_erp = lineas_itemF['codigos_erp_arr']
            iterations = 0

            for r_fechas in lineas_itemF['rango']:
                r_fechas['llegadas'] = pedidos_pendientes(oracle, arr_codigos_erp, r_fechas, EXPEDIENTES_SIN_PRECIO_FINAL, iterations, LAST_CHANGE_VAL)
                r_fechas['consumo']  = consumo_pasado(oracle, arr_codigos_erp, r_fechas)          
                iterations += 1
     

    # 9. STOCK AND PRICE
    for itemG in articulos_data:
        lineas_array  = itemG['lineas']
        for lineas_itemG in lineas_array:
            pecentage = float(lineas_itemG['percentage'] or 0)
            PRECIO    = float(lineas_itemG['resumen_alternativos']['precio_kg'] or 0)
            STOCK     = float(lineas_itemG['resumen_alternativos']['stock_kg'] or 0)
            
            for rango_fechasG in lineas_itemG['rango']:
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
                rango_fechasG['precio_percentage'] = PRECIO / 100 * pecentage


    # 10.
    today = datetime.today()
    mes_actual = (today.replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    mes_mas1   = ((today + relativedelta(months=1)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    mes_mas2   = ((today + relativedelta(months=2)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")
    mes_mas3   = ((today + relativedelta(months=3)).replace(day=1) + relativedelta(months=1, days=-1)).strftime("%Y-%m-%d")


    for itemQ in articulos_data:
        
        eEditable, created = ExcelLinesEditable.objects.get_or_create(article_code=itemQ['__article__erp'])
        eEditable.article_name = itemQ['__article__name']
        if float(eEditable.rendimiento or 0) == 0: 
            eEditable.rendimiento = 1
        eEditable.precio_padre_act = float(itemQ['precio_padre_act'] or 0)

        sum_editables = float(eEditable.precio_aceite or 0) + float(eEditable.precio_servicios or 0) + float(eEditable.aditivos or 0) + float(eEditable.mod or 0) + float(eEditable.embalajes or 0) + float(eEditable.amort_maq or 0) + float(eEditable.moi or 0)
        
        eEditable.precio_padre_mas_gastos = eEditable.precio_padre_act / eEditable.rendimiento + sum_editables
        itemQ['precio_padre_mas_gastos']  = eEditable.precio_padre_mas_gastos

        for rango in rango_meses:                                 
            lineas_array = itemQ['lineas']
            coste        = 0
            calculo      = ''
            for lineas_articulo_padre in lineas_array:
                array_rangos_en_cada_linea_padre = lineas_articulo_padre['rango']
                for obj_rango_desde_hasta in array_rangos_en_cada_linea_padre:
                    if rango[1] == obj_rango_desde_hasta['hasta']:
                        coste   += obj_rango_desde_hasta['precio_percentage']
                        calculo += str(obj_rango_desde_hasta['precio_percentage'])+', '

                    if rango[1] == mes_actual:
                        eEditable.inicio_coste_act      = coste
                        eEditable.precio_materia_prima  = eEditable.precio_padre_act / eEditable.rendimiento
                        eEditable.final_coste_act       = eEditable.inicio_coste_act / eEditable.rendimiento + sum_editables

                    if rango[1] == mes_mas1:
                        eEditable.inicio_coste_mas1     = coste
                        eEditable.final_coste_mas1      = eEditable.inicio_coste_mas1 / eEditable.rendimiento + sum_editables
                       
                    if rango[1] == mes_mas2:
                        eEditable.inicio_coste_mas2     = coste
                        eEditable.final_coste_mas2      = eEditable.inicio_coste_mas2 / eEditable.rendimiento + sum_editables
                       
                    if rango[1] == mes_mas3:
                        eEditable.inicio_coste_mas3     = coste
                        eEditable.final_coste_mas3      = eEditable.inicio_coste_mas3 / eEditable.rendimiento + sum_editables
                        

            itemQ['costes_fecha'] += [{'fecha_tope': rango[1], 'inicio_coste_act': coste, 'composicion_precio': calculo }]

        todayDay = date.today()
        tomorrow = todayDay + timedelta(days=1)
        # standart price, only recalculate the last day of the month, added calc precio_estandar_con_gastos
        if tomorrow.day == 1:
            eEditable.precio_estandar = (eEditable.precio_padre_act + eEditable.inicio_coste_mas1) / 2
            eEditable.precio_estandar_con_gastos = eEditable.precio_estandar / eEditable.rendimiento + sum_editables

        eEditable.save()   

    # 11. save en database
    for itemW in articulos_data:
        try:
            head = ArticleCostsHead.objects.get(id=itemW['id'])
            head.cost_date = json.dumps(itemW['costes_fecha'])
            now = datetime.now()
            head.updated_at = now.strftime('%Y-%m-%d %H:%M:%S')
            itemW['expediente_sin_precios'] = EXPEDIENTES_SIN_PRECIO_FINAL     
            head.save()
        except:
            # manejar el caso
            pass

    aviso_expediente_sin_precio(request, EXPEDIENTES_SIN_PRECIO_FINAL)
      
    if code and code.isdigit() and int(code) > 0:
        # ejecutado desde http://127.0.0.1:3000/dashboard/#detalle-articulo-costes?codigo=40244
        pass
    else:
        # ejecutado desde el boton de recalcular
        recalculate_equiv_with_contaner(request)
        embarcado_art_con_sin_cont(request)

    oracle.close()
    return articulos_data


