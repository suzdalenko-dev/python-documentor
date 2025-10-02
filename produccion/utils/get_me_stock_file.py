import copy
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

from produccion.repository.embarcado_con_sin_cont.articulos_file import dame_gasto_de_alguna_forma, precio_con_sin_contenedor, precio_con_sin_contenedor_sin_gastos
from produccion.utils.precio_con_gastos import consultar_precio_con_gastos

def get_last_changed_value(oracle):
    sql  = """SELECT EMPRESA, PERIODO, CAMBIO FROM FROXA_SEGUROS_CAMBIO WHERE 1=1 AND ROWNUM=1 ORDER BY PERIODO DESC"""
    lasst_val = oracle.consult(sql)
    if lasst_val and len(lasst_val) > 0:
        lasst_val = lasst_val[0].get('CAMBIO')
        return float(lasst_val)
    else:
        return 0
   


def get_me_stock_now(erp_code, oracle):
    sql = """SELECT V_CODIGO_ALMACEN,
            D_CODIGO_ALMACEN,
            V_TIPO_SITUACION,
            V_CANTIDAD_PRESENTACION,
            V_STOCK_UNIDAD2,
            V_PRESENTACION,
            CODIGO_ARTICULO
            FROM 
        (
            SELECT  s.* , 
                CANTIDAD_PRESENTACION V_CANTIDAD_PRESENTACION,
                CODIGO_ALMACEN V_CODIGO_ALMACEN,
                PRESENTACION V_PRESENTACION,
                STOCK_UNIDAD1 V_STOCK_UNIDAD1,
                STOCK_UNIDAD2 V_STOCK_UNIDAD2,
                TIPO_SITUACION V_TIPO_SITUACION 
            FROM 
                (
                    SELECT codigo_empresa, 
                    codigo_almacen,
                    (SELECT a.nombre FROM almacenes a WHERE a.almacen = s.codigo_almacen AND a.codigo_empresa = s.codigo_empresa) d_codigo_almacen, 
                    codigo_articulo, 
                    tipo_situacion, 
                    presentacion, 
                    SUM(cantidad_unidad1) stock_unidad1, 
                    SUM(NVL(cantidad_unidad2, 0)) stock_unidad2, 
                    SUM(NVL(cantidad_presentacion, 0)) cantidad_presentacion
                    FROM stocks_detallado s  
                    WHERE NOT EXISTS 
                        (SELECT 1
                        FROM almacenes_zonas az
                        WHERE az.codigo_empresa = s.codigo_empresa
                               AND az.codigo_almacen = s.codigo_almacen
                               AND az.codigo_zona = s.codigo_zona
                               AND az.es_zona_reserva_virtual = 'S') 
                        GROUP BY codigo_empresa, codigo_almacen, codigo_articulo, tipo_situacion, presentacion
                ) s 
        )  s WHERE (NVL(stock_unidad1, 0) != 0 OR NVL(stock_unidad2, 0) != 0) and CODIGO_ARTICULO=:erp_code order by codigo_almacen"""

    stockArticle = oracle.consult(sql, {"erp_code": erp_code})
    stock_almcenes =  [{'erp': erp_code, 'almacenes': stockArticle, 'precio':0, 'stock':0}]
    stockItem  = 0
    if len(stockArticle) > 0:
        for almacen in stockArticle:
            cantidad_raw = almacen.get('V_CANTIDAD_PRESENTACION')
            if cantidad_raw not in [None, '', 'None']:
                stockItem += float(cantidad_raw)
    stock_almcenes[0]['stock']  = stockItem


    sql = """select PRECIO_MEDIO_PONDERADO from ARTICULOS_VALORACION where CODIGO_ARTICULO = :erp_code AND CODIGO_DIVISA = 'EUR' AND CODIGO_ALMACEN = '00'"""
    precioArticle = oracle.consult(sql, {"erp_code": erp_code})
    precioItem = 0.0
    if precioArticle and len(precioArticle) > 0:
        precio_raw   = precioArticle[0].get('PRECIO_MEDIO_PONDERADO')
        if precio_raw not in [None, '', 'None']:
            precioItem = float(precio_raw)
        stock_almcenes[0]['precio'] = precioItem

    return stock_almcenes



################################################

def obtener_rangos_meses():
    rangos = []
    meses_en_adelante = 4
    hoy = datetime.today()
    mes_actual = hoy.month
    anio_actual = hoy.year

    for i in range(meses_en_adelante):
        mes = (mes_actual + i) % 12
        mes = 12 if mes == 0 else mes
        anio = anio_actual + ((mes_actual + i - 1) // 12)
        
        primera_fecha = datetime(anio, mes, 1)
        ultima_fecha = primera_fecha + relativedelta(months=1) - timedelta(days=1)
        
        rangos.append([
            primera_fecha.strftime("%Y-%m-%d"),
            ultima_fecha.strftime("%Y-%m-%d")
        ])

    return rangos

################################################

def obtener_rangos_meses7():
    rangos = []
    meses_en_adelante = 7
    hoy = datetime.today()
    mes_actual = hoy.month
    anio_actual = hoy.year

    for i in range(meses_en_adelante):
        mes = (mes_actual + i) % 12
        mes = 12 if mes == 0 else mes
        anio = anio_actual + ((mes_actual + i - 1) // 12)
        
        primera_fecha = datetime(anio, mes, 1)
        ultima_fecha = primera_fecha + relativedelta(months=1) - timedelta(days=1)
        
        rangos.append([
            primera_fecha.strftime("%Y-%m-%d"),
            ultima_fecha.strftime("%Y-%m-%d")
        ])

    return rangos


#######################################################



def consumo_produccion(oracle, arr_codigos_erp, r_fechas):
    pass




#######################################################
### here I first look for the orders and then I look for the containers
#######################################################

def pedidos_pendientes(oracle, arr_codigos_erp, r_fechas, expedientes_sin_precio, iterations, LAST_CHANGE_VAL):
    # desde pedidos
    llegadas_p_data = []


    for codigo_erp in arr_codigos_erp:
        sql_pp = """
            SELECT
              pc.numero_pedido AS NUMERO,
              pc.fecha_pedido AS FECHA_PREV_LLEGADA,
              pcl.codigo_articulo AS ARTICULO,
              pcl.descripcion AS descripcion_articulo,
              pcl.cantidad_presentacion AS CANTIDAD,
              pcl.unidades_entregadas,
              'PED' AS ENTIDAD,
               DECODE(
                 (SELECT a.unidad_precio_coste 
                  FROM articulos a 
                  WHERE a.codigo_articulo = pcl.codigo_articulo 
                    AND a.codigo_empresa = pcl.codigo_empresa),
                 1,
                   CASE 
                     WHEN pcl.unidades_pedidas = 0 THEN 0
                     ELSE pcl.importe_lin_neto / pcl.unidades_pedidas
                   END,
                 CASE 
                   WHEN NVL(pcl.unidades_pedidas2, 0) = 0 THEN 0
                   ELSE pcl.importe_lin_neto / pcl.unidades_pedidas2
                 END
               ) AS PRECIO_EUR
            FROM
              pedidos_compras pc
            JOIN
              pedidos_compras_lin pcl
              ON pc.numero_pedido = pcl.numero_pedido
              AND pc.serie_numeracion = pcl.serie_numeracion
              AND pc.organizacion_compras = pcl.organizacion_compras
              AND pc.codigo_empresa = pcl.codigo_empresa
            WHERE
                pc.fecha_pedido >= TO_DATE(:fechaDesde, 'YYYY-MM-DD') AND pc.fecha_pedido <= TO_DATE(:fechaHasta, 'YYYY-MM-DD') 
                AND pc.fecha_pedido >= TO_DATE(:fechaActual, 'YYYY-MM-DD')
                AND pc.codigo_empresa = '001'
                AND pc.status_cierre = 'E'
                AND pcl.codigo_articulo = :codigo_erp
                AND (pcl.unidades_entregadas = 0 OR pcl.unidades_entregadas IS NULL)
            ORDER BY pc.fecha_pedido ASC
        """

        if iterations == 0:                                                        # espero 22 dias al pedido Katerina 
            desde_dt = datetime.strptime(r_fechas['desde'], '%Y-%m-%d')
            fechaDesde = (desde_dt - timedelta(days=22)).strftime('%Y-%m-%d')
        else:
            fechaDesde = r_fechas['desde']
        
        fechaActual = (datetime.today() - timedelta(days=22)).strftime('%Y-%m-%d') # espero 22 dias al pedido Katerina

        res = oracle.consult(sql_pp, { 'fechaDesde': fechaDesde, 'fechaHasta': r_fechas['hasta'], 'codigo_erp': codigo_erp, 'fechaActual': fechaActual })

        if res:
            llegadas_p_data.extend(res)


    # desde expedientes !!! OJO SOLO CON CONTENEDOR FILTRAMOS LA ULTIMA HOJA DE SEGUIMIENTO
    for codigo_erp in arr_codigos_erp:
        sql_ei = """SELECT
                      ehs.FECHA_PREV_LLEGADA,
                      ehs.num_expediente AS NUM_EXPEDIENTE,
                      eae.articulo AS ARTICULO,
                      ei.valor_cambio,
                      eae.PRECIO,
                      (CASE WHEN ei.divisa = 'USD' THEN eae.precio * ei.valor_cambio ELSE eae.precio END) AS PRECIO_EUR_ORIGINAL,
                      :LAST_CHANGE_VAL AS CAMBIO_MES,
                      (CASE WHEN ei.divisa = 'USD' THEN eae.precio * :LAST_CHANGE_VAL ELSE eae.precio END) AS PRECIO_EUR_ORIGINAL_CAM_MES,
                      eae.cantidad as CANTIDAD,
                      ehs.fecha_llegada,
                      ehs.codigo_entrada,
                      ec.contenedor AS NUMERO,
                      ei.divisa,
                      ei.valor_cambio,
                      'EXP' AS ENTIDAD,
                      -2224 as PRECIO_EUR,
                      ehs.NUM_HOJA
                    FROM expedientes_hojas_seguim ehs
                    JOIN expedientes_articulos_embarque eae ON ehs.num_expediente = eae.num_expediente AND ehs.num_hoja = eae.num_hoja AND ehs.empresa = eae.empresa
                    JOIN expedientes_imp ei ON ei.codigo = eae.num_expediente AND ei.empresa = eae.empresa
                    JOIN expedientes_contenedores ec ON ec.num_expediente = eae.num_expediente AND ec.num_hoja = eae.num_hoja AND ec.empresa = eae.empresa
                    WHERE 
                        ehs.FECHA_PREV_LLEGADA >= TO_DATE(:fechaDesde, 'YYYY-MM-DD') AND ehs.FECHA_PREV_LLEGADA <= TO_DATE(:fechaHasta, 'YYYY-MM-DD') 
                        AND ehs.FECHA_PREV_LLEGADA >= TO_DATE(:fechaActual, 'YYYY-MM-DD')
                        AND eae.articulo = :codigo_erp
                        AND ehs.codigo_entrada IS NULL
                        AND (ec.contenedor IS NOT NULL AND ec.contenedor != 'CNT')
                        AND ehs.empresa = '001'
                    ORDER BY ehs.FECHA_PREV_LLEGADA ASC
        """

        if iterations == 0:                                                       # espero 66 dias al pedido Katerina
            desde_dt = datetime.strptime(r_fechas['desde'], '%Y-%m-%d')
            fechaDesde = (desde_dt - timedelta(days=66)).strftime('%Y-%m-%d')
        else:
            fechaDesde = r_fechas['desde']
        
        fechaActual = (datetime.today() - timedelta(days=66)).strftime('%Y-%m-%d') # espero 66 dias al pedido Katerina

        res = oracle.consult(sql_ei, { 'fechaDesde': fechaDesde, 'fechaHasta': r_fechas['hasta'], 'codigo_erp': codigo_erp, 'fechaActual': fechaActual, 'LAST_CHANGE_VAL':LAST_CHANGE_VAL})

        if res:
            for r in res:
                precio_llegada_sql_sin_gastos = precio_con_sin_contenedor_sin_gastos(oracle, r['NUM_EXPEDIENTE'], r['ARTICULO'])
                precio_llegada_sql_con_gastos = precio_con_sin_contenedor(oracle, r['NUM_EXPEDIENTE'], r['ARTICULO'])

                if precio_llegada_sql_sin_gastos and precio_llegada_sql_con_gastos:
                    PRECIO_SIN_GASTOS_EXCEL = precio_llegada_sql_sin_gastos[0].get('N9')
                    PRECIO_SIN_GASTOS_EXCEL = float(PRECIO_SIN_GASTOS_EXCEL) if PRECIO_SIN_GASTOS_EXCEL not in [None, 'None', ''] else 0

                    PRECIO_CON_GASTOS_EXCEL = precio_llegada_sql_con_gastos[0].get('N10')
                    PRECIO_CON_GASTOS_EXCEL = float(PRECIO_CON_GASTOS_EXCEL) if PRECIO_CON_GASTOS_EXCEL not in [None, 'None', ''] else 0
                    if PRECIO_SIN_GASTOS_EXCEL == 0 or PRECIO_CON_GASTOS_EXCEL == 0:
                        if r['NUM_EXPEDIENTE'] not in expedientes_sin_precio:
                            expedientes_sin_precio.append(r['NUM_EXPEDIENTE'])
                        # buscar el ultimo precio con gastos y sin gastos DE ALGUNA FORMA
                        gasto_de_alguna_forma = dame_gasto_de_alguna_forma(oracle, r['ARTICULO'])
                        if gasto_de_alguna_forma:
                            PRECIO_SIN_GASTOS_EXCEL = gasto_de_alguna_forma[0].get('N9')
                            PRECIO_SIN_GASTOS_EXCEL = float(PRECIO_SIN_GASTOS_EXCEL) if PRECIO_SIN_GASTOS_EXCEL not in [None, 'None', ''] else 0
                            PRECIO_CON_GASTOS_EXCEL = gasto_de_alguna_forma[0].get('N10')
                            PRECIO_CON_GASTOS_EXCEL = float(PRECIO_CON_GASTOS_EXCEL) if PRECIO_CON_GASTOS_EXCEL not in [None, 'None', ''] else 0
                            if PRECIO_SIN_GASTOS_EXCEL == 0 or PRECIO_CON_GASTOS_EXCEL == 0:
                                r['PRECIO_EUR'] = -1122
                            else:
                                r['PRECIO_SIN_GASTOS_EXCEL'] = PRECIO_SIN_GASTOS_EXCEL
                                r['PRECIO_CON_GASTOS_EXCEL'] = PRECIO_CON_GASTOS_EXCEL
                                r['GASTOS']                  = r['PRECIO_CON_GASTOS_EXCEL'] - r['PRECIO_SIN_GASTOS_EXCEL']
                                r['PRECIO_EUR'] = float(r['PRECIO_EUR_ORIGINAL_CAM_MES'] or - 4444) + r['GASTOS']
                    else:
                        r['PRECIO_SIN_GASTOS_EXCEL'] = PRECIO_SIN_GASTOS_EXCEL
                        r['PRECIO_CON_GASTOS_EXCEL'] = PRECIO_CON_GASTOS_EXCEL
                        r['GASTOS']                  = r['PRECIO_CON_GASTOS_EXCEL'] - r['PRECIO_SIN_GASTOS_EXCEL']
                        r['PRECIO_EUR'] = float(r['PRECIO_EUR_ORIGINAL_CAM_MES'] or - 4444) + r['GASTOS']
                else:
                    
                    r['PRECIO_EUR'] = -3333



        # iterare hojas de seguimiento y si existe una con el numero posterior pasare a esta
        exped_filtrados = []
        for expediente in res:
            sql_hoja_mayor = """SELECT ehs.NUM_HOJA 
                                FROM expedientes_hojas_seguim ehs
                                JOIN expedientes_imp ei ON ei.codigo = ehs.num_expediente AND ei.empresa = ehs.empresa
                                WHERE ehs.num_hoja > :numHoja AND ei.codigo = :numExpediente"""
                
            res_sql_mayor = oracle.consult(sql_hoja_mayor, { 'numHoja': expediente['NUM_HOJA'], 'numExpediente': expediente['NUM_EXPEDIENTE']})
            if(res_sql_mayor):
                pass
            else:
                exped_filtrados.append(expediente)
                

        
        if exped_filtrados:        
            llegadas_p_data.extend(exped_filtrados) 
           


    
    ids_in_use = []
    suzdalIcon = "*"
    for i in llegadas_p_data:
        currentId = str(i['NUMERO'])+str(i['ARTICULO'])
        if currentId in ids_in_use:
            i['NUMERO'] = str(i['NUMERO'])+" "+str(suzdalIcon)
            suzdalIcon += str("*")
        ids_in_use += [currentId]


    return llegadas_p_data


##########################################################
# consume in production and sales
##########################################################

def consumo_pasado(oracle, arr_codigos_erp, r_fechas):
    # Convert strings to datetime objects
    fechaDesde_dt = datetime.strptime(r_fechas['desde'], '%Y-%m-%d')
    fechaHasta_dt = datetime.strptime(r_fechas['hasta'], '%Y-%m-%d')

    # Restar 1 año
    fechaDesde_dt -= relativedelta(years=1)
    fechaHasta_dt -= relativedelta(years=1)

    # Restar 1 mes !!! cambiar aqui por 1 año
    # fechaDesde_dt -= relativedelta(months=1)
    # fechaHasta_dt -= relativedelta(months=1)

    # Formato correcto a STRING para SQL
    fechaDesde = fechaDesde_dt.strftime('%Y-%m-%d')
    fechaHasta = fechaHasta_dt.strftime('%Y-%m-%d')

    consumo_data = []

    for codigo_erp in arr_codigos_erp:
        # sql_of = """SELECT 
        #                 ofc.FECHA_ENTREGA_PREVISTA,
        #                 cofmc.ORDEN_DE_FABRICACION,
        #                 cofmc.CODIGO_ARTICULO_CONSUMIDO,
        #                 a.DESCRIP_COMERCIAL AS DESCRIP_CONSUMIDO,
        #                 a.unidad_codigo1 AS CODIGO_PRESENTACION,
        #                 TO_NUMBER(cofmc.CANTIDAD_UNIDAD1) AS CANTIDAD,
        #                 'OFS_CONSUMO' AS CONSUMO
        #             FROM 
        #                 COSTES_ORDENES_FAB_MAT_CTD cofmc
        #             JOIN 
        #                 ORDENES_FABRICA_CAB ofc ON ofc.ORDEN_DE_FABRICACION = cofmc.ORDEN_DE_FABRICACION
        #             JOIN 
        #                 articulos a ON a.codigo_articulo = cofmc.CODIGO_ARTICULO_CONSUMIDO
        #             WHERE 
        #                 ofc.FECHA_ENTREGA_PREVISTA >= TO_DATE(:fechaDesde, 'YYYY-MM-DD') 
        #                 AND ofc.FECHA_ENTREGA_PREVISTA <= TO_DATE(:fechaHasta, 'YYYY-MM-DD')
        #                 AND codigo_articulo_consumido = :codigo_erp
        #                 AND TO_NUMBER(cofmc.CANTIDAD_UNIDAD1) != 0
        #             ORDER BY ofc.FECHA_ENTREGA_PREVISTA ASC
        #                 
        # """
        sql_of = """SELECT 
                        ofc.FECHA_ENTREGA_PREVISTA,
                        om.ORDEN_DE_FABRICACION,
                        om.CODIGO_COMPONENTE AS CODIGO_ARTICULO_CONSUMIDO,
                        a.UNIDAD_CODIGO1     AS CODIGO_PRESENTACION,
                        SUM(NVL(om.CANT_REAL_CONSUMO_UNIDAD1, 0)) AS CANTIDAD,
                        'OFS_CONSUMO'        AS CONSUMO
                    FROM 
                        OF_MATERIALES_UTILIZADOS om
                    JOIN 
                        ORDENES_FABRICA_CAB ofc 
                            ON ofc.ORDEN_DE_FABRICACION = om.ORDEN_DE_FABRICACION
                    JOIN 
                        ARTICULOS a 
                            ON a.CODIGO_ARTICULO = om.CODIGO_COMPONENTE
                    WHERE 
                        ofc.FECHA_ENTREGA_PREVISTA >= TO_DATE(:fechaDesde, 'YYYY-MM-DD') 
                        AND ofc.FECHA_ENTREGA_PREVISTA <= TO_DATE(:fechaHasta, 'YYYY-MM-DD')
                        AND om.CODIGO_COMPONENTE = :codigo_erp
                    GROUP BY
                        ofc.FECHA_ENTREGA_PREVISTA,
                        om.ORDEN_DE_FABRICACION,
                        om.CODIGO_COMPONENTE,
                        a.UNIDAD_CODIGO1
                    HAVING 
                        SUM(NVL(om.CANT_REAL_CONSUMO_UNIDAD1, 0)) <> 0
                    ORDER BY 
                        ofc.FECHA_ENTREGA_PREVISTA ASC"""

        res = oracle.consult(sql_of, { 'codigo_erp': codigo_erp, 'fechaDesde': fechaDesde, 'fechaHasta': fechaHasta })
        if res:
            consumo_data.extend(res)


    for codigo_erp in arr_codigos_erp:
        sql_pv = """SELECT
                        c.fecha_pedido AS fecha_venta,
                        l.articulo AS codigo_articulo,
                        TO_NUMBER(l.uni_seralm) AS CANTIDAD,
                        'P_VENTA' AS CONSUMO,
                        c.cliente
                    FROM
                        albaran_ventas_lin l
                    JOIN
                        albaran_ventas c ON l.numero_albaran = c.numero_albaran AND l.numero_serie = c.numero_serie AND l.ejercicio = c.ejercicio AND l.organizacion_comercial = c.organizacion_comercial AND l.empresa = c.empresa
                    JOIN
                        articulos a ON a.codigo_articulo = l.articulo
                    WHERE
                        l.empresa = '001'
                        AND NVL(l.linea_anulada, 'N') = 'N'
                        AND l.articulo = :codigo_erp
                        AND c.fecha_pedido BETWEEN TO_DATE(:fechaDesde, 'YYYY-MM-DD') AND TO_DATE(:fechaHasta, 'YYYY-MM-DD')
                        AND TO_NUMBER(l.uni_seralm) != 0
                        AND c.cliente < '999900'
                    ORDER BY
                        c.fecha_pedido DESC
        """
        res = oracle.consult(sql_pv, { 'codigo_erp': codigo_erp, 'fechaDesde': fechaDesde, 'fechaHasta': fechaHasta })
        if res:
            consumo_data.extend(res)

    return consumo_data


###################################################
# fechas y dias mes restantes
###################################################


def verificar_mes(fecha_str):
    """
    Verifica si la fecha (en string "YYYY-MM-DD") está en el mes y año actual.
    :param fecha_str: str
    :return: "mes actual" o "mes no actual"
    """
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    ahora = datetime.now().date()
    return "mes actual" if fecha.month == ahora.month and fecha.year == ahora.year else "mes no actual"

def obtener_dias_restantes_del_mes():
    """
    Retorna el número de días restantes en el mes actual (incluyendo hoy).
    :return: int
    """
    hoy = datetime.now().date()
    ultimo_dia = calendar.monthrange(hoy.year, hoy.month)[1]
    return ultimo_dia - hoy.day + 1

###################################################

def obtener_rangos_meses12():
    rangos = []
    meses_en_adelante = 12
    hoy = datetime.today()
    mes_actual = hoy.month
    anio_actual = hoy.year

    for i in range(meses_en_adelante):
        mes = (mes_actual + i) % 12
        mes = 12 if mes == 0 else mes
        anio = anio_actual + ((mes_actual + i - 1) // 12)
        
        primera_fecha = datetime(anio, mes, 1)
        ultima_fecha = primera_fecha + relativedelta(months=1) - timedelta(days=1)
        
        rangos.append([
            primera_fecha.strftime("%Y-%m-%d"),
            ultima_fecha.strftime("%Y-%m-%d")
        ])

    return rangos

