def get_list_palets_prod(request, oracle):
    sql = """SELECT
              lote codigo_entrada,
              (s.codigo_articulo || ' ' || (SELECT aa.DESCRIP_COMERCIAL from articulos aa WHERE aa.codigo_articulo = s.codigo_articulo)) articulo,
              (s.codigo_almacen || ' ' || (SELECT alm.nombre from almacenes alm WHERE alm.almacen = s.codigo_almacen)) almacen,
              s.tipo_situacion situacion,
              s.numero_lote_int numero_lote,
              s.cantidad_unidad1 cantidad_kg
            FROM (
              SELECT
                s.*,
                (SELECT MAX(h.descripcion_lote2)
                   FROM historico_lotes h
                  WHERE h.numero_lote_int = s.numero_lote_int
                    AND h.codigo_articulo = s.codigo_articulo
                    AND h.codigo_empresa  = s.codigo_empresa
                ) AS lote
              FROM stocks_deposito_cli s
              WHERE s.codigo_empresa  = '001' AND s.cantidad_con <> 0
            ) s
            WHERE s.lote = 'PRODUCCION' AND s.codigo_almacen = '90' AND s.tipo_situacion = 'CALID'"""
    
    res = oracle.consult(sql) or []
    return res