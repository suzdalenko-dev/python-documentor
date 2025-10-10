SELECT * from EXPEDIENTES_IMP
where divisa = 'USD'
order by CODIGO desc
;

select CODIGO, PROVEEDOR, FECHA_EXPEDIENTE, VALOR_CAMBIO, USUARIO_APERTURA, USUARIO_RESPONSABLE
from EXPEDIENTES_IMP
where divisa = 'USD' and FECHA_EXPEDIENTE >= '01/01/2025' and FECHA_EXPEDIENTE <= '31/12/2025'
order by CODIGO desc
;


SELECT * from clientes;
SELECT * from proveedores;

SELECT GC1,D_GC1,GC2, GN1 FROM (SELECT EMPRESA GC1,DECODE(froxa_seguros_cambio.empresa,NULL,NULL,(SELECT lvemp.nombre FROM empresas_conta lvemp WHERE lvemp.codigo = froxa_seguros_cambio.empresa)) D_GC1,PERIODO GC2,CAMBIO GN1,NULL GN2,NULL GN3,NULL GN4,NULL GN5,NULL GN6,NULL GN7,NULL GN8,NULL GN9,NULL GN10,NULL GN11,NULL GN12,NULL GN13,NULL GN14,NULL GN15,NULL GN16,NULL GN17,NULL GN18,NULL GN19,NULL GN20,NULL GN21,NULL GN22,NULL GN23,NULL GN24,NULL GN25,NULL GC3,NULL GC4,NULL GC5,NULL GC6,NULL GC7,NULL GC8,NULL GC9,NULL GC10,NULL GC11,NULL GC12,NULL GC13,NULL GC14,NULL GC15,NULL GC16,NULL GC17,NULL GC18,NULL GC19,NULL GC20,NULL GC21,NULL GC22,NULL GC23,NULL GC24,NULL GC25,NULL GD1,NULL GD2,NULL GD3,NULL GD4,NULL GD5,NULL GD6,NULL GD7,NULL GD8,NULL GD9,NULL GD10,NULL GD11,NULL GD12,NULL GD13,NULL GD14,NULL GD15,NULL GD16,NULL GD17,NULL GD18,NULL GD19,NULL GD20,NULL GD21,NULL GD22,NULL GD23,NULL GD24,NULL GD25,NULL GCHECK1,NULL GCHECK2,NULL GCHECK3,NULL GCHECK4,NULL GCHECK5,NULL GCHECK6,NULL GCHECK7,NULL GCHECK8,NULL GCHECK9,NULL GCHECK10,NULL GCHECK11,NULL GCHECK12,NULL GCHECK13,NULL GCHECK14,NULL GCHECK15,NULL GCHECK16,NULL GCHECK17,NULL GCHECK18,NULL GCHECK19,NULL GCHECK20,NULL GCHECK21,NULL GCHECK22,NULL GCHECK23,NULL GCHECK24,NULL GCHECK25,NULL N1,NULL N2,NULL N3,NULL N4,NULL N5,NULL N6,NULL N7,NULL N8,NULL N9,NULL N10,NULL N11,NULL N12,NULL N13,NULL N14,NULL N15,NULL N16,NULL N17,NULL N18,NULL N19,NULL N20,NULL N21,NULL N22,NULL N23,NULL N24,NULL N25,NULL N26,NULL N27,NULL N28,NULL N29,NULL N30,NULL C1,NULL C2,NULL C3,NULL C4,NULL C5,NULL C6,NULL C7,NULL C8,NULL C9,NULL C10,NULL C11,NULL C12,NULL C13,NULL C14,NULL C15,NULL C16,NULL C17,NULL C18,NULL C19,NULL C20,NULL C21,NULL C22,NULL C23,NULL C24,NULL C25,NULL C26,NULL C27,NULL C28,NULL C29,NULL C30,NULL D1,NULL D2,NULL D3,NULL D4,NULL D5,NULL D6,NULL D7,NULL D8,NULL D9,NULL D10,NULL D11,NULL D12,NULL D13,NULL D14,NULL D15,NULL D16,NULL D17,NULL D18,NULL D19,NULL D20,NULL D21,NULL D22,NULL D23,NULL D24,NULL D25,NULL D26,NULL D27,NULL D28,NULL D29,NULL D30,NULL CHECK1,NULL CHECK2,NULL CHECK3,NULL CHECK4,NULL CHECK5,NULL CHECK6,NULL CHECK7,NULL CHECK8,NULL CHECK9,NULL CHECK10,NULL CHECK11,NULL CHECK12,NULL CHECK13,NULL CHECK14,NULL CHECK15,NULL CHECK16,NULL CHECK17,NULL CHECK18,NULL CHECK19,NULL CHECK20,NULL CHECK21,NULL CHECK22,NULL CHECK23,NULL CHECK24,NULL CHECK25,NULL CHECK26,NULL CHECK27,NULL CHECK28,NULL CHECK29,NULL CHECK30,NULL LIST1,NULL LIST2,NULL LIST3,NULL LIST4,NULL LIST5,NULL LIST6,NULL LIST7,NULL LIST8,NULL LIST9,NULL LIST10,NULL TEXTAREA1,NULL TEXTAREA2,NULL D_GC2,NULL D_GC3,NULL D_GC4,NULL D_GC5,NULL D_GC6,NULL D_GC7,NULL D_GC8,NULL D_GC9,NULL D_GC10,NULL D_GC11,NULL D_GC12,NULL D_GC13,NULL D_GC14,NULL D_GC15,NULL D_GC16,NULL D_GC17,NULL D_GC18,NULL D_GC19,NULL D_GC20,NULL D_GC21,NULL D_GC22,NULL D_GC23,NULL D_GC24,NULL D_GC25,NULL D_GN0,NULL D_GN1,NULL D_GN2,NULL D_GN3,NULL D_GN4,NULL D_GN5,NULL D_GN6,NULL D_GN7,NULL D_GN8,NULL D_GN9,NULL D_GN10,NULL D_GN11,NULL D_GN12,NULL D_GN13,NULL D_GN14,NULL D_GN15,NULL D_GN16,NULL D_GN17,NULL D_GN18,NULL D_GN19,NULL D_GN20,NULL D_GN21,NULL D_GN22,NULL D_GN23,NULL D_GN24,NULL D_GN25,NULL D_C1,NULL D_C2,NULL D_C3,NULL D_C4,NULL D_C5,NULL D_C6,NULL D_C7,NULL D_C8,NULL D_C9,NULL D_C10,NULL D_C11,NULL D_C12,NULL D_C13,NULL D_C14,NULL D_C15,NULL D_C16,NULL D_C17,NULL D_C18,NULL D_C19,NULL D_C20,NULL D_C21,NULL D_C22,NULL D_C23,NULL D_C24,NULL D_C25,NULL D_C26,NULL D_C27,NULL D_C28,NULL D_C29,NULL D_C30,NULL D_N1,NULL D_N2,NULL D_N3,NULL D_N4,NULL D_N5,NULL D_N6,NULL D_N7,NULL D_N8,NULL D_N9,NULL D_N10,NULL D_N11,NULL D_N12,NULL D_N13,NULL D_N14,NULL D_N15,NULL D_N16,NULL D_N17,NULL D_N18,NULL D_N19,NULL D_N20,NULL D_N21,NULL D_N22,NULL D_N23,NULL D_N24,NULL D_N25,NULL D_N26,NULL D_N27,NULL D_N28,NULL D_N29,NULL D_N30,NULL GN0,NULL GD0,rowid int_rowid FROM FROXA_SEGUROS_CAMBIO) FROXA_SEGUROS_CAMBIO WHERE 8=8/*INIQRY*/  order by GC2;


