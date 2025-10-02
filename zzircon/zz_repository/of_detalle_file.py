from froxa.utils.connectors.libra_connector import OracleConnector

# los detalles de una orden de fabricacion

def of_detalle_function(of_id):
    res = [{}]
    sql = """select o.ORDEN_DE_FABRICACION, 
                o.CODIGO_ARTICULO,
                (select MIN(DESCRIP_COMERCIAL) from ARTICULOS where CODIGO_ARTICULO = o.CODIGO_ARTICULO) AS NOMBRE_ARTICULO,
                o.CODIGO_PRESENTACION,
                o.CANTIDAD_A_FABRICAR,
                o.FECHA_INI_FABRI_PREVISTA,
                o.FECHA_ENTREGA_PREVISTA,
                o.SITUACION_OF
            from ORDENES_FABRICA_CAB o
            where o.ORDEN_DE_FABRICACION = :of_id"""
    
    oracle = OracleConnector()
    oracle.connect()
    res[0]['OF'] = oracle.consult(sql, {"of_id": of_id})
    
    sql_detail_packaged = """select orden_de_fabricacion,
                                   codigo_articulo_subp,
                                   d_codigo_articulo_subp,
                                   codigo_presentacion_subp,
                                   cantidad_tecnica,
                                   cantidad_a_fabricar,
                                   cantidad_tecnica_2,
                                   unidad_medida_2,
                                   valor_reparto,
                                   rendimiento_real,
                                   status_fabricacion,
                                   status_consumo,
                                   cantidad_a_fabricar2,
                                   cantidad_aceptada,
                                   cantidad_rechazada
                              from (
                               select ordenes_fabrica_multiproduc.*,
                                      (
                                         select a.descrip_comercial
                                           from articulos a
                                          where a.codigo_articulo = ordenes_fabrica_multiproduc.codigo_articulo_subp
                                            and a.codigo_empresa = ordenes_fabrica_multiproduc.codigo_empresa
                                      ) d_codigo_articulo_subp,
                                      decode(
                                         ordenes_fabrica_multiproduc.grupo_op_maquila,
                                         null,
                                         null,
                                         (
                                            select g.descripcion
                                              from grupos_op_maquila_c g
                                             where g.codigo = ordenes_fabrica_multiproduc.grupo_op_maquila
                                               and g.codigo_org_planta = ordenes_fabrica_multiproduc.codigo_org_planta
                                               and g.codigo_empresa = ordenes_fabrica_multiproduc.codigo_empresa
                                         )
                                      ) d_grupo_op_maquila,
                                      (
                                         select f.descripcion
                                           from tarifas_maquila_filtros f
                                          where f.filtro = ordenes_fabrica_multiproduc.grupo_op_maquila_filtro_mp
                                            and f.codigo_empresa = ordenes_fabrica_multiproduc.codigo_empresa
                                      ) d_grupo_op_maquila_filtro_mp,
                                      (
                                         select f.descripcion
                                           from tarifas_maquila_filtros f
                                          where f.filtro = ordenes_fabrica_multiproduc.grupo_op_maquila_filtro_pt
                                            and f.codigo_empresa = ordenes_fabrica_multiproduc.codigo_empresa
                                      ) d_grupo_op_maquila_filtro_pt,
                                      (
                                         select ar.unidad_codigo2
                                           from articulos ar
                                          where ar.codigo_articulo = ordenes_fabrica_multiproduc.codigo_articulo_subp
                                            and ar.codigo_empresa = ordenes_fabrica_multiproduc.codigo_empresa
                                      ) unidad_medida_2
                                 from ordenes_fabrica_multiproduc
                            ) ordenes_fabrica_multiproduc
                             where ( codigo_empresa = '001' )
                               and ( codigo_org_planta = '0' )
                               and ( orden_de_fabricacion = :of_id )
                             order by num_linea"""
    
    res[0]['MULTIPRODUCCION'] = oracle.consult(sql_detail_packaged, {"of_id": of_id}) or []

    # material pedido OF desde la vista 427
    material_ordered = """select orden_de_fabricacion,
                            codigo_componente,
                            codigo_presentacion_compo,
                            cantidad_tecnica,
                            consumo_teorico,
                            afecta_al_rendimiento,
                            compo_desc_comercial,
                            codigo_familia,
                            d_codigo_familia,
                            codigo_articulo,
                            codigo_presentacion,
                            ejercicio
                        from (
                         select ordenes_fabrica_compo.*,
                                (
                                   select codigo_familia
                                     from articulos
                                    where codigo_empresa = ordenes_fabrica_compo.codigo_empresa
                                      and codigo_articulo = ordenes_fabrica_compo.codigo_componente
                                ) codigo_familia,
                                (
                                   select descrip_comercial
                                     from articulos
                                    where codigo_empresa = ordenes_fabrica_compo.codigo_empresa
                                      and codigo_articulo = ordenes_fabrica_compo.codigo_componente
                                ) compo_desc_comercial,
                                (
                                   select f.descripcion
                                     from familias f,
                                          articulos a
                                    where a.codigo_empresa = ordenes_fabrica_compo.codigo_empresa
                                      and a.codigo_articulo = ordenes_fabrica_compo.codigo_componente
                                      and f.numero_tabla = 1
                                      and f.codigo_familia = a.codigo_familia
                                      and a.codigo_empresa = f.codigo_empresa
                                ) d_codigo_familia
                           from ordenes_fabrica_compo
                        )ordenes_fabrica_compo
                        where orden_de_fabricacion =  :of_id"""
 
    res[0]['MATERIAL_PEDIDO'] = oracle.consult(material_ordered, {"of_id": of_id})

    material_consumed = """SELECT
                              MAX(om.ORDEN_DE_FABRICACION)                 AS ORDEN_DE_FABRICACION,
                              om.CODIGO_COMPONENTE                         AS CODIGO_ARTICULO_CONSUMIDO,
                              MAX(om.DESC_ARTICULO)                        AS DESCRIP_CONSUMIDO,
                              MAX(om.CODIGO_PRESENTACION_COMPO)            AS CODIGO_PRESENTACION,
                              om.NUMERO_LOTE_INT                           AS NUMERO_LOTE_INT_CONSUMIDO,
                              SUM(NVL(om.CANT_REAL_CONSUMO_UNIDAD1,0)) AS CANTIDAD_UNIDAD1,
                              MAX(hl.FECHA_CREACION)                       AS FECHA_CREACION,
                              MAX(hl.FECHA_CADUCIDAD)                      AS FECHA_CADUCIDAD
                            FROM OF_MATERIALES_UTILIZADOS om
                            LEFT JOIN HISTORICO_LOTES hl
                              ON hl.NUMERO_LOTE_INT = om.NUMERO_LOTE_INT
                             AND hl.CODIGO_ARTICULO = om.CODIGO_COMPONENTE
                            WHERE om.ORDEN_DE_FABRICACION = :of_id
                            GROUP BY
                              om.CODIGO_COMPONENTE,
                              om.NUMERO_LOTE_INT
                            ORDER BY om.CODIGO_COMPONENTE, om.NUMERO_LOTE_INT
                        """

    res[0]['MATERIAL_CONSUMIDO'] = oracle.consult(material_consumed, {"of_id": of_id})

    material_produced = """select h.CODIGO_ARTICULO,
                           (select art.DESCRIP_COMERCIAL from  articulos art where art.codigo_articulo = h.CODIGO_ARTICULO) as DESCRIP_COMERCIAL,
                            h.CODIGO_MOVIMIENTO, 
                            h.PARTE_OF,
                            h.TIPO_MOVIMIENTO, 
                            h.TIPO_SITUACION, 
                            h.NUMERO_LOTE_INT,
                            h.PRESENTACION as CODIGO_PRESENTACION, 
                            h.EJERCICIO, 
                            h.NUMERO_PALET, 
                            h.CANTIDAD_UNIDAD1,
                            h.FECHA_MOVIM,
                            (select MAX(FECHA_CREACION) from historico_lotes where NUMERO_LOTE_INT  =  h.NUMERO_LOTE_INT and CODIGO_ARTICULO =  h.CODIGO_ARTICULO) AS FECHA_CREACION,
                            (select MAX(FECHA_CADUCIDAD) from historico_lotes where NUMERO_LOTE_INT =  h.NUMERO_LOTE_INT and CODIGO_ARTICULO =  h.CODIGO_ARTICULO) AS FECHA_CADUCIDAD
                            from historico_movim_almacen h
                            where (h.ORDEN_DE_FABRICACION = :of_id  and h.tipo_movimiento = '20' and h.PARTE_OF > 0) and (h.CODIGO_MOVIMIENTO = '2051L' or h.CODIGO_MOVIMIENTO = '205ML')
                        """
    res[0]['MATERIAL_PRODUCIDO'] = oracle.consult(material_produced, {"of_id": of_id})

    listAppOFs = res[0]['OF']
    if len(listAppOFs) > 0:
        for appOf in listAppOFs:
            codArt = appOf['CODIGO_ARTICULO']
        
            ficha_articulo = """SELECT art.CODIGO_ARTICULO, 
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
            
            res[0]['FICHA_ARTICULO'] = oracle.consult(ficha_articulo, {'codArt': codArt})
            break
    
    oracle.close()
    return res