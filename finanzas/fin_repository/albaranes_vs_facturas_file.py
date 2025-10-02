from froxa.utils.connectors.libra_connector import OracleConnector


def albaranes_vs_facturas(request):
    oracle = OracleConnector()
    oracle.connect()

    out = []
    date_from = request.GET.get('date_from')
    date_to   = request.GET.get('date_to')

    #date_from = '2025-08-28'
    #date_to   = '2025-08-28'

    # 1. buscamos albaranes del 98 entre fechas

    sql1 = """select  TO_CHAR(alc.FECHA, 'YYYY-MM-DD') FECHA, 
                    TO_CHAR(alc.FECHA, 'YYYYMM') SHORTDATE,
                    (select fsc.CAMBIO from froxa_seguros_cambio fsc where fsc.PERIODO = TO_CHAR(alc.FECHA, 'YYYYMM')) CAMBIOMES,
                    alc.NUMERO_DOC_INTERNO, 
                    alc.NUMERO_DOC_EXT,
                    alc.CODIGO_PROVEEDOR,
                    alc.CODIGO_ALMACEN,
                    (SELECT SUM(NVL(lin.importe_lin_neto_div, 0)) from albaran_compras_l lin where lin.NUMERO_DOC_INTERNO = alc.NUMERO_DOC_INTERNO) AS IMPORTE_LIN_NETO_DIV_USD,
                    (SELECT MAX(NVL(lin.cambio, 0))               from albaran_compras_l lin where lin.NUMERO_DOC_INTERNO = alc.NUMERO_DOC_INTERNO) AS CAMBIO,
                    (SELECT SUM(NVL(lin.importe_lin_neto, 0))     from albaran_compras_l lin where lin.NUMERO_DOC_INTERNO = alc.NUMERO_DOC_INTERNO) AS IMPORTE_LIN_NETO_EUR
            from ALBARAN_COMPRAS_C alc
            where alc.centro_contable = '01'
              and alc.organizacion_compras = '01'
              and alc.codigo_empresa = '001'
              and alc.codigo_almacen = '98'
              and TO_CHAR(alc.FECHA, 'YYYY-MM-DD') >= :date_from
              and TO_CHAR(alc.FECHA, 'YYYY-MM-DD') <= :date_to
              -- -- and alc.CODIGO_PROVEEDOR = '000365'               -- QUITAR ESTE PROVEEDOR YA !!!
            order by alc.FECHA DESC
    """
    res = oracle.consult(sql1, {'date_from':date_from, 'date_to': date_to})


    for r1 in res:
        out += [{'albaranes98': r1}]

    # return out

    """ 2. Buscamos a cada albaran del 98 su factura
           Solo dejo 1 factura diferente
    """

    for o2 in out:
        sql2 = """SELECT DISTINCT fl.NUMERO_FACTURA,
                    (SELECT TO_CHAR(fcc.FECHA_FACTURA, 'DD/MM/YYYY') FROM FACTURAS_COMPRAS_CAB fcc where fcc.numero_factura = fl.numero_factura) AS FECHA_FACTURA,
                    (SELECT NVL(fcc.LIQUIDO_FACTURA_DIV, 0) FROM FACTURAS_COMPRAS_CAB fcc where fcc.numero_factura = fl.numero_factura) AS LIQUIDO_FACTURA_DIV,
                    (SELECT NVL(fcc.VALOR_CAMBIO, 0)        FROM FACTURAS_COMPRAS_CAB fcc where fcc.numero_factura = fl.numero_factura) AS VALOR_CAMBIO,
                    (SELECT NVL(fcc.LIQUIDO_FACTURA, 0)     FROM FACTURAS_COMPRAS_CAB fcc where fcc.numero_factura = fl.numero_factura) AS LIQUIDO_FACTURA
                FROM facturas_compras_lin fl
                WHERE fl.num_albaran_int = :NUMERO_DOC_INTERNO
            """
        
        NUMERO_DOC_INTERNO = o2['albaranes98']['NUMERO_DOC_INTERNO']
        facturas = oracle.consult(sql2, {'NUMERO_DOC_INTERNO': NUMERO_DOC_INTERNO}) or []

        if len(facturas) > 0:
            o2['facturas_reales'] = facturas
        else:
            o2['facturas_reales'] = []

    # return out

    # 3. Buscar desde el numero de factura todo que puede tener facturado esta factura

    for o3 in out:
        datos_facturas = []
        for x in o3['facturas_reales']:
            sql3 = """select DISTINCT NUM_ALBARAN_INT from facturas_compras_lin where numero_factura = :numero_factura"""

            lo_que_se_factura = oracle.consult(sql3, {'numero_factura': x['NUMERO_FACTURA']}) or []
            datos_facturas.extend(lo_que_se_factura)

        o3['lo_que_se_factura'] = datos_facturas



    # 4. Aqui voy a buscar los datos de los albaranes en cuestion o del 98 (desde el que nace todo) o otros que meten a mano para arreglar cosas !!!

    for o4 in out:        
        albaranes_reales = []

        for factura_item in o4['lo_que_se_factura']:
            sql4 = """select alc.NUMERO_DOC_INTERNO,
                        TO_CHAR(alc.FECHA, 'YYYY-MM-DD') FECHA,
                        TO_CHAR(alc.FECHA, 'YYYYMM') SHORTDATE,
                        (select fsc.CAMBIO from froxa_seguros_cambio fsc where fsc.PERIODO = TO_CHAR(alc.FECHA, 'YYYYMM')) CAMBIOMES,
                        alc.NUMERO_DOC_EXT,
                        alc.CODIGO_PROVEEDOR,
                        alc.CODIGO_ALMACEN,
                    (SELECT SUM(NVL(lin.importe_lin_neto_div, 0)) from albaran_compras_l lin where lin.NUMERO_DOC_INTERNO = alc.NUMERO_DOC_INTERNO) AS IMPORTE_LIN_NETO_DIV_USD,
                    (SELECT MAX(NVL(lin.cambio, 0))               from albaran_compras_l lin where lin.NUMERO_DOC_INTERNO = alc.NUMERO_DOC_INTERNO) AS CAMBIO,
                    (SELECT SUM(NVL(lin.importe_lin_neto, 0))     from albaran_compras_l lin where lin.NUMERO_DOC_INTERNO = alc.NUMERO_DOC_INTERNO) AS IMPORTE_LIN_NETO_EUR
                    from ALBARAN_COMPRAS_C alc
                    where alc.numero_doc_interno = :NUM_ALBARAN_INT"""

            albs = oracle.consult(sql4, {'NUM_ALBARAN_INT': factura_item['NUM_ALBARAN_INT']}) or []
            
            albaranes_reales.extend(albs)


        o4['albaranes_reales'] = albaranes_reales

    oracle.close()


    # 5. Si no tengo albaranes reales los cogere desde albaranes 98

    for o5 in out:
        if len(o5['albaranes_reales']) == 0:
            o5['albaranes_reales']  += [o5['albaranes98']]


    # 6. no mostrar las facturas que se repiten ya que pueden estar en diferentes albaranes "FA02-0003073"
    data_sin_facturas_repetidas = []
    unique_facturas = []
    for o6 in out:
        if len(o6['facturas_reales']) > 0:
            for factX in o6['facturas_reales']:
                if factX['NUMERO_FACTURA'] not in unique_facturas:
                    unique_facturas += [factX['NUMERO_FACTURA']]
                    data_sin_facturas_repetidas += [o6]
        else:
            data_sin_facturas_repetidas += [o6]

    return {'data': data_sin_facturas_repetidas}