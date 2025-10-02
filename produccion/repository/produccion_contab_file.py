from froxa.utils.connectors.libra_connector import OracleConnector


def produccion_vs_contabilidad(request):
    # /produccion/get/0/0/produccion_vs_contabilidad/?from=2025-09-01&to=2025-09-30
    fromPCCC = request.GET.get('from')
    toPCCC   = request.GET.get('to')

    data = []
    oracle = OracleConnector()
    oracle.connect()

    sql_conta = """SELECT  historico_movim_almacen.orden_de_fabricacion,
                    SUM(historico_movim_almacen.importe_coste) importe_coste
                    FROM ARTICULOS,HISTORICO_MOVIM_ALMACEN,CODIGOS_MOVIMIENTO,FAMILIAS,ALMACENES 
                    WHERE (ARTICULOS.CODIGO_EMPRESA=HISTORICO_MOVIM_ALMACEN.CODIGO_EMPRESA 
                        and ARTICULOS.CODIGO_ARTICULO = HISTORICO_MOVIM_ALMACEN.CODIGO_ARTICULO 
                        and HISTORICO_MOVIM_ALMACEN.CODIGO_EMPRESA = CODIGOS_MOVIMIENTO.CODIGO_EMPRESA 
                        and HISTORICO_MOVIM_ALMACEN.CODIGO_MOVIMIENTO = CODIGOS_MOVIMIENTO.CODIGO_MOVIMIENTO 
                        AND ARTICULOS.CODIGO_FAMILIA = FAMILIAS.CODIGO_FAMILIA 
                        AND ARTICULOS.CODIGO_EMPRESA = FAMILIAS.CODIGO_EMPRESA 
                        AND HISTORICO_MOVIM_ALMACEN.CODIGO_EMPRESA = ALMACENES.CODIGO_EMPRESA 
                        AND HISTORICO_MOVIM_ALMACEN.CODIGO_ALMACEN = ALMACENES.ALMACEN
                        AND familias.numero_tabla = '1' 
                        AND CODIGOS_MOVIMIENTO.CODIGO_MOVIMIENTO NOT IN ('MODCR','MODST','MODCE')) 
                        AND (articulos.codigo_empresa = '001') 
                        AND (historico_movim_almacen.codigo_empresa = '001') 
                        AND (codigos_movimiento.codigo_empresa = '001') 
                        AND (familias.codigo_empresa = '001') 
                        AND (almacenes.codigo_empresa = '001') 
                        AND historico_movim_almacen.fecha_valor BETWEEN TO_DATE(:fromPCCC, 'YYYY-MM-DD') AND TO_DATE(:toPCCC, 'YYYY-MM-DD') 
                        AND historico_movim_almacen.tipo_situacion != 'DEPC' 
                        AND historico_movim_almacen.tipo_movimiento IN ('20')  
                    GROUP BY  historico_movim_almacen.orden_de_fabricacion"""

    contabilidads = oracle.consult(sql_conta, {'fromPCCC':fromPCCC, 'toPCCC':toPCCC})


    sql_produccion = """SELECT  v_froxa_validacion_costes_of.orden_de_fabricacion,
                                v_froxa_validacion_costes_of.nombre_of,
                                v_froxa_validacion_costes_of.fecha_prod,
                                v_froxa_validacion_costes_of.fecha_cierre,
                                v_froxa_validacion_costes_of.kg_fabricados,
                                v_froxa_validacion_costes_of.status_of,
                                v_froxa_validacion_costes_of.coste_indirecto,
                                v_froxa_validacion_costes_of.coste_mano_obra,
                                (v_froxa_validacion_costes_of.coste_indirecto+v_froxa_validacion_costes_of.coste_mano_obra) TOTAL_COSTE_INDRECTO_AND_MANO_OBRA
                        FROM V_FROXA_VALIDACION_COSTES_OF  
                        WHERE v_froxa_validacion_costes_of.fecha_cierre BETWEEN TO_DATE(:fromPCCC, 'YYYY-MM-DD') AND TO_DATE(:toPCCC, 'YYYY-MM-DD')
                        ORDER BY v_froxa_validacion_costes_of.fecha_prod ASC
                        """

    produccion = oracle.consult(sql_produccion, {'fromPCCC':fromPCCC, 'toPCCC':toPCCC})

    for p in produccion:
        of_encontrada = False
        for c in contabilidads:
            if p['ORDEN_DE_FABRICACION'] == c['ORDEN_DE_FABRICACION']:
                p['OF_CONTA']  = c['ORDEN_DE_FABRICACION']
                p['IMP_CONTA'] = c['IMPORTE_COSTE']
                of_encontrada = True
        if of_encontrada == False:
            p['OF_CONTA']  = c['ORDEN_DE_FABRICACION']
            p['IMP_CONTA'] = 0
            p['NOMBRE_OF'] = 'Solo existe en producción'       
    


    for c in contabilidads:
        of_encontrada = False
        for p in produccion:
            if p['ORDEN_DE_FABRICACION'] == c['ORDEN_DE_FABRICACION']:
                of_encontrada = True
        if of_encontrada == False and abs(float(c['IMPORTE_COSTE'])) > 1:
            x = {'OF_CONTA': c['ORDEN_DE_FABRICACION'], 'IMP_CONTA': c['IMPORTE_COSTE'], 'ORDEN_DE_FABRICACION': c['ORDEN_DE_FABRICACION'], 'TOTAL_COSTE_INDRECTO_AND_MANO_OBRA': 0, 'NOMBRE_OF': 'Solo existe en contabilidad', 'KG_FABRICADOS': 0 }
            produccion += [x]


    oracle.close()
    return {'res': produccion}


# tensorFlow
# pythorh  mas sencilla