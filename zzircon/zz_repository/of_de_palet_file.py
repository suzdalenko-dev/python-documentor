from froxa.utils.connectors.libra_connector import OracleConnector

# entiendo que no dice que tal paleta se ha llevado(usado) para tal orden de fabricacion
# lo mismo que el informe "OF de PALET" en modulo web
# 0731L ENVIO M.PRIMA>PRODUCCION 07 TRASPASOS ENTRE ALMACENES
# almacen salida 00 CARTES (10 CAMARA PALET) => almacen entrada 90 PRODUCCION FABRICA (00 RECEPCION DE MATERIAL)

def of_de_palet_function(pal_code):
    # of de palet 000000096 000011805
    sql = """SELECT numero_palet, 
                H1.orden_de_fabricacion,
                O.CODIGO_ARTICULO,
                (SELECT DESCRIP_COMERCIAL FROM ARTICULOS A WHERE A.Codigo_Articulo = O.CODIGO_ARTICULO) AS DESCRIP_COMERCIAL, 
                fecha_movim
            FROM HISTORICO_MOVIM_ALMACEN h1, ORDENES_FABRICA_CAB O
            WHERE numero_palet = :pal_code 
              AND  TIPO_MOVIMIENTO = '07'
              AND CANTIDAD_UNIDAD1 > 0
              AND CODIGO_ALMACEN = '90'
              AND codigo_movimiento = '0731L'
              AND H1.codigo_empresa = '001'
              AND H1.ORDEN_DE_FABRICACION = O.ORDEN_DE_FABRICACION
              AND fecha_movim = (
                  SELECT MAX(h2.fecha_movim)
                  FROM HISTORICO_MOVIM_ALMACEN h2
                  WHERE h2.TIPO_MOVIMIENTO = '07'
                    AND h2.CANTIDAD_UNIDAD1 > 0
                    AND h2.CODIGO_ALMACEN = '90'
                    AND h2.codigo_movimiento = '0731L'
                    AND h2.codigo_empresa = '001'
                    AND h2.numero_palet = h1.numero_palet
              )"""
    oracle = OracleConnector()
    oracle.connect()
    res = oracle.consult(sql, {"pal_code": pal_code})
    oracle.close()
    return res