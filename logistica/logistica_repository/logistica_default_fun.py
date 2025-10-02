import json
import threading
from froxa.utils.connectors.erp_old_connector import MySQLConn
from froxa.utils.connectors.libra_connector import OracleConnector
from logistica.models import OrderListBelinLoads
from django.db import connection


def get_and_refresh_gema_routes(request):
    cursor = connection.cursor()
    cursor.execute("""SELECT DISTINCT load_id,
                        MAX(load_date) AS load_date,
                        MAX(load_week) AS load_week,
                        SUM(palets)    AS palets
                    FROM logistica_orderlistbelinloads 
                    GROUP BY load_id
                    ORDER BY load_date DESC, load_id DESC
                    LIMIT 22""")
    rows    = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    belin_routes = [dict(zip(columns, row)) for row in rows]
    
    for routeA in belin_routes:
        sql = """SELECT l.truck_id,
                    MIN(l.truck_name) AS truck_name, 
                    SUM(l.palets) AS palets,
                    (BOOL_AND(COALESCE(l.clicked, 0) = 1))::int AS clicked
                FROM logistica_orderlistbelinloads l
                WHERE l.load_id = %s AND l.truck_id > 0
                GROUP BY l.truck_id
                ORDER BY l.truck_id ASC"""
        cursor.execute(sql, [routeA['load_id']])
        travel_list = cursor.fetchall()
        columns = [col[0] for col in cursor.description]
        travel_list = [dict(zip(columns, row)) for row in travel_list]
        routeA['travel_names'] = travel_list

    for routeB in belin_routes:
        for travelA in routeB['travel_names']:
            sql1 = """SELECT DISTINCT client_id, input_palets FROM logistica_orderlistbelinloads WHERE load_id = %s AND truck_id= %s"""
            cursor.execute(sql1, [routeB['load_id'], travelA['truck_id']])
            client_ids =cursor.fetchall()
            columns = [col[0] for col in cursor.description]
            client_ids = [dict(zip(columns, row)) for row in client_ids]
            sum_input_pal = 0
            for cl in client_ids:
                sum_input_pal += cl['input_palets'] or 0 
            travelA['sum_input_pal'] = sum_input_pal
       
       
    threading.Thread(target=refresh_gema_table,  daemon=True).start()
    return belin_routes



def load_truck_details(request, load_id, truck_id):
    if truck_id == 0 or truck_id == "0":
        lines = OrderListBelinLoads.objects.filter(load_id=load_id).values('load_id', 'load_week', 'load_date', 'truck_id', 'truck_name', 'orden', 'client_id', 'client_name', 'palets', 'input_palets', 'clicked', 'articles', 'order_id', 'click_info').order_by('truck_id', '-orden')
    else:
        lines = OrderListBelinLoads.objects.filter(load_id=load_id, truck_id=truck_id).values('load_id', 'load_week', 'load_date', 'truck_id', 'truck_name', 'orden', 'client_id', 'client_name', 'palets', 'input_palets', 'clicked', 'articles', 'order_id', 'click_info').order_by('-orden')
    
    lines = list(lines)

 
    all_data  = []
    truck_ids = []
    for l in lines:
        truck_id_X = str(l['truck_id'])+". "+str(l['truck_name'])
        if truck_id_X not in truck_ids:
            truck_ids += [truck_id_X]
            x = {'truck_id': l['truck_id'], 'truck_name': truck_id_X, 'lines': [], 'uniq_clients': [], 'client_lines': []}
            all_data += [x]
   
    
    for data in all_data:
        for l in lines:
            if l['truck_id'] == data['truck_id']:
                data['lines'] += [l]


    for data in all_data:
        unique_clients = []
        for inner_line in data['lines']:
            clientZ = str(inner_line['client_id'])+" "+inner_line['client_name']
            if clientZ not in unique_clients:
                unique_clients += [clientZ]
                data['client_lines'] += [{'cli': clientZ, 'lines': [], 'sum_pal': 0}]
        data['uniq_clients'] = unique_clients
       
        
    for dataQ in all_data:
        for client_line in dataQ['client_lines']:
            clientQ = client_line['cli']
            for dataW in all_data:
                for line_data in dataW['lines']:
                    cliente_w = str(line_data['client_id'])+" "+line_data['client_name']
                    if clientQ == cliente_w:
                        client_line['lines']   += [line_data]
                        client_line['sum_pal'] += line_data['palets']

    threading.Thread(target=refresh_gema_table,  daemon=True).start()

    return all_data



def order_clicked(request, load_id):
    order_id   = str(request.GET.get('order_id'))
    article_id = str(request.GET.get('article_id'))

    line = OrderListBelinLoads.objects.filter(load_id=load_id, order_id=order_id).first()

    article_number = json.loads(line.articles) or []
    article_number = len(article_number)

    test_clicked_info   = str(line.click_info).strip()
    if test_clicked_info in ['None', '', []] or len(test_clicked_info) <= 4:
        clicked_info = []
    else:
        clicked_info = json.loads(line.click_info) or []

    ARTICLE_EXIST = False
    for info in clicked_info:
        if info['code'] == article_id:
            ARTICLE_EXIST = True
            if info['value'] != 1:
                info['value'] = 1
            elif info['value'] == 1:
                info['value'] = 0
            break

    if ARTICLE_EXIST == False:
        clicked_info += [{'code':article_id, 'value': 1}]

    line.click_info = json.dumps(clicked_info)

    num_click = 0
    for info in clicked_info:
        if info['value'] == 1:
            num_click += 1

    if num_click == article_number:
        line.clicked = 1
    else:
        line.clicked = 0 

    line.save()

    return {'load_id': load_id, 'order_id': order_id, 'article_number':article_number, 'click_info':line.click_info, 'clicked': line.clicked, 'clicked_info': clicked_info}



def change_palets(request, load_id, truck_id):
    client_id = request.GET.get('client_id')
    num_pal   = request.GET.get('num_pal')

    lines = OrderListBelinLoads.objects.filter(load_id=load_id,truck_id=truck_id,client_id=client_id)



    for line in lines:
        line.input_palets = num_pal
        line.save()

    return {'load_id':load_id, 'truck_id':truck_id, 'client_id':client_id,  'num_pal': num_pal}





def refresh_gema_table():
    # palets guidance for travel
    # paltes input for client !!
    
    conn = MySQLConn()
    conn.connect()
    sql = """SELECT r.id, l.__camion, l.__orden, r.__fecha, r.__semana, l.__pedido__id,  l.__nombre__camion, l.__cliente__id, l.__cliente__descripcion, l.__totalpaletas, l.__excel__city, l.__excel__direccion
            FROM (
                SELECT id, __fecha, __semana
                FROM recogida
                ORDER BY id DESC
                LIMIT 22
            ) r
            JOIN lineaentrega l ON l.__recogida__id = r.id
            WHERE l.__camion > 0
            ORDER BY r.id DESC, l.__camion ASC, l.__orden DESC
        """
    belin_routes = conn.consult(sql)
    belin_routes = list(belin_routes)

    oracle = OracleConnector()
    oracle.connect()

    ORDERS_IN_USE = []

    for orden in belin_routes:
        pedido_id = str(orden['__pedido__id']).strip()
        parts = pedido_id.split("-")

        if len(parts) == 3:
            year, serie, number_code = parts
            sqlDetail = """SELECT 
                            avl.ARTICULO, 
                            MAX(avl.DESCRIPCION_ARTICULO) AS DESCRIPCION_ARTICULO, 
                            SUM(avl.UNIDADES_SERVIDAS) AS UNIDADES_SERVIDAS, 
                            SUM(avl.UNI_SERALM) AS UNI_SERALM, 
                            avl.ID_PEDIDO,
                            MAX(avl.ID_ALBARAN) AS ID_ALBARAN,
                            MAX(avl.PRESENTACION_PEDIDO) AS PRESENTACION_PEDIDO,
                            SUM(
                                CASE  
                                    WHEN avl.PRESENTACION_PEDIDO = 'UND' THEN 
                                        ROUND(
                                            avl.UNIDADES_SERVIDAS / 
                                            (SELECT MAX(CONVERS_U_DIS) 
                                             FROM CADENA_LOGISTICA 
                                             WHERE CODIGO_ARTICULO = avl.ARTICULO), 2)
                                    WHEN avl.PRESENTACION_PEDIDO = 'KG' THEN
                                        ROUND(
                                                avl.UNIDADES_SERVIDAS /
                                                ( NVL(NULLIF(
                                                      (SELECT MAX(CONVERS_U_SOB)
                                                       FROM CADENA_LOGISTICA
                                                       WHERE CODIGO_ARTICULO = avl.ARTICULO), 0), 1)
                                                  * 
                                                  NVL(NULLIF(
                                                      (SELECT MAX(CONVERS_U_DIS)
                                                       FROM CADENA_LOGISTICA
                                                       WHERE CODIGO_ARTICULO = avl.ARTICULO), 0), 1)
                                                ), 2)
                                    ELSE avl.UNIDADES_SERVIDAS
                                END
                            ) AS CAJAS_CALCULADAS
                        FROM (
                            SELECT 
                                avl.ARTICULO, 
                                avl.DESCRIPCION_ARTICULO, 
                                avl.UNIDADES_SERVIDAS, 
                                avl.UNI_SERALM, 
                                avl.PRESENTACION_PEDIDO, 
                                avl.EJERCICIO_PEDIDO || '-' || avl.NUMERO_SERIE_PEDIDO || '-' || avl.NUMERO_PEDIDO AS ID_PEDIDO,
                                avl.EJERCICIO_PEDIDO || '-' || avl.NUMERO_SERIE || '-' || avl.NUMERO_ALBARAN AS ID_ALBARAN
                            FROM ALBARAN_VENTAS_LIN avl
                            WHERE avl.NUMERO_PEDIDO = :number_code
                              AND avl.NUMERO_SERIE_PEDIDO = :serie
                              AND avl.EJERCICIO_PEDIDO = :year
                        ) avl
                        GROUP BY avl.ID_PEDIDO, avl.ARTICULO
                        """
            rows_diario  = oracle.consult(sqlDetail, {'number_code':number_code, 'serie':serie, 'year':year}) or []
            if len(rows_diario) == 0:
                sqlDetail = """SELECT 
                                pvl.ARTICULO, 
                                MAX(pvl.DESCRIPCION_ARTICULO) AS DESCRIPCION_ARTICULO,
                                SUM(pvl.UNIDADES_SERVIDAS) AS UNIDADES_SERVIDAS, 
                                SUM(pvl.UNI_SERALM) AS UNI_SERALM, 
                                pvl.ID_PEDIDO,
                                MAX(pvl.ID_ALBARAN) AS ID_ALBARAN,
                                MAX(pvl.PRESENTACION_PEDIDO) AS PRESENTACION_PEDIDO,
                                SUM(
                                    CASE  
                                        WHEN pvl.PRESENTACION_PEDIDO = 'UND' THEN 
                                            ROUND(
                                                pvl.UNIDADES_SERVIDAS / 
                                                (SELECT MAX(CONVERS_U_DIS) 
                                                 FROM CADENA_LOGISTICA 
                                                 WHERE CODIGO_ARTICULO = pvl.ARTICULO), 2)
                                        WHEN pvl.PRESENTACION_PEDIDO = 'KG' THEN
                                            ROUND(
                                                pvl.UNIDADES_SERVIDAS /
                                                ( NVL(NULLIF(
                                                      (SELECT MAX(CONVERS_U_SOB)
                                                       FROM CADENA_LOGISTICA
                                                       WHERE CODIGO_ARTICULO = pvl.ARTICULO), 0), 1)
                                                  * 
                                                  NVL(NULLIF(
                                                      (SELECT MAX(CONVERS_U_DIS)
                                                       FROM CADENA_LOGISTICA
                                                       WHERE CODIGO_ARTICULO = pvl.ARTICULO), 0), 1)
                                                ), 2)
                                        ELSE pvl.UNIDADES_SERVIDAS
                                    END
                                ) AS CAJAS_CALCULADAS
                            FROM (
                                SELECT 
                                    ARTICULO, 
                                    DESCRIPCION_ARTICULO, 
                                    CANTIDAD_PEDIDA AS UNIDADES_SERVIDAS, 
                                    UNI_PEDALM AS UNI_SERALM,
                                    PRESENTACION_PEDIDO, 
                                    EJERCICIO || '-' || NUMERO_SERIE || '-' || NUMERO_PEDIDO AS ID_PEDIDO,
                                    ' ' AS ID_ALBARAN
                                FROM PEDIDOS_VENTAS_LIN
                                WHERE numero_serie = :serie
                                  AND NUMERO_PEDIDO = :number_code
                                  AND EJERCICIO = :year
                            ) pvl
                            GROUP BY pvl.ID_PEDIDO, pvl.ARTICULO
                            """
            rows_diario  = oracle.consult(sqlDetail, {'number_code':number_code, 'serie':serie, 'year':year}) or []

        orden['articles'] = rows_diario
       
        if orden['__pedido__id'] not in ORDERS_IN_USE:
            ORDERS_IN_USE += [orden['__pedido__id']]

        lineBelin, created         = OrderListBelinLoads.objects.get_or_create(order_id=orden['__pedido__id'], load_id=orden['id'])
        # lineBelin.load_id        = orden['id']
        lineBelin.load_date        = orden['__fecha']
        lineBelin.truck_id         = orden['__camion']
        lineBelin.truck_name       = orden['__nombre__camion']
        lineBelin.client_id        = orden['__cliente__id']
        lineBelin.client_name      = orden['__cliente__descripcion']+' ('+orden['__excel__city']+' '+ orden['__excel__direccion']+')'
        lineBelin.orden            = orden['__orden']
        lineBelin.palets           = orden['__totalpaletas']
        lineBelin.articles         = json.dumps(orden['articles'])
        lineBelin.load_week        = orden['__semana']

        
        lineBelin.save()



    # traer las devoluciones
    sql = """SELECT *
            FROM lineadevolucion
            ORDER BY id DESC
            LIMIT 111
        """
    all_returns  = conn.consult(sql)
    all_returns = list(all_returns)

    for devolucion in all_returns:

        if devolucion['id'] not in ORDERS_IN_USE:
            ORDERS_IN_USE += [devolucion['id']]

        lineBelin, created         = OrderListBelinLoads.objects.get_or_create(order_id=devolucion['id'])
        lineBelin.load_id          = devolucion['__recodiga__id']
        lineBelin.load_date        = ' '
        lineBelin.truck_id         = devolucion['__camion__id']
        lineBelin.truck_name       = devolucion['__nombre__camion']
        lineBelin.client_id        = 'DEVOLUCION '+ devolucion['__codigo__proveedor']
        lineBelin.client_name      = devolucion['__nombre__proveedor']
        lineBelin.orden            = 1111
        lineBelin.palets           = devolucion['__numero__palets']
        lineBelin.articles         = json.dumps([{'ARTICULO':devolucion['id'], 'DESCRIPCION_ARTICULO':devolucion['__comment'], 'UNIDADES_SERVIDAS': devolucion['__kg_value'], 'PRESENTACION_PEDIDO': 'KG', 'UNI_SERALM': devolucion['__kg_value']}])
        lineBelin.load_week        = ' '

        lineBelin.save()





    # comprobar que pedidos sobran y borrar los que estan en DB_FROXA y no estan el lineasEtrega
    cursor = connection.cursor()
    cursor.execute("""
            SELECT DISTINCT load_id
            FROM logistica_orderlistbelinloads lo
            ORDER BY load_id DESC
            LIMIT 22
        """)
    rows = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    ID_LOADS_DB_FROXA = [dict(zip(columns, row)) for row in rows]

    cursor = connection.cursor()
    for ID_LOAD in ID_LOADS_DB_FROXA:
        cursor.execute("""
            SELECT DISTINCT lo.order_id
            FROM logistica_orderlistbelinloads lo
            WHERE lo.load_id = %s
        """, [ID_LOAD['load_id']])

        rows2 = cursor.fetchall()
        columns2 = [col[0] for col in cursor.description]
        ID_LOAD['list_orders'] = [dict(zip(columns2, row)) for row in rows2]

    # borrado
    for LOAD_DATA in ID_LOADS_DB_FROXA:
        for ordenX in LOAD_DATA['list_orders']:
            # Delete orders that are only in DB_FROXA and are no longer in 7 server
            if ordenX['order_id'] not in ORDERS_IN_USE:
                OrderListBelinLoads.objects.filter(order_id=ordenX['order_id']).delete()
        
    

   

    conn.close()
    oracle.close()

    return all_returns

