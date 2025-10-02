from froxa.utils.connectors.libra_connector import OracleConnector

# ordenes de fabricacion activas y seleccionadas en otras palabras que estan en el uso

def ofs_abiertas_function():
    sql = """SELECT o.ORDEN_DE_FABRICACION, 
                o.CODIGO_ARTICULO,
                (SELECT MIN(DESCRIP_COMERCIAL) FROM ARTICULOS WHERE CODIGO_ARTICULO = o.CODIGO_ARTICULO) AS NOMBRE_ARTICULO,
                o.CODIGO_PRESENTACION,
                o.CANTIDAD_A_FABRICAR,
                o.FECHA_INI_FABRI_PREVISTA,
                o.FECHA_ENTREGA_PREVISTA,
                o.SITUACION_OF,
                o.STATUS_FABRICACION
            FROM ORDENES_FABRICA_CAB o
            WHERE o.SITUACION_OF = 'A'
            ORDER BY o.ORDEN_DE_FABRICACION DESC"""
    oracle = OracleConnector()
    oracle.connect()
    res = oracle.consult(sql, None)
    oracle.close()
    return res