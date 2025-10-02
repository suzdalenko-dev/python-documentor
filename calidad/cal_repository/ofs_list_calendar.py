from froxa.utils.connectors.libra_connector import OracleConnector


def get_list_ofs_calendar_func(request):
    fromOF      = request.GET.get('from')
    toOF        = request.GET.get('to')

    sql = """SELECT o.ORDEN_DE_FABRICACION, 
                o.CODIGO_ARTICULO,
                (SELECT MIN(DESCRIP_COMERCIAL) FROM ARTICULOS WHERE CODIGO_ARTICULO = o.CODIGO_ARTICULO) AS NOMBRE_ARTICULO,
                o.CODIGO_PRESENTACION,
                o.CANTIDAD_A_FABRICAR,
                o.FECHA_INI_FABRI_PREVISTA,
                o.SITUACION_OF
            FROM ORDENES_FABRICA_CAB o
            WHERE o.FECHA_INI_FABRI_PREVISTA >= TO_DATE(:fromOF, 'YYYY-MM-DD') AND o.FECHA_INI_FABRI_PREVISTA <= TO_DATE(:toOF, 'YYYY-MM-DD')
        """
    oracle = OracleConnector()
    oracle.connect()
    res = oracle.consult(sql, {'fromOF':fromOF, 'toOF':toOF})
    oracle.close()
    return res