select PRECIO_MEDIO_PONDERADO from ARTICULOS_VALORACION where CODIGO_ARTICULO = '40764' AND CODIGO_DIVISA = 'EUR' AND CODIGO_ALMACEN = '00';







SELECT V_FECHA_PEDIDO,V_CODIGO_ARTICULO,V_CODIGO_PROVEEDOR,D_CODIGO_PROVEEDOR,V_CANTIDAD_PRESENTACION,V_CANTIDAD_PRESENTACION_ENT,V_PRESENTACION_PEDIDO,V_PRECIO_PRESENTACION,V_DTO_1,V_DTO_2,V_DTO_3,V_IMPORTE_LIN_NETO,
V_ORGANIZACION_COMPRAS,D_ORGANIZACION_COMPRAS,V_DESCRIPCION,V_USUARIO_ALTA,V_CODIGO_ALMACEN,V_CENTRO_CONTABLE,D_CODIGO_ALMACEN,D_CENTRO_CONTABLE,V_REFERENCIA_PROVEEDOR,V_CODIGO_DIVISA,V_FECHA_ENTREGA,
V_FECHA_ENTREGA_TOPE,V_FECHA_ENTREGA_CONFIRM,V_UNIDADES_PEDIDAS,V_UNIDADES_ENTREGADAS,V_UNIDADES_PEDIDAS2,V_UNIDADES_ENTREGADAS2,V_PRECIO_NETO,V_SERIE_NUMERACION,V_NUMERO_PEDIDO,V_SOLICITUD_COMPRA,
HAY_REPLICACION_VTA,NUMERO_LINEA,NUMERO_EXPEDIENTE FROM (SELECT  v.* ,(SELECT lvcc.nombre FROM caracteres_asiento lvcc WHERE lvcc.codigo = v.centro_contable AND lvcc.empresa = v.codigo_empresa) D_CENTRO_CONTABLE,
(SELECT lval.nombre FROM almacenes lval WHERE lval.almacen = v.codigo_almacen AND lval.codigo_empresa = v.codigo_empresa) D_CODIGO_ALMACEN,DECODE(v.codigo_proveedor,NULL,NULL,
(SELECT prlv.nombre FROM proveedores prlv WHERE prlv.codigo_rapido = v.codigo_proveedor AND codigo_empresa = v.codigo_empresa)) D_CODIGO_PROVEEDOR,
(SELECT lvcpr.nombre FROM organizacion_compras lvcpr WHERE lvcpr.codigo_org_compras = v.organizacion_compras AND lvcpr.codigo_empresa = v.codigo_empresa) D_ORGANIZACION_COMPRAS,pkconsgen.hay_replicacion_pedcom_vta(v.numero_pedido, v.serie_numeracion, v.organizacion_compras, v.codigo_empresa, v.numero_linea) HAY_REPLICACION_VTA,CANTIDAD_PRESENTACION V_CANTIDAD_PRESENTACION,pkconsgen.cantidad_servida_pres_ped_com(p_empresa => codigo_empresa, p_numero_pedido => numero_pedido, p_numero_serie => serie_numeracion, p_organizacion_compras => organizacion_compras, p_numero_linea => numero_linea, p_articulo => codigo_articulo, p_presentacion_pedido => presentacion_pedido, p_cantidad_presentacion => cantidad_presentacion, p_unidades_pedidas => unidades_pedidas) V_CANTIDAD_PRESENTACION_ENT,CENTRO_CONTABLE V_CENTRO_CONTABLE,CODIGO_ALMACEN V_CODIGO_ALMACEN,CODIGO_ARTICULO V_CODIGO_ARTICULO,PKCONSGEN.DIVISA(codigo_divisa) V_CODIGO_DIVISA,CODIGO_PROVEEDOR V_CODIGO_PROVEEDOR,DESCRIPCION V_DESCRIPCION,dto_1 V_DTO_1,dto_2 V_DTO_2,dto_3 V_DTO_3,FECHA_ENTREGA V_FECHA_ENTREGA,FECHA_ENTREGA_CONFIRM V_FECHA_ENTREGA_CONFIRM,FECHA_ENTREGA_TOPE V_FECHA_ENTREGA_TOPE,FECHA_PEDIDO V_FECHA_PEDIDO,PKCONSGEN.IMPORTE_TXT(importe_lin_neto, importe_lin_neto_div, codigo_divisa) V_IMPORTE_LIN_NETO,NUMERO_PEDIDO V_NUMERO_PEDIDO,ORGANIZACION_COMPRAS V_ORGANIZACION_COMPRAS,DECODE((SELECT a.unidad_precio_coste FROM articulos a WHERE a.codigo_articulo = v.codigo_articulo AND a.codigo_empresa = v.codigo_empresa), 1, DECODE(unidades_pedidas, 0, PKCONSGEN.PRECIO_TXT(0, 0, codigo_divisa), PKCONSGEN.PRECIO_TXT(importe_lin_neto / unidades_pedidas, importe_lin_neto_div / unidades_pedidas, codigo_divisa)), DECODE(NVL(unidades_pedidas2, 0), 0, PKCONSGEN.PRECIO_TXT(0, 0, codigo_divisa), PKCONSGEN.PRECIO_TXT(importe_lin_neto  / unidades_pedidas2, importe_lin_neto_div / unidades_pedidas2, codigo_divisa))) V_PRECIO_NETO,PKCONSGEN.PRECIO_TXT(DECODE(tipo_precio, 'P', precio_presentacion, precio_coste) * cambio, DECODE(tipo_precio, 'P', precio_presentacion, precio_coste), codigo_divisa) V_PRECIO_PRESENTACION,PRESENTACION_PEDIDO V_PRESENTACION_PEDIDO,REFERENCIA_PROVEEDOR V_REFERENCIA_PROVEEDOR,SERIE_NUMERACION V_SERIE_NUMERACION,UNIDADES_ENTREGADAS V_UNIDADES_ENTREGADAS,UNIDADES_ENTREGADAS2 V_UNIDADES_ENTREGADAS2,UNIDADES_PEDIDAS V_UNIDADES_PEDIDAS,UNIDADES_PEDIDAS2 V_UNIDADES_PEDIDAS2,USUARIO_ALTA V_USUARIO_ALTA,SUBSTR(pkconsgen.f_solicitud_mat_pedido_compras(codigo_empresa, organizacion_compras, numero_pedido, serie_numeracion, numero_linea), 3) V_SOLICITUD_COMPRA FROM (SELECT l.codigo_empresa, l.codigo_articulo, c.codigo_almacen, l.unidades_entregadas, l.unidades_entregadas2, l.unidades_pedidas2, l.precio_presentacion, l.precio_coste, l.tipo_precio, l.organizacion_compras, c.centro_contable, c.fecha_pedido, l.fecha_entrega, l.fecha_entrega_confirm, l.fecha_entrega_tope, l.serie_numeracion, l.numero_pedido, l.numero_linea, DECODE(PKCONSGEN.VER_PRO_BLOQUEADOS, 'S', c.codigo_proveedor, DECODE(PKCONSGEN.PROVEEDOR_BLOQUEADO(c.codigo_empresa, c.codigo_proveedor), 'S', NULL, c.codigo_proveedor)) codigo_proveedor, l.referencia_proveedor, l.unidades_pedidas, l.unidades_facturadas, l.status_cierre, l.cantidad_presentacion, l.presentacion_pedido, l.dto_1, l.dto_2, l.dto_3, l.importe_lin_neto, l.importe_lin_neto_div, c.usuario_alta, c.codigo_divisa, c.cambio, l.descripcion,c.numero_expediente  FROM pedidos_compras c, pedidos_compras_lin l WHERE c.numero_pedido = l.numero_pedido AND c.serie_numeracion = l.serie_numeracion AND c.organizacion_compras = l.organizacion_compras AND c.codigo_empresa = l.codigo_empresa ORDER BY /*PKLBOB*/c.fecha_pedido DESC/*PKLEOB*/) v)  v 
WHERE V_CODIGO_PROVEEDOR = '001089' AND codigo_empresa = '001' AND status_cierre = 'E';






SELECT V_CODIGO_ARTICULO,V_DESCRIPCION,V_CANTIDAD_PRESENTACION,V_CANTIDAD_PRESENTACION_ENT,V_PRESENTACION_PEDIDO,V_PRECIO_PRESENTACION,V_DTO_1,V_DTO_2,V_DTO_3,V_IMPORTE_LIN_NETO,V_UNIDADES_PEDIDAS,V_UNIDADES_ENTREGADAS,V_UNIDADES_PEDIDAS2,V_UNIDADES_ENTREGADAS2,V_UNIDAD_CODIGO1,V_UNIDAD_CODIGO2,V_REFERENCIA_PROVEEDOR,V_MODO_RECOGIDA,V_SOLICITUD_COMPRA,D_MODO_RECOGIDA,V_CENTRO_COSTE,D_CENTRO_COSTE,V_USUARIO_CIERRE,V_FECHA_ENTREGA,V_FECHA_ENTREGA_TOPE,V_HORA_ENTREGA,V_HORA_TOPE_ENTREGA,CODIGO_EMPRESA,ORGANIZACION_COMPRAS,SERIE_NUMERACION,NUMERO_PEDIDO,V_NUM_UNID_ALM,ID_CRM,HAY_ASOCIACION_CRM,NUMERO_LINEA,HAY_TEXTOS,HAY_REPLICACION_VTA FROM (SELECT PEDIDOS_COMPRAS_LIN.* ,DECODE(centro_coste, NULL, NULL, pkconsgen.f_descrip_centro_doc_cmp(codigo_empresa, organizacion_compras, centro_coste)) D_CENTRO_COSTE,DECODE(pedidos_compras_lin.modo_recogida,NULL,NULL,(SELECT lvmrec.descripcion FROM modos_recogida lvmrec WHERE lvmrec.codigo = pedidos_compras_lin.modo_recogida)) D_MODO_RECOGIDA,pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,pkconsgen.hay_replicacion_pedcom_vta(pedidos_compras_lin.numero_pedido, pedidos_compras_lin.serie_numeracion, pedidos_compras_lin.organizacion_compras, pedidos_compras_lin.codigo_empresa, pedidos_compras_lin.numero_linea) HAY_REPLICACION_VTA,PKCONSGEN.HAY_TEXTOS_PEDCOMPRA(numero_pedido, serie_numeracion, organizacion_compras, codigo_empresa, numero_linea) HAY_TEXTOS,CANTIDAD_PRESENTACION V_CANTIDAD_PRESENTACION,pkconsgen.cantidad_servida_pres_ped_com(p_empresa => codigo_empresa, p_numero_pedido => numero_pedido, p_numero_serie => serie_numeracion, p_organizacion_compras => organizacion_compras, p_numero_linea => numero_linea, p_articulo => codigo_articulo, p_presentacion_pedido => presentacion_pedido, p_cantidad_presentacion => cantidad_presentacion, p_unidades_pedidas => unidades_pedidas) V_CANTIDAD_PRESENTACION_ENT,CENTRO_COSTE V_CENTRO_COSTE,CODIGO_ARTICULO V_CODIGO_ARTICULO,COALESCE(pedidos_compras_lin.descripcion,(SELECT a.descrip_comercial FROM articulos a WHERE a.codigo_articulo=pedidos_compras_lin.codigo_articulo AND a.codigo_empresa=pedidos_compras_lin.codigo_empresa)) V_DESCRIPCION,DTO_1 V_DTO_1,DTO_2 V_DTO_2,DTO_3 V_DTO_3,FECHA_ENTREGA V_FECHA_ENTREGA,FECHA_ENTREGA_TOPE V_FECHA_ENTREGA_TOPE,HORA_ENTREGA V_HORA_ENTREGA,HORA_TOPE_ENTREGA V_HORA_TOPE_ENTREGA,PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div,pkconsgen.f_get_divisa_pedcomp(pedidos_compras_lin.codigo_empresa, pedidos_compras_lin.numero_pedido, pedidos_compras_lin.serie_numeracion, pedidos_compras_lin.organizacion_compras)) V_IMPORTE_LIN_NETO,MODO_RECOGIDA V_MODO_RECOGIDA,(SELECT a.num_unid_alm FROM articulos a WHERE a.codigo_articulo = pedidos_compras_lin.codigo_articulo AND a.codigo_empresa = pedidos_compras_lin.codigo_empresa) V_NUM_UNID_ALM,PKCONSGEN.PRECIO(precio_presentacion * pkconsgen.f_get_valor_cambio_pedcomp(pedidos_compras_lin.codigo_empresa, pedidos_compras_lin.numero_pedido, pedidos_compras_lin.serie_numeracion, pedidos_compras_lin.organizacion_compras), precio_presentacion, pkconsgen.f_get_divisa_pedcomp(pedidos_compras_lin.codigo_empresa, pedidos_compras_lin.numero_pedido, pedidos_compras_lin.serie_numeracion, pedidos_compras_lin.organizacion_compras)) V_PRECIO_PRESENTACION,PRESENTACION_PEDIDO V_PRESENTACION_PEDIDO,REFERENCIA_PROVEEDOR V_REFERENCIA_PROVEEDOR,SUBSTR(pkconsgen.f_solicitud_mat_pedido_compras(codigo_empresa, organizacion_compras, numero_pedido, serie_numeracion, numero_linea), 3) V_SOLICITUD_COMPRA,UNIDADES_ENTREGADAS V_UNIDADES_ENTREGADAS,UNIDADES_ENTREGADAS2 V_UNIDADES_ENTREGADAS2,UNIDADES_PEDIDAS V_UNIDADES_PEDIDAS,UNIDADES_PEDIDAS2 V_UNIDADES_PEDIDAS2,(SELECT a.unidad_codigo1 FROM articulos a WHERE a.codigo_articulo = pedidos_compras_lin.codigo_articulo AND a.codigo_empresa = pedidos_compras_lin.codigo_empresa) V_UNIDAD_CODIGO1,(SELECT a.unidad_codigo2 FROM articulos a WHERE a.codigo_articulo = pedidos_compras_lin.codigo_articulo AND a.codigo_empresa = pedidos_compras_lin.codigo_empresa) V_UNIDAD_CODIGO2,usuario_cierre V_USUARIO_CIERRE FROM PEDIDOS_COMPRAS_LIN) PEDIDOS_COMPRAS_LIN WHERE (CODIGO_EMPRESA='001') and (ORGANIZACION_COMPRAS='02') and (SERIE_NUMERACION='02') and (NUMERO_PEDIDO='17');






SELECT
  pc.numero_pedido,
  pc.fecha_pedido,
  pc.organizacion_compras,
  pc.codigo_proveedor,
  pc.codigo_divisa,
  pc.importe_total_pedido,
  pcl.numero_linea,
  pcl.codigo_articulo,
  pcl.descripcion AS descripcion_articulo,
  pcl.unidades_pedidas,
  pcl.unidades_entregadas,
  pcl.precio_presentacion,
  pcl.importe_lin_neto
FROM
  pedidos_compras pc
JOIN
  pedidos_compras_lin pcl
  ON pc.numero_pedido = pcl.numero_pedido
  AND pc.serie_numeracion = pcl.serie_numeracion
  AND pc.organizacion_compras = pcl.organizacion_compras
  AND pc.codigo_empresa = pcl.codigo_empresa
WHERE
  pc.codigo_empresa = '001'
  AND pc.codigo_proveedor = '001089'
  AND pc.status_cierre = 'E'
ORDER BY
  pc.fecha_pedido DESC, pcl.numero_linea;
