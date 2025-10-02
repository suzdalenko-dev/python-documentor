from datetime import date, timedelta


def get_containers_for_today(oracle):
    
    sql = """SELECT c.NUMERO_DOC_EXT,
                    c.NUMERO_DOC_INTERNO,
                    TO_CHAR(c.FECHA, 'YYYY-MM-DD') AS FECHA_SUPERVISION,
                    c.CODIGO_ALMACEN,
                    (select a.NOMBRE from ALMACENES a WHERE a.ALMACEN = c.CODIGO_ALMACEN) AS D_ALMACEN,
                    c.TIPO_PEDIDO_COM,
                    (SELECT t.DESCRIPCION
                       FROM TIPOS_PEDIDO_COM t
                      WHERE t.TIPO_PEDIDO = c.TIPO_PEDIDO_COM AND t.ORGANIZACION_COMPRAS = c.ORGANIZACION_COMPRAS) AS D_TIPO_PEDIDO_COM,
                    CODIGO_PROVEEDOR,
                    (SELECT prlv.nombre
                        FROM proveedores prlv
                        WHERE prlv.codigo_rapido = c.codigo_proveedor AND prlv.codigo_empresa = c.codigo_empresa) AS D_CODIGO_PROVEEDOR
            FROM ALBARAN_COMPRAS_C c
            WHERE c.CODIGO_EMPRESA = '001'
                AND c.ORGANIZACION_COMPRAS = '01'
                AND c.CENTRO_CONTABLE IN (
                    SELECT DISTINCT gru.CODIGO_CENTRO
                    FROM CENTROS_GRUPO_CCONT gru
                    WHERE gru.EMPRESA = c.CODIGO_EMPRESA AND gru.CODIGO_GRUPO = '01')
                AND EXISTS (
                    SELECT 1
                    FROM ALBARAN_COMPRAS_L li
                    WHERE li.NUMERO_DOC_INTERNO = c.NUMERO_DOC_INTERNO AND li.CODIGO_EMPRESA = c.CODIGO_EMPRESA)
                AND c.STATUS_ANULADO = 'N'
                AND c.CODIGO_ALMACEN = '98'
                AND c.FECHA >= TRUNC(SYSDATE) - 3
                AND c.FECHA <  TRUNC(SYSDATE) + 1       
            ORDER BY c.FECHA DESC
            """

    containers = oracle.consult(sql) or []
    return containers   