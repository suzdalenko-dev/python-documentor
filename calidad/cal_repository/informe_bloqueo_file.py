from froxa.utils.connectors.libra_connector import OracleConnector


def informe_bloqueo(request):
    sql = """SELECT 
                ALMACEN,
                D_ALMACEN,
                TIPO_SITUACION,
                CODIGO_PROVEEDOR,
                D_CODIGO_PROVEEDOR,
                LOTE,
                NUMERO_LOTE_INT,
                DESCRIPCION_ARTICULO_MIRROR,
                CODIGO_ARTICULO,
                CANTIDAD_CON,
                CANTIDAD_EXP,
                UNIDAD_CODIGO1,
                D_TIPO_SITUACION,
                D_CODIGO_FAMILIA
                D_CODIGO_ESTAD2,
                D_CODIGO_ESTAD3    
                FROM (SELECT DATOS.* ,almacen ALMACEN_MIRROR,codigo_articulo ARTICULO_MIRROR,(SELECT SUM(pl.cantidad_unidad1)
               FROM articulos ar, barcos ba, lotes lo,mareas ma, nota_pesca pc, nota_pesca_lin pl
              WHERE pc.empresa = pl.empresa
                AND pc.codigo = pl.codigo
                AND pc.marea = pl.marea
                AND ba.codigo = ma.barco
                AND ba.empresa = ma.empresa
            and lo.lote = ma.codigo_entrada
            and lo.empresa = ma.empresa
            and lo.descarga_finalizada='N'
                AND ar.codigo_articulo = pl.articulo
                AND ar.codigo_empresa = pl.empresa
                AND ma.empresa = pl.empresa
                AND ma.codigo = pl.marea
            and pl.articulo = datos.codigo_articulo
                AND pl.empresa = datos.empresa
            and ma.situacion='1000') CANTIDAD_NOTAS_PESCA,(select sum(PL.UNIDADES_PEDIDAS - PL.UNIDADES_ENTREGADAS)
            FROM PARAM_COMPRAS p, articulos a, pedidos_compras pc, pedidos_compras_lin pl
                     WHERE     PL.CODIGO_EMPRESA = PC.CODIGO_EMPRESA
                           AND PL.ORGANIZACION_COMPRAS = PC.ORGANIZACION_COMPRAS
                           AND PL.SERIE_NUMERACION = PC.SERIE_NUMERACION
                           AND PL.NUMERO_PEDIDO = PC.NUMERO_PEDIDO
                           AND A.CODIGO_EMPRESA = PL.CODIGO_EMPRESA
                           AND A.CODIGO_ARTICULO = PL.CODIGO_ARTICULO
                           and p.CODIGO_EMPRESA = pc.codigo_empresa
                           and p.ORGANIZACION_COMPRAS = PC.ORGANIZACION_COMPRAS
                           AND PL.STATUS_CIERRE = 'E'
                           AND pl.codigo_articulo = DATOS.CODIGO_ARTICULO
                  and (P.ALMACEN_DISTINTO = 'S' or (P.ALMACEN_DISTINTO = 'N' AND PC.CODIGO_ALMACEN = DATOS.ALMACEN))
                 AND PL.UNIDADES_PEDIDAS - nvl(PL.UNIDADES_ENTREGADAS, 0) > 0
             AND pc.codigo_empresa = datos.empresa) CANTIDAD_PEND_RECI,cliente CLIENTE_MIRROR,CODIGO_ARTICULO_AUX CODIGO_ARTICULO_MIRROR,DESCRIPCION_ARTICULO DESCRIPCION_ARTICULO_MIRROR,(SELECT h.descripcion_lote FROM historico_lotes h WHERE h.numero_lote_int = NVL(datos.numero_lote_int_aux, datos.numero_lote_int)AND h.codigo_articulo = datos.codigo_articulo AND h.codigo_empresa = datos.empresa) DESCRIPCION_PARTIDA_MIRROR,(SELECT lval.nombre FROM almacenes lval WHERE lval.almacen = datos.almacen AND lval.codigo_empresa = datos.empresa) D_ALMACEN,datos.almacen D_ALMACEN_MIRROR,DESCRIPCION_ARTICULO D_ARTICULO_MIRROR,(SELECT lvb.nombre FROM barcos lvb WHERE lvb.codigo = datos.barco_lote AND lvb.empresa = datos.empresa ) D_BARCO_LOTE,(Select lvb.nombre from buques lvb where lvb.codigo = datos.buque and lvb.empresa =datos.empresa) D_BUQUE,(SELECT lvcc.nombre FROM caracteres_asiento lvcc WHERE lvcc.codigo = datos.centro_contable AND lvcc.empresa = datos.empresa) D_CENTRO_CONTABLE,(select ca.nombre from caracteres_asiento ca where ca.empresa=datos.empresa and ca.codigo=datos.centro_contable_frio) D_CENTRO_CONTABLE_FRIO,(SELECT c.nombre FROM clientes c WHERE c.codigo_rapido = datos.cliente AND c.codigo_empresa = datos.empresa) D_CLIENTE,(SELECT c.nombre FROM clientes c WHERE c.codigo_rapido = datos.cliente_facturacion_frio AND c.codigo_empresa = datos.empresa) D_CLIENTE_FACTURACION_FRIO,datos.cliente D_CLIENTE_MIRROR,(SELECT prlv.nombre FROM proveedores prlv WHERE prlv.codigo_rapido = datos.codigo_proveedor AND codigo_empresa = datos.empresa) D_CODIGO_PROVEEDOR,(SELECT lvlot.descripcion FROM lotes lvlot WHERE lvlot.lote = datos.lote_aux AND lvlot.empresa = datos.empresa) D_LOTE_AUX,(SELECT lvm.descripcion FROM mareas lvm WHERE lvm.codigo = datos.marea AND lvm.empresa = datos.empresa) D_MAREA,(SELECT lvrs.descripcion FROM registros_sanitarios lvrs where lvrs.numero_registro = datos.registro_sanitario and lvrs.empresa = datos.empresa) D_REGISTRO_SANITARIO,(SELECT lvtpm.descripcion FROM tipos_movimiento lvtpm WHERE lvtpm.codigo = datos.tipo_doc_entrada) D_TIPO_DOC_ENTRADA,(SELECT lvtp.descripcion FROM tipos_palet lvtp WHERE lvtp.codigo = datos.tipo_palet AND lvtp.empresa = datos.empresa) D_TIPO_PALET,(SELECT lvtp.descripcion FROM tipos_palet lvtp WHERE lvtp.codigo = datos.tipo_recipiente AND lvtp.empresa = datos.empresa) D_TIPO_RECIPIENTE,(SELECT lvts.descripcion FROM tipos_situacion lvts WHERE lvts.tipo_situacion = datos.tipo_situacion AND lvts.codigo_empresa = datos.empresa) D_TIPO_SITUACION,(SELECT lvaz.descripcion FROM almacenes_zonas lvaz WHERE lvaz.codigo_zona = datos.zona_almacen AND lvaz.codigo_almacen = datos.almacen AND lvaz.codigo_empresa = datos.empresa) D_ZONA_ALMACEN,(select NVL(id_digital, 0) from lotes l where l.empresa = DATOS.EMPRESA and l.lote = DATOS.LOTE) ID_DIGITAL,DECODE(UNID_VALORACION,  0, 0,  COSTE / UNID_VALORACION) PRECIO_COSTE,recipiente RECIPIENTE_MIRROR,NULL RESERVADOA01,NULL RESERVADOA02,NULL RESERVADOA03,NULL RESERVADOA04 FROM (SELECT m.codigo_almacen almacen,  NULL zona_almacen, m.tipo_situacion ,s.stock_disponible  ,m.numero_lote_int,   h.numero_lote_pro ,m.numero_lote_int numero_lote_int_aux, m.codigo_articulo, m.codigo_articulo codigo_articulo_aux, h.documento_entrada, h.codigo_creacion tipo_doc_entrada,  l.descarga_finalizada descarga_finalizada, ma.codigo marea, l.barco barco_lote, l.buque, ma.zona_fao fao_marea, COALESCE(alm.centro_contable, l.centro_contable_fact_frio, l.centro_contable) centro_contable_frio,  NULL coste,  NULL unid_valoracion,  NULL recipiente, NULL tipo_recipiente, NULL Obs_Hist_Palets, NULL sscc,  m.cantidad_con, m.cantidad_sub, m.cantidad_sob, m.cantidad_dis, m.cantidad_exp, DECODE(s.stock_disponible, 'N', 0, m.cantidad_con -  pk_parametros_pesca.calcula_stock_en_pedidos(m.codigo_empresa, m.codigo_cliente, NULL, NULL, NULL, NULL, NULL, m.codigo_articulo, m.numero_lote_int,h.descripcion_lote2, m.codigo_almacen, 'CON', l.centro_contable,m.tipo_situacion) ) cantidad_con2,  DECODE(s.stock_disponible, 'N', 0, m.cantidad_sub -  pk_parametros_pesca.calcula_stock_en_pedidos(m.codigo_empresa, m.codigo_cliente, NULL, NULL, NULL, NULL, NULL, m.codigo_articulo, m.numero_lote_int,h.descripcion_lote2, m.codigo_almacen, 'SUB', l.centro_contable,m.tipo_situacion) ) cantidad_sub2,  DECODE(s.stock_disponible, 'N', 0, m.cantidad_sob -  pk_parametros_pesca.calcula_stock_en_pedidos(m.codigo_empresa, m.codigo_cliente, NULL, NULL, NULL, NULL, NULL, m.codigo_articulo, m.numero_lote_int,h.descripcion_lote2, m.codigo_almacen, 'SOB', l.centro_contable,m.tipo_situacion) ) cantidad_sob2,  DECODE(s.stock_disponible, 'N', 0, m.cantidad_dis -  pk_parametros_pesca.calcula_stock_en_pedidos(m.codigo_empresa, m.codigo_cliente, NULL, NULL, NULL, NULL, NULL, m.codigo_articulo, m.numero_lote_int,h.descripcion_lote2, m.codigo_almacen, 'DIS', l.centro_contable,m.tipo_situacion) ) cantidad_dis2,  DECODE(s.stock_disponible, 'N', 0, m.cantidad_exp -  pk_parametros_pesca.calcula_stock_en_pedidos(m.codigo_empresa, m.codigo_cliente, NULL, NULL, NULL, NULL, NULL, m.codigo_articulo, m.numero_lote_int,h.descripcion_lote2, m.codigo_almacen, 'EXP', l.centro_contable,m.tipo_situacion) ) cantidad_exp2,  DECODE(s.stock_disponible, 'N', 0, m.cantidad_unidad1 -  pk_parametros_pesca.calcula_stock_en_pedidos(m.codigo_empresa, m.codigo_cliente, NULL, NULL, NULL, NULL, NULL, m.codigo_articulo, m.numero_lote_int,h.descripcion_lote2, m.codigo_almacen, 'CT1', l.centro_contable,m.tipo_situacion) ) cantidad_almacen12,  DECODE(s.stock_disponible, 'N', 0, m.cantidad_unidad2 -  pk_parametros_pesca.calcula_stock_en_pedidos(m.codigo_empresa, m.codigo_cliente, NULL, NULL, NULL, NULL, NULL, m.codigo_articulo, m.numero_lote_int,h.descripcion_lote2, m.codigo_almacen, 'CT2', l.centro_contable,m.tipo_situacion) ) cantidad_almacen22, l.lote_ext, m.cantidad_unidad1 cantidad_almacen1,m.cantidad_unidad2 cantidad_almacen2, m.codigo_empresa empresa,  h.descripcion_lote2 lote,  h.descripcion_lote2 lote_aux, DECODE('V','V',a.descrip_comercial,'T',a.descrip_tecnica,'C',a.descrip_compra,a.descrip_comercial) descripcion_articulo,DECODE('V','V',a.descrip_comercial,'T',a.descrip_tecnica,'C',a.descrip_compra,a.descrip_comercial) descripcion_articulo_aux,  a.unidad_Codigo1,a.unidad_codigo2,a.codigo_valor_invent,a.unidad_valoracion,a.cantidad_precio,a.incluir_gtos_gener_invent,
                   a.codigo_familia,(select descripcion from familias where numero_tabla = '1' AND codigo_familia = a.codigo_familia AND codigo_empresa = '001') d_codigo_familia,
                   a.codigo_estad2,(select descripcion from familias where numero_tabla = '2' AND codigo_familia = a.codigo_estad2 AND codigo_empresa = '001') d_codigo_estad2,
                   a.codigo_estad3,(select descripcion from familias where numero_tabla = '3' AND codigo_familia = a.codigo_estad3 AND codigo_empresa = '001') d_codigo_estad3,
                   a.codigo_estad4,(select descripcion from familias where numero_tabla = '4' AND codigo_familia = a.codigo_estad4 AND codigo_empresa = '001') d_codigo_estad4,
                   a.codigo_estad5,(select descripcion from familias where numero_tabla = '5' AND codigo_familia = a.codigo_estad5 AND codigo_empresa = '001') d_codigo_estad5,
                   a.codigo_estad6,(select descripcion from familias where numero_tabla = '6' AND codigo_familia = a.codigo_estad6 AND codigo_empresa = '001') d_codigo_estad6,
                   a.codigo_estad7,(select descripcion from familias where numero_tabla = '7' AND codigo_familia = a.codigo_estad7 AND codigo_empresa = '001') d_codigo_estad7,
                   a.codigo_estad8,(select descripcion from familias where numero_tabla = '8' AND codigo_familia = a.codigo_estad8 AND codigo_empresa = '001') d_codigo_estad8,
                   a.codigo_estad9,(select descripcion from familias where numero_tabla = '9' AND codigo_familia = a.codigo_estad9 AND codigo_empresa = '001') d_codigo_estad9,
                   a.codigo_estad10,(select descripcion from familias where numero_tabla = '10' AND codigo_familia = a.codigo_estad10 AND codigo_empresa = '001') d_codigo_estad10, 
                   a.codigo_estad11,(select descripcion from familias where numero_tabla = '11' AND codigo_familia = a.codigo_estad11 AND codigo_empresa = '001') d_codigo_estad11, 
                   a.codigo_estad12,(select descripcion from familias where numero_tabla = '12' AND codigo_familia = a.codigo_estad12 AND codigo_empresa = '001') d_codigo_estad12, 
                   a.codigo_estad13,(select descripcion from familias where numero_tabla = '13' AND codigo_familia = a.codigo_estad13 AND codigo_empresa = '001') d_codigo_estad13, 
                   a.codigo_estad14,(select descripcion from familias where numero_tabla = '14' AND codigo_familia = a.codigo_estad14 AND codigo_empresa = '001') d_codigo_estad14, 
                   a.codigo_estad15,(select descripcion from familias where numero_tabla = '15' AND codigo_familia = a.codigo_estad15 AND codigo_empresa = '001') d_codigo_estad15, 
                   a.codigo_estad16,(select descripcion from familias where numero_tabla = '16' AND codigo_familia = a.codigo_estad16 AND codigo_empresa = '001') d_codigo_estad16, 
                   a.codigo_estad17,(select descripcion from familias where numero_tabla = '17' AND codigo_familia = a.codigo_estad17 AND codigo_empresa = '001') d_codigo_estad17, 
                   a.codigo_estad18,(select descripcion from familias where numero_tabla = '18' AND codigo_familia = a.codigo_estad18 AND codigo_empresa = '001') d_codigo_estad18, 
                   a.codigo_estad19,(select descripcion from familias where numero_tabla = '19' AND codigo_familia = a.codigo_estad19 AND codigo_empresa = '001') d_codigo_estad19, 
                   a.codigo_estad20,(select descripcion from familias where numero_tabla = '20' AND codigo_familia = a.codigo_estad20 AND codigo_empresa = '001') d_codigo_estad20, 
                   t.titulo_alfa_1, t.titulo_alfa_2, t.titulo_alfa_3, t.titulo_alfa_4, t.titulo_alfa_5, t.titulo_alfa_6, t.titulo_alfa_7, t.titulo_alfa_8, t.titulo_alfa_9, t.titulo_alfa_10,
                 t.titulo_num_1, t.titulo_num_2, t.titulo_num_3, t.titulo_num_4, t.titulo_num_5, t.titulo_num_6, t.titulo_num_7, t.titulo_num_8, t.titulo_num_9, t.titulo_num_10,
                 t.titulo_fecha_1, t.titulo_fecha_2, t.titulo_fecha_3,
                 c.valor_alfa_1, c.valor_alfa_2, c.valor_alfa_3, c.valor_alfa_4, c.valor_alfa_5, c.valor_alfa_6, c.valor_alfa_7, c.valor_alfa_8, c.valor_alfa_9, c.valor_alfa_10,  (SELECT descripcion FROM titulos_personaliz_des WHERE valor=c.valor_alfa_1 AND numero=1 AND codigo_personaliz=a.codigo_personaliz_lotes AND empresa='001') d_valor_alfa_1, (SELECT descripcion FROM titulos_personaliz_des WHERE valor=c.valor_alfa_2 AND numero=2 AND codigo_personaliz=a.codigo_personaliz_lotes AND empresa='001') d_valor_alfa_2, (SELECT descripcion FROM titulos_personaliz_des WHERE valor=c.valor_alfa_3 AND numero=3 AND codigo_personaliz=a.codigo_personaliz_lotes AND empresa='001') d_valor_alfa_3, (SELECT descripcion FROM titulos_personaliz_des WHERE valor=c.valor_alfa_4 AND numero=4 AND codigo_personaliz=a.codigo_personaliz_lotes AND empresa='001') d_valor_alfa_4, (SELECT descripcion FROM titulos_personaliz_des WHERE valor=c.valor_alfa_5 AND numero=5 AND codigo_personaliz=a.codigo_personaliz_lotes AND empresa='001') d_valor_alfa_5, (SELECT descripcion FROM titulos_personaliz_des WHERE valor=c.valor_alfa_6 AND numero=6 AND codigo_personaliz=a.codigo_personaliz_lotes AND empresa='001') d_valor_alfa_6, (SELECT descripcion FROM titulos_personaliz_des WHERE valor=c.valor_alfa_7 AND numero=7 AND codigo_personaliz=a.codigo_personaliz_lotes AND empresa='001') d_valor_alfa_7, (SELECT descripcion FROM titulos_personaliz_des WHERE valor=c.valor_alfa_8 AND numero=8 AND codigo_personaliz=a.codigo_personaliz_lotes AND empresa='001') d_valor_alfa_8, (SELECT descripcion FROM titulos_personaliz_des WHERE valor=c.valor_alfa_9 AND numero=9 AND codigo_personaliz=a.codigo_personaliz_lotes AND empresa='001') d_valor_alfa_9, (SELECT descripcion FROM titulos_personaliz_des WHERE valor=c.valor_alfa_10 AND numero=10 AND codigo_personaliz=a.codigo_personaliz_lotes AND empresa='001') d_valor_alfa_10, (SELECT registro_sanitario FROM titulos_personaliz_des WHERE valor=decode(t.valor_alfa_registro,'1',c.valor_alfa_1,'2',c.valor_alfa_2,'3',c.valor_alfa_3,'4',c.valor_alfa_4,
                  '5',c.valor_alfa_5,'6',c.valor_alfa_6,'7',c.valor_alfa_7,'8',c.valor_alfa_8,'9',c.valor_alfa_9,'10',
                  c.valor_alfa_10) AND numero=t.valor_alfa_registro AND codigo_personaliz=a.codigo_personaliz_lotes AND empresa='001') registro_Sanitario,
                 c.valor_num_1, c.valor_num_2, c.valor_num_3, c.valor_num_4, c.valor_num_5, c.valor_num_6, c.valor_num_7, c.valor_num_8, c.valor_num_9, c.valor_num_10,
                 c.valor_fecha_1, c.valor_fecha_2, c.valor_fecha_3,
                   (SELECT numero_autorizacion_cliente FROM DOCUMENTO_VINCULACION_DEPOSITO D 
                   WHERE D.CODIGO = h.codigo_dvd AND d.empresa = h.codigo_empresa) numero_autorizacion_cliente,
                   (SELECT numero_dip FROM DOCUMENTO_VINCULACION_DEPOSITO D WHERE D.CODIGO = h.codigo_dvd AND d.empresa = h.codigo_empresa) numero_dip,
                   (SELECT fecha_liberacion_dip FROM DOCUMENTO_VINCULACION_DEPOSITO D WHERE D.CODIGO = h.codigo_dvd AND d.empresa = h.codigo_empresa) fecha_liberacion_dip,
                (SELECT numero_dvce FROM DOCUMENTO_VINCULACION_DEPOSITO D WHERE D.CODIGO = h.codigo_dvd AND d.empresa = h.codigo_empresa) numero_dvce,
                 (SELECT e.nombre FROM documento_vinculacion_deposito d, aduanas a, estados e WHERE a.codigo = d.aduana_registro 
                 AND e.codigo = a.estado AND d.codigo = h.codigo_dvd AND d.empresa = h.codigo_empresa) estado_dvd,   
                   h.tara_con, h.tara_sub, h.tara_sob, h.tara_dis, 
                   h.tara_exp,  h.codigo_dvd codigo_dvd, h.codigo_proveedor,h.FECHA_FIN_FACT_FRIO_CLI_ORIGEN,h.cliente_facturacion_frio,h.fecha_siguiente_fact_frio, h.descripcion_lote d_numero_lote_int,h.descripcion_lote d_numero_lote_int_aux, null codigo_subreferencia,  h.fecha_caducidad, h.fecha_creacion, h.numero_lote_int_anterior,  a.alfa3_fao, a.partida_arancelaria partida_arancelaria, (SELECT nc.nombre_cientifico FROM nombres_cientificos nc WHERE nc.codigo = a.alfa3_fao) nombre_cientifico, (SELECT nc.descripcion FROM partidas_arancelarias nc WHERE nc.empresa = m.codigo_empresa AND nc.codigo = a.partida_arancelaria) d_partida_arancelaria,  m.codigo_cliente cliente, NULL palet, null numero_transporte, NULL d_numero_transporte, NULL ubicacion,  l.centro_contable,  NULL tipo_palet  FROM tipos_situacion s, almacenes alm,  caracteristicas_lotes c, titulos_personaliz t,lotes l, articulos a, historico_lotes h,  mareas ma,  stocks_deposito_cli m  WHERE h.numero_lote_int = m.numero_lote_int
               AND h.codigo_articulo = m.codigo_articulo
               AND h.codigo_empresa = m.codigo_empresa 
               AND l.lote(+) = h.descripcion_lote2
               AND l.empresa(+) = h.codigo_empresa  
               and ma.codigo(+) = l.marea
               and ma.empresa(+) = l.empresa 
               AND a.codigo_articulo = m.codigo_articulo
               AND a.codigo_empresa = m.codigo_empresa
               AND s.tipo_situacion = m.tipo_situacion
               AND s.codigo_empresa = m.codigo_empresa 
               AND alm.almacen = m.codigo_almacen
               AND alm.codigo_empresa = m.codigo_empresa  AND t.codigo_personaliz(+) = a.codigo_personaliz_lotes
                 AND t.codigo_empresa(+) = a.codigo_empresa
                 AND c.codigo_articulo(+) = m.codigo_articulo
                 AND c.numero_lote_int(+) = m.numero_lote_int
                 AND c.codigo_empresa(+) = m.codigo_empresa AND m.codigo_empresa = '001' AND m.codigo_almacen BETWEEN '00' AND '01' AND m.tipo_situacion IN ('CALID')  AND m.cantidad_CON != 0  ORDER BY cliente, lote, numero_lote_int) datos) d WHERE 1=1"""
    
    oracle = OracleConnector()
    oracle.connect()
    blockLines  = oracle.consult(sql)

    for b in blockLines:
        code = b['CODIGO_ARTICULO']
        lote = b['NUMERO_LOTE_INT']
        sql = """select codigo_articulo, OBSERVACIONES
                from historico_movim_almacen
                where codigo_articulo = :code
                    and OBSERVACIONES IS NOT NULL
                    and CODIGO_MOVIMIENTO = '1185L'
                    and TIPO_SITUACION = 'CALID'
                    and NUMERO_LOTE_INT = :lote
        """
        observ = oracle.consult(sql, {'code':code, 'lote':lote})
        b['coments'] = observ
        
    oracle.close()
    return blockLines