def get_valor_cambio(request, oracle):
    sql = """SELECT GC1 EMPRESA, D_GC1 NOMBRE, GC2 FECHA, GN1 VALOR_CAMBIO
            FROM (
                SELECT EMPRESA GC1,
                       DECODE(froxa_seguros_cambio.empresa,NULL,NULL,
                              (SELECT lvemp.nombre 
                                 FROM empresas_conta lvemp 
                                WHERE lvemp.codigo = froxa_seguros_cambio.empresa)) D_GC1,
                       PERIODO GC2,
                       CAMBIO GN1
                FROM FROXA_SEGUROS_CAMBIO
                ORDER BY PERIODO DESC
            )
            WHERE ROWNUM = 1"""
    res = oracle.consult(sql) or []
    if res and len(res) > 0:
        res = float(res[0]['VALOR_CAMBIO']) or -22
    else:
        res = -11
    return res


def get_expediente_almacen_98(request, oracle, valor_cambio):
    from_day = request.GET.get('from')
    to_day   = request.GET.get('to')

    sql = """SELECT c.NUMERO_DOC_EXT,
                    c.NUMERO_DOC_INTERNO,
                    TO_CHAR(c.FECHA, 'YYYY-MM-DD') AS FECHA_SUPERVISION,
                    c.CODIGO_ALMACEN,
                    (select a.NOMBRE from ALMACENES a WHERE a.ALMACEN = c.CODIGO_ALMACEN) AS D_ALMACEN,
                    c.TIPO_PEDIDO_COM,
                    (SELECT t.DESCRIPCION
                       FROM TIPOS_PEDIDO_COM t
                      WHERE t.TIPO_PEDIDO = c.TIPO_PEDIDO_COM AND t.ORGANIZACION_COMPRAS = c.ORGANIZACION_COMPRAS) AS D_TIPO_PEDIDO_COM,
                    c.CODIGO_PROVEEDOR,
                    (SELECT prlv.nombre
                        FROM proveedores prlv
                        WHERE prlv.codigo_rapido = c.codigo_proveedor AND prlv.codigo_empresa = c.codigo_empresa) AS D_CODIGO_PROVEEDOR,
                    (SELECT SUM(li.IMPORTE_LIN_NETO)                                                                                       -- li.IMPORTE_LIN_NETO_DIV, 
                        FROM ALBARAN_COMPRAS_L li
                        WHERE li.NUMERO_DOC_INTERNO = c.NUMERO_DOC_INTERNO AND li.CODIGO_EMPRESA = c.CODIGO_EMPRESA) AS IMPORTE_TOTAL_EUR
                    -- (SELECT MIN(li.DIVISA)
                    --     FROM ALBARAN_COMPRAS_L li
                    --     WHERE li.NUMERO_DOC_INTERNO = c.NUMERO_DOC_INTERNO AND li.CODIGO_EMPRESA = c.CODIGO_EMPRESA) AS DIVISA
            FROM ALBARAN_COMPRAS_C c
            WHERE 
                c.CODIGO_EMPRESA = '001'
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
                AND TO_CHAR(c.FECHA, 'YYYY-MM-DD') >= :from_day
                AND TO_CHAR(c.FECHA, 'YYYY-MM-DD') <= :to_day
                
                -- -- --AND c.NUMERO_DOC_EXT = '266/3'
          
            ORDER BY c.FECHA DESC
            """
    res = oracle.consult(sql, {'from_day':from_day, 'to_day': to_day}) or []

    ### for r in res:
    ###     r['VALOR_CAMBIO'] = valor_cambio
    ###     if r['DIVISA'] != 'EUR':
    ###         r['IMPORTE_TOTAL_EUR'] = float(r['IMPORTE_TOTAL_ORIGINAL']) * valor_cambio
    ###     else:
    ###         r['IMPORTE_TOTAL_EUR'] = float(r['IMPORTE_TOTAL_ORIGINAL'])

    return res
    


def get_textos(request, oracle, num_doc_ext, valor_cambio):
    sql = """SELECT 
                    acc.NUMERO_DOC_EXT,
                    acc.NUMERO_DOC_INTERNO,
                    TO_CHAR(acc.FECHA, 'YYYY-MM-DD') AS FECHA_SUPERVISION,
                    acc.CODIGO_ALMACEN,
                    (select a.NOMBRE from ALMACENES a WHERE a.ALMACEN = acc.CODIGO_ALMACEN) AS D_ALMACEN,
                    acc.TIPO_PEDIDO_COM,
                    (SELECT t.DESCRIPCION
                       FROM TIPOS_PEDIDO_COM t
                      WHERE t.TIPO_PEDIDO = acc.TIPO_PEDIDO_COM AND t.ORGANIZACION_COMPRAS = acc.ORGANIZACION_COMPRAS) AS D_TIPO_PEDIDO_COM,
                    acc.CODIGO_PROVEEDOR,
                    (SELECT prlv.nombre
                        FROM proveedores prlv
                        WHERE prlv.codigo_rapido = acc.codigo_proveedor AND prlv.codigo_empresa = acc.codigo_empresa) AS D_CODIGO_PROVEEDOR,
                    (SELECT SUM(lai.IMPORTE_LIN_NETO)
                        FROM ALBARAN_COMPRAS_L lai
                        WHERE lai.NUMERO_DOC_INTERNO = acc.NUMERO_DOC_INTERNO AND lai.CODIGO_EMPRESA = acc.CODIGO_EMPRESA) AS IMPORTE_TOTAL_EUR
                    -- (SELECT MIN(lai.DIVISA)
                    --     FROM ALBARAN_COMPRAS_L lai
                    --     WHERE lai.NUMERO_DOC_INTERNO = acc.NUMERO_DOC_INTERNO AND lai.CODIGO_EMPRESA = acc.CODIGO_EMPRESA) AS DIVISA
                FROM ALBARAN_COMPRAS_C acc
                WHERE acc.CODIGO_EMPRESA = '001'
                    AND acc.ORGANIZACION_COMPRAS = '01'
                    AND acc.CENTRO_CONTABLE IN (
                            SELECT DISTINCT gru.CODIGO_CENTRO
                            FROM CENTROS_GRUPO_CCONT gru
                            WHERE gru.EMPRESA = acc.CODIGO_EMPRESA AND gru.CODIGO_GRUPO = '01')
                    AND EXISTS (
                            SELECT 1
                            FROM ALBARAN_COMPRAS_L li, ARTICULOS lia
                            WHERE li.NUMERO_DOC_INTERNO = acc.NUMERO_DOC_INTERNO AND li.CODIGO_EMPRESA = acc.CODIGO_EMPRESA AND lia.CODIGO_EMPRESA = li.CODIGO_EMPRESA AND lia.CODIGO_ARTICULO = li.CODIGO_ARTICULO)
                    AND acc.STATUS_ANULADO = 'N'
                    AND acc.NUMERO_DOC_EXT = :num_doc_ext
                    AND acc.CODIGO_ALMACEN = '25'
                ORDER BY acc.FECHA DESC
            """
    textos = oracle.consult(sql, {'num_doc_ext': num_doc_ext}) or []
    ### for r in textos:
    ###     if r['DIVISA'] != 'EUR':
    ###         r['IMPORTE_TOTAL_EUR'] = float(r['IMPORTE_TOTAL_ORIGINAL']) * valor_cambio
    ###     else:
    ###         r['IMPORTE_TOTAL_EUR'] = float(r['IMPORTE_TOTAL_ORIGINAL'])
    return textos


def get_stock(request, oracle, num_doc_ext, valor_cambio):
    sql = """SELECT 
                    acc.NUMERO_DOC_EXT,
                    acc.NUMERO_DOC_INTERNO,
                    TO_CHAR(acc.FECHA, 'YYYY-MM-DD') AS FECHA_SUPERVISION,
                    acc.CODIGO_ALMACEN,
                    (select a.NOMBRE from ALMACENES a WHERE a.ALMACEN = acc.CODIGO_ALMACEN) AS D_ALMACEN,
                    acc.TIPO_PEDIDO_COM,
                    (SELECT t.DESCRIPCION
                       FROM TIPOS_PEDIDO_COM t
                      WHERE t.TIPO_PEDIDO = acc.TIPO_PEDIDO_COM AND t.ORGANIZACION_COMPRAS = acc.ORGANIZACION_COMPRAS) AS D_TIPO_PEDIDO_COM,
                    acc.CODIGO_PROVEEDOR,
                    (SELECT prlv.nombre
                        FROM proveedores prlv
                        WHERE prlv.codigo_rapido = acc.codigo_proveedor AND prlv.codigo_empresa = acc.codigo_empresa) AS D_CODIGO_PROVEEDOR,
                    (SELECT SUM(lai.IMPORTE_LIN_NETO)
                        FROM ALBARAN_COMPRAS_L lai
                        WHERE lai.NUMERO_DOC_INTERNO = acc.NUMERO_DOC_INTERNO AND lai.CODIGO_EMPRESA = acc.CODIGO_EMPRESA) AS IMPORTE_TOTAL_EUR,
                    (SELECT MIN(lai.DIVISA)
                        FROM ALBARAN_COMPRAS_L lai
                        WHERE lai.NUMERO_DOC_INTERNO = acc.NUMERO_DOC_INTERNO AND lai.CODIGO_EMPRESA = CODIGO_EMPRESA) AS DIVISA
                FROM ALBARAN_COMPRAS_C acc
                WHERE acc.CODIGO_EMPRESA = '001'
                    AND acc.ORGANIZACION_COMPRAS = '01'
                    AND acc.CENTRO_CONTABLE IN (
                            SELECT DISTINCT gru.CODIGO_CENTRO
                            FROM CENTROS_GRUPO_CCONT gru
                            WHERE gru.EMPRESA = acc.CODIGO_EMPRESA AND gru.CODIGO_GRUPO = '01')
                    AND EXISTS (
                            SELECT 1
                            FROM ALBARAN_COMPRAS_L li, ARTICULOS lia
                            WHERE li.NUMERO_DOC_INTERNO = acc.NUMERO_DOC_INTERNO AND li.CODIGO_EMPRESA = acc.CODIGO_EMPRESA AND lia.CODIGO_EMPRESA = li.CODIGO_EMPRESA AND lia.CODIGO_ARTICULO = li.CODIGO_ARTICULO)
                    AND acc.STATUS_ANULADO = 'N'
                    AND acc.NUMERO_DOC_EXT = :num_doc_ext
                    AND acc.CODIGO_ALMACEN IN ('00', '01', '02', 'E01', 'E02', 'E03', 'E04', 'E05', 'E06')
                ORDER BY acc.FECHA DESC
            """
    stock = oracle.consult(sql, {'num_doc_ext': num_doc_ext}) or []
    # for r in stock:
    #     if r['DIVISA'] != 'EUR':
    #         r['IMPORTE_TOTAL_EUR'] = float(r['IMPORTE_TOTAL_ORIGINAL']) * valor_cambio
    #     else:
    #         r['IMPORTE_TOTAL_EUR'] = float(r['IMPORTE_TOTAL_ORIGINAL'])
    return stock