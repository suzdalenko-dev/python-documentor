from froxa.utils.connectors.libra_connector import OracleConnector


def evaluacion_proveedor(request):
    fromEP = request.GET.get('from') or '2025-01-01'
    toEP   = request.GET.get('to')   or '2995-02-27'

    oracle = OracleConnector()
    oracle.connect()

    sql = """SELECT PI.FECHA_ENTRADA FECHA_PARTE, PI.NUMERO_PARTE , PIX.VALOR_OBTENIDO, PI.CODIGO_PROVEEDOR , PIX.CODIGO_CARACT, PI.CODIGO_ARTICULO, PI.CANT_RECIBIDA, PI.CANT_ACEPTADA, PI.CODIGO_PRESENTACION,
             PI.LOTE_PROVEEDOR, PI.LOTE_INTERNO, PI.FECHA_VERIFICACION,
             (SELECT P.NOMBRE FROM PROVEEDORES P WHERE P.CODIGO_RAPIDO = PI.CODIGO_PROVEEDOR) D_PROVEEDOR,
             (SELECT A.DESCRIP_COMERCIAL FROM ARTICULOS A WHERE A.CODIGO_ARTICULO = PI.CODIGO_ARTICULO) D_ARTICULO
            FROM CA_PARTES_INSPECCION pi
            JOIN CA_PARTES_INSPECCION_ESP PIX ON PI.NUMERO_PARTE = PIX.NUMERO_PARTE
            WHERE 
             TO_CHAR(PI.FECHA_ENTRADA, 'YYYY-MM-DD') >= :fromEP
             AND TO_CHAR(PI.FECHA_ENTRADA, 'YYYY-MM-DD') <= :toEP
             AND PI.ORDEN_FABRICACION IS NULL
             AND PIX.VALOR_OBTENIDO IS NOT NULL
             AND PI.CODIGO_PROVEEDOR IS NOT NULL
             AND PIX.CODIGO_CARACT = 'E'
             AND PIX.CODIGO_PAUTA = 'D1B'
             ORDER BY PI.numero_parte DESC"""
    
    res = oracle.consult(sql, {'fromEP': fromEP, 'toEP': toEP})

    code_suppliers     = []
    material_suppliers = []

    for r in res:
        if r['CODIGO_PROVEEDOR'] not in code_suppliers:
            code_suppliers += [r['CODIGO_PROVEEDOR']]
            material_suppliers += [{'code': r['CODIGO_PROVEEDOR'], 'name': r['D_PROVEEDOR'], 'use_supplier': 0, 'score': 0, 'final_valuation': 0}]


    for r1 in res:
        for ms in material_suppliers:
            if r1['CODIGO_PROVEEDOR'] == ms['code']:
                ms['use_supplier'] += 1
                ms['score'] += float(r1['VALOR_OBTENIDO']) or 0
        
    for ms1 in material_suppliers:
        ms1['final_valuation'] = ms1['score'] / ms1['use_supplier']

    oracle.close()
    return {'material_suppliers': material_suppliers, 'all': res, }