from froxa.utils.connectors.libra_connector import OracleConnector


def article_detail(code):
    oracle = OracleConnector()
    oracle.connect()

    if code == 'all':
        sql_all = """SELECT art.CODIGO_ARTICULO, art.DESCRIP_COMERCIAL FROM articulos art"""
        res = oracle.consult(sql_all)
    else:
        res = [{'DETALLE':{}, 'PRECIO':{}, 'STOCK':{}}]
        sql = """SELECT art.CODIGO_ARTICULO, 
                                    art.DESCRIP_COMERCIAL,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'DESCRIPCION' AND C3 = 'A1A' AND ROWNUM = 1) AS DESCRIPCION,
                                    '' AS CATEGORIA_COMERCIAL,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'NOMBRE CIENTIFICO' AND ROWNUM = 1)  AS NOMBRE_CIENTIFICO,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'METODO PRODUCCION' AND ROWNUM = 1)  AS METODO_PRODUCCION,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'ARTE PESCA' AND ROWNUM = 1)  AS ARTE_PESCA,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'PAIS ORIGEN/CAPTURA' AND ROWNUM = 1)  AS PAIS_ORIGEN_CAPTURA,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'ZONA CAPTURA' AND ROWNUM = 1)  AS ZONA_CAPTURA,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'PESO NETO ESCURRIDO' AND ROWNUM = 1)  AS PESO_NETO_ESCURRIDO,
                                    art.RESERVADO_NUMBER_5 AS PESO_KG_ESCURRIDO,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND C3 = 'A2R' AND ROWNUM = 1) AS TALLA,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'INGREDIENTES' AND ROWNUM = 1)  AS INGREDIENTES,
                                    '' AS AGUA,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'CONTIENE' AND ROWNUM = 1)  AS CONTIENE,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'VALOR ENERGETICO KJ' AND ROWNUM = 1)  AS VALOR_ENERGETICO_KJ,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'VALOR ENERGETICO KCAL' AND ROWNUM = 1)  AS VALOR_ENERGETICO_KCA,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'GRASA' AND ROWNUM = 1)  AS GRASA,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'SAT' AND ROWNUM = 1)  AS SATURADA,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'HCO' AND ROWNUM = 1)  AS HIDRATOS_DE_CARBONO,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'AZ' AND ROWNUM = 1)  AS AZUCARES,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'PROT' AND ROWNUM = 1)  AS PROTEINAS,
                                    (SELECT VALOR_FICHA_TECNICA_ESPANOL FROM MIG_PAUTAS_IDIOMA mpi WHERE mpi.CODIGO = :codArt AND DESCRIPCION2 = 'SAL' AND ROWNUM = 1)  AS SAL,
                                    '' AS VIDA_UTIL,
                                    '' AS CONDICIONES_CONSERVACION,
                                    '' AS METODO_EMPPLEO,
                                    '' AS CONSUMIR_ANTES_DE
                
                                FROM articulos art
                                WHERE art.CODIGO_ARTICULO = :codArt
                            """
        sql_all = """SELECT art.CODIGO_ARTICULO, art.DESCRIP_COMERCIAL FROM articulos art"""
        res1 = oracle.consult(sql, {'codArt': code})
        res[0]['DETALLE'] = res1
    
        sql2 = """select TO_NUMBER(PRECIO_MEDIO_PONDERADO) AS PRECIO_MEDIO_PONDERADO, TO_NUMBER(PRECIO_STANDARD) AS PRECIO_STANDARD, CODIGO_ALMACEN
                    from ARTICULOS_VALORACION 
                    where CODIGO_ARTICULO = :codArt 
                        AND CODIGO_DIVISA = 'EUR' 
                """
        res2 = oracle.consult(sql2, {'codArt': code})
        res[0]['PRECIO'] = res2

        sql3 = """SELECT V_CODIGO_ALMACEN,
                    D_CODIGO_ALMACEN,
                    V_TIPO_SITUACION,
                    V_CANTIDAD_PRESENTACION,
                    V_PRESENTACION
                FROM 
                (
                    SELECT  s.* , 
                        CANTIDAD_PRESENTACION V_CANTIDAD_PRESENTACION,
                        CODIGO_ALMACEN V_CODIGO_ALMACEN,
                        PRESENTACION V_PRESENTACION,
                        STOCK_UNIDAD1 V_STOCK_UNIDAD1,
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
                )  s WHERE (NVL(stock_unidad1, 0) != 0) and CODIGO_ARTICULO=:erp_code order by codigo_almacen"""
        
        res3 = oracle.consult(sql3, {'erp_code': code})
        res[0]['STOCK'] = res3

        sql4 = """select 
                       (SELECT ntt.DESCRIPCION FROM NUMERO_TABLAS ntt WHERE ntt.NUMERO_TABLA = c.numero_tabla AND ROWNUM = 1) AS ETIQUETA, 
                       v_codigo,
                       d_codigo,
                       numero_tabla
                  from (
                   select c.*,
                          (
                             select lvfm.descripcion
                               from familias lvfm
                              where lvfm.codigo_familia = c.codigo
                                and lvfm.numero_tabla = c.numero_tabla
                                and lvfm.codigo_empresa = c.codigo_empresa
                          ) d_codigo,
                          codigo v_codigo
                     from (
                      select decode(
                         numero_tabla,
                         1,
                         'CODIGO_FAMILIA',
                         'CODIGO_ESTAD' || numero_tabla
                      ) campo,
                             codigo_empresa,
                             codigo_articulo,
                             codigo,
                             numero_tabla
                        from articulos unpivot ( codigo
                         for numero_tabla
                      in ( codigo_familia as 1,
                           codigo_estad2 as 2,
                           codigo_estad3 as 3,
                           codigo_estad4 as 4,
                           codigo_estad5 as 5,
                           codigo_estad6 as 6,
                           codigo_estad7 as 7,
                           codigo_estad8 as 8,
                           codigo_estad9 as 9,
                           codigo_estad10 as 10,
                           codigo_estad11 as 11,
                           codigo_estad12 as 12,
                           codigo_estad13 as 13,
                           codigo_estad14 as 14,
                           codigo_estad15 as 15,
                           codigo_estad16 as 16,
                           codigo_estad17 as 17,
                           codigo_estad18 as 18,
                           codigo_estad19 as 19,
                           codigo_estad20 as 20 ) )
                   ) c
                ) c
                 where ( codigo_articulo = :erp_code )
                   and ( codigo_empresa = '001' )
                 order by numero_tabla
                    """
        res4 = oracle.consult(sql4, {'erp_code': code})
        res[0]['CLASIFICACION'] = res4

    oracle.close()
    return res