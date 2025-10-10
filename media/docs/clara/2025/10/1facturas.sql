select v_numero_expediente, v_fecha_factura,
       v_numero_factura,
       v_tipo_factura,
       v_organizacion_compras,
       d_organizacion_compras,
       v_centro_contable,
       d_centro_contable,
       hay_archivos_x_id_digital,
       v_forma_pago,
       d_forma_pago,
       v_neto_factura,
       v_liquido_factura,
       v_pendiente_pago,
       v_codigo_divisa,
       v_usuario,
       d_tipo_factura,
       d_banco_asegurador,
       v_valor_cambio,
       v_codigo_proveedor,
       d_codigo_proveedor,
       v_dto_1,
       v_dto_2,
       v_dto_3,
       v_dto_ppago,
       v_dto_5,
       v_dto_6,
       v_recargo_financiero,
       v_recargo_2,
       id_digital,
       v_recargo_3,
       v_imp_fac_dto1,
       v_imp_fac_dto2,
       v_imp_fac_dto3,
       v_imp_fac_dtoppago,
       v_imp_fac_dto5,
       v_imp_fac_dto6,
       v_imp_rcgo_financiero,
       v_imp_recargo_2,
       v_imp_recargo_3,
       ejercicio,
       codigo_proveedor,
       tipo_factura,
       codigo_empresa,
       numero_asiento_borrador,
       fecha_asiento,
       id_crm,
       numero_registro,
       hay_asociacion_crm,
       hay_archivos
  from (
   select facturas_compras_cab.*,
          decode(
             facturas_compras_cab.banco_asegurador,
             null,
             null,
             (
                select lvba.nombre
                  from bancos lvba
                 where lvba.codigo_rapido = facturas_compras_cab.banco_asegurador
                   and lvba.empresa = facturas_compras_cab.codigo_empresa
             )
          ) d_banco_asegurador,
          (
             select lvcc.nombre
               from caracteres_asiento lvcc
              where lvcc.codigo = facturas_compras_cab.centro_contable
                and lvcc.empresa = facturas_compras_cab.codigo_empresa
          ) d_centro_contable,
          (
             select prlv.nombre
               from proveedores prlv
              where prlv.codigo_rapido = facturas_compras_cab.codigo_proveedor
                and codigo_empresa = facturas_compras_cab.codigo_empresa
          ) d_codigo_proveedor,
          (
             select lvfcp.nombre
               from formas_cobro_pago lvfcp
              where lvfcp.codigo = facturas_compras_cab.forma_pago
          ) d_forma_pago,
          (
             select lvcpr.nombre
               from organizacion_compras lvcpr
              where lvcpr.codigo_org_compras = facturas_compras_cab.organizacion_compras
                and lvcpr.codigo_empresa = facturas_compras_cab.codigo_empresa
          ) d_organizacion_compras,
          (
             select lvtfc.descripcion
               from tipos_facturas_comp lvtfc
              where lvtfc.codigo = facturas_compras_cab.tipo_factura
                and lvtfc.tipo_documento = 'STD'
          ) d_tipo_factura,
          pkconsgen.fc_hay_archivos(
             codigo_empresa,
             numero_factura,
             ejercicio,
             codigo_proveedor,
             organizacion_compras,
             numero_registro
          ) hay_archivos,
          pkconsgen.hay_archivos_x_id_digital(
             facturas_compras_cab.id_digital,
             'FACTURAS_COMPRAS_CAB'
          ) hay_archivos_x_id_digital,
          pkconsgen.hay_asociacion_crm(
             codigo_empresa,
             id_crm
          ) hay_asociacion_crm,
          centro_contable v_centro_contable,
          pkconsgen.divisa(codigo_divisa) v_codigo_divisa,
          codigo_proveedor v_codigo_proveedor,
          dto_1 v_dto_1,
          dto_2 v_dto_2,
          dto_3 v_dto_3,
          dto_5 v_dto_5,
          dto_6 v_dto_6,
          dto_ppago v_dto_ppago,
          fecha_factura v_fecha_factura,
          forma_pago v_forma_pago,
          pkconsgen.importe(
             imp_fac_dto1,
             imp_fac_dto1_div,
             codigo_divisa
          ) v_imp_fac_dto1,
          pkconsgen.importe(
             imp_fac_dto2,
             imp_fac_dto2_div,
             codigo_divisa
          ) v_imp_fac_dto2,
          pkconsgen.importe(
             imp_fac_dto3,
             imp_fac_dto3_div,
             codigo_divisa
          ) v_imp_fac_dto3,
          pkconsgen.importe(
             imp_fac_dto5,
             imp_fac_dto5_div,
             codigo_divisa
          ) v_imp_fac_dto5,
          pkconsgen.importe(
             imp_fac_dto6,
             imp_fac_dto6_div,
             codigo_divisa
          ) v_imp_fac_dto6,
          pkconsgen.importe(
             imp_fac_dtoppago,
             imp_fac_dtoppago_div,
             codigo_divisa
          ) v_imp_fac_dtoppago,
          pkconsgen.importe(
             imp_rcgo_financiero,
             imp_rcgo_financiero_div,
             codigo_divisa
          ) v_imp_rcgo_financiero,
          pkconsgen.importe(
             imp_recargo_2,
             imp_recargo_2_div,
             codigo_divisa
          ) v_imp_recargo_2,
          pkconsgen.importe(
             imp_recargo_3,
             imp_recargo_3_div,
             codigo_divisa
          ) v_imp_recargo_3,
          pkconsgen.importe_txt(
             liquido_factura,
             liquido_factura_div,
             codigo_divisa
          ) v_liquido_factura,
          pkconsgen.importe_txt(
             importe_fac_neto,
             importe_fac_neto_div,
             codigo_divisa
          ) v_neto_factura,
          numero_expediente v_numero_expediente,
          numero_factura v_numero_factura,
          organizacion_compras v_organizacion_compras,
          decode(
             numero_asiento_borrador,
             null,
             pkconsgen.importe_txt(
                liquido_factura,
                liquido_factura_div,
                codigo_divisa
             ),
             pkconsgen.importe_pdte_pago_doc_txt(
                codigo_empresa,
                numero_factura,
                fecha_factura,
                codigo_proveedor,
                codigo_divisa,
                liquido_factura,
                liquido_factura_div
             )
          ) v_pendiente_pago,
          recargo_2 v_recargo_2,
          recargo_3 v_recargo_3,
          recargo_financiero v_recargo_financiero,
          tipo_factura v_tipo_factura,
          usuario v_usuario,
          valor_cambio v_valor_cambio
     from facturas_compras_cab
) facturas_compras_cab
 where codigo_proveedor != '001101'
   and codigo_empresa = '001'
 order by fecha_factura desc;




--- datos de la factura que necesito
SELECT 
   V_NUMERO_EXPEDIENTE,
   CODIGO_PROVEEDOR,
   V_CODIGO_PROVEEDOR,
   D_CODIGO_PROVEEDOR, 
   V_FECHA_FACTURA,
   V_NUMERO_FACTURA,
   V_TIPO_FACTURA,
   V_NETO_FACTURA,
   V_LIQUIDO_FACTURA,
   V_PENDIENTE_PAGO,
   V_CODIGO_DIVISA,
   V_VALOR_CAMBIO,
   EJERCICIO,
   NUMERO_REGISTRO
FROM (SELECT FACTURAS_COMPRAS_CAB.* ,DECODE(facturas_compras_cab.banco_asegurador,NULL,NULL,(SELECT lvba.nombre FROM bancos lvba WHERE lvba.codigo_rapido = facturas_compras_cab.banco_asegurador AND lvba.empresa = facturas_compras_cab.codigo_empresa)) D_BANCO_ASEGURADOR,(SELECT lvcc.nombre FROM caracteres_asiento lvcc WHERE lvcc.codigo = facturas_compras_cab.centro_contable AND lvcc.empresa = facturas_compras_cab.codigo_empresa) D_CENTRO_CONTABLE,(SELECT prlv.nombre FROM proveedores prlv WHERE prlv.codigo_rapido = facturas_compras_cab.codigo_proveedor AND codigo_empresa = facturas_compras_cab.codigo_empresa) D_CODIGO_PROVEEDOR,(SELECT lvfcp.nombre FROM formas_cobro_pago lvfcp WHERE lvfcp.codigo = facturas_compras_cab.forma_pago) D_FORMA_PAGO,(SELECT lvcpr.nombre FROM organizacion_compras lvcpr WHERE lvcpr.codigo_org_compras = facturas_compras_cab.organizacion_compras AND lvcpr.codigo_empresa = facturas_compras_cab.codigo_empresa) D_ORGANIZACION_COMPRAS,(SELECT lvtfc.descripcion FROM tipos_facturas_comp lvtfc WHERE lvtfc.codigo = facturas_compras_cab.tipo_factura AND lvtfc.tipo_documento = 'STD') D_TIPO_FACTURA,pkconsgen.fc_hay_archivos(codigo_empresa, numero_factura, ejercicio, codigo_proveedor, organizacion_compras, numero_registro) HAY_ARCHIVOS,pkconsgen.hay_archivos_x_id_digital(facturas_compras_cab.ID_DIGITAL, 'FACTURAS_COMPRAS_CAB') HAY_ARCHIVOS_X_ID_DIGITAL,pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,CENTRO_CONTABLE V_CENTRO_CONTABLE,PKCONSGEN.DIVISA(codigo_divisa) V_CODIGO_DIVISA,codigo_proveedor V_CODIGO_PROVEEDOR,DTO_1 V_DTO_1,DTO_2 V_DTO_2,DTO_3 V_DTO_3,DTO_5 V_DTO_5,DTO_6 V_DTO_6,DTO_PPAGO V_DTO_PPAGO,FECHA_FACTURA V_FECHA_FACTURA,FORMA_PAGO V_FORMA_PAGO,PKCONSGEN.IMPORTE(imp_fac_dto1, imp_fac_dto1_div, codigo_divisa) V_IMP_FAC_DTO1,PKCONSGEN.IMPORTE(imp_fac_dto2, imp_fac_dto2_div, codigo_divisa) V_IMP_FAC_DTO2,PKCONSGEN.IMPORTE(imp_fac_dto3, imp_fac_dto3_div, codigo_divisa) V_IMP_FAC_DTO3,PKCONSGEN.IMPORTE(imp_fac_dto5, imp_fac_dto5_div, codigo_divisa) V_IMP_FAC_DTO5,PKCONSGEN.IMPORTE(imp_fac_dto6, imp_fac_dto6_div, codigo_divisa) V_IMP_FAC_DTO6,PKCONSGEN.IMPORTE(imp_fac_dtoppago, imp_fac_dtoppago_div, codigo_divisa) V_IMP_FAC_DTOPPAGO,PKCONSGEN.IMPORTE(imp_rcgo_financiero, imp_rcgo_financiero_div, codigo_divisa) V_IMP_RCGO_FINANCIERO,PKCONSGEN.IMPORTE(imp_recargo_2, imp_recargo_2_div, codigo_divisa) V_IMP_RECARGO_2,PKCONSGEN.IMPORTE(imp_recargo_3, imp_recargo_3_div, codigo_divisa) V_IMP_RECARGO_3,PKCONSGEN.IMPORTE_TXT(liquido_factura, liquido_factura_div, codigo_divisa) V_LIQUIDO_FACTURA,PKCONSGEN.IMPORTE_TXT(importe_fac_neto, importe_fac_neto_div, codigo_divisa) V_NETO_FACTURA,numero_expediente V_NUMERO_EXPEDIENTE,NUMERO_FACTURA V_NUMERO_FACTURA,ORGANIZACION_COMPRAS V_ORGANIZACION_COMPRAS,DECODE(numero_asiento_borrador, NULL, PKCONSGEN.IMPORTE_TXT(liquido_factura, liquido_factura_div, codigo_divisa), PKCONSGEN.IMPORTE_PDTE_PAGO_DOC_TXT(codigo_empresa, numero_factura, fecha_factura, codigo_proveedor, codigo_divisa, liquido_factura, liquido_factura_div)) V_PENDIENTE_PAGO,RECARGO_2 V_RECARGO_2,RECARGO_3 V_RECARGO_3,RECARGO_FINANCIERO V_RECARGO_FINANCIERO,TIPO_FACTURA V_TIPO_FACTURA,USUARIO V_USUARIO,VALOR_CAMBIO V_VALOR_CAMBIO FROM FACTURAS_COMPRAS_CAB) FACTURAS_COMPRAS_CAB 
WHERE codigo_proveedor = '000240' AND codigo_empresa = '001'  order by fecha_factura DESC;


-- lineas factura de alli tenemos el albaran y la factura
SELECT 
   V_NUMERO_EXPEDIENTE,
   V_CANTIDAD_FACTURADA,
   V_PRESENTACION,
   V_PRECIO_PRESENTACION,
   V_PRECIO_NETO,
   V_IMPORTE_NETO,
   V_NUM_ALBARAN_INT,
   V_NUM_ALBARAN_EXT,
   V_LINEA_ALBARAN,
   NUMERO_FACTURA,
   NUMERO_LINEA 
   FROM (SELECT FACTURAS_COMPRAS_LIN.* ,DECODE(facturas_compras_lin.centro_coste,NULL,NULL,(SELECT lvcencos.nombre FROM centros_coste lvcencos WHERE lvcencos.codigo = facturas_compras_lin.centro_coste AND lvcencos.empresa = facturas_compras_lin.codigo_empresa)) D_CENTRO_COSTE,pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,pkconsgen.hay_replicacion_com_vta(facturas_compras_lin.num_albaran_int, facturas_compras_lin.codigo_empresa, facturas_compras_lin.linea_albaran) HAY_REPLICACION_VTA,CANTIDAD_FACTURADA V_CANTIDAD_FACTURADA,CENTRO_COSTE V_CENTRO_COSTE,CODIGO_ARTICULO V_CODIGO_ARTICULO,COALESCE((SELECT a.descripcion FROM albaran_compras_l a WHERE a.numero_doc_interno = facturas_compras_lin.num_albaran_int AND a.numero_linea = facturas_compras_lin.linea_albaran AND a.codigo_empresa = facturas_compras_lin.codigo_empresa), (SELECT a.descrip_comercial FROM articulos a WHERE a.codigo_articulo = facturas_compras_lin.codigo_articulo AND a.codigo_empresa = facturas_compras_lin.codigo_empresa)) V_DESCRIPCION_ARTICULO,dto_1 V_DTO_1,dto_2 V_DTO_2,dto_3 V_DTO_3,PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) V_IMPORTE_NETO,LINEA_ALBARAN V_LINEA_ALBARAN,(SELECT al.expediente_importacion FROM albaran_compras_l al WHERE al.numero_doc_interno = facturas_compras_lin.num_albaran_int AND al.numero_linea = facturas_compras_lin.numero_linea AND al.codigo_empresa = facturas_compras_lin.codigo_empresa) V_NUMERO_EXPEDIENTE,(SELECT c.numero_doc_ext FROM albaran_compras_c c WHERE c.numero_doc_interno = facturas_compras_lin.num_albaran_int AND c.codigo_empresa = facturas_compras_lin.codigo_empresa) V_NUM_ALBARAN_EXT,NUM_ALBARAN_INT V_NUM_ALBARAN_INT,DECODE((SELECT a.unidad_precio_coste FROM articulos a WHERE a.codigo_articulo = facturas_compras_lin.codigo_articulo AND a.codigo_empresa = facturas_compras_lin.codigo_empresa), 1, DECODE(unidades_facturadas, 0, 0, PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) / unidades_facturadas),  DECODE(unidades_facturadas2, 0, 0, PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) / unidades_facturadas2)) V_PRECIO_NETO,PKCONSGEN.PRECIO(precio_presentacion * pkconsgen.f_get_valor_cambio_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura), precio_presentacion, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) V_PRECIO_PRESENTACION,PRESENTACION V_PRESENTACION,facturas_compras_lin.tipo_factura V_TIPO_FACTURA,UNIDADES_FACTURADAS V_UNIDADES_FACTURADAS,UNIDADES_FACTURADAS2 V_UNIDADES_FACTURADAS2 FROM FACTURAS_COMPRAS_LIN) FACTURAS_COMPRAS_LIN 
   WHERE (CODIGO_EMPRESA='001') and (CODIGO_PROVEEDOR='000240') and (EJERCICIO='2025') and (NUMERO_FACTURA='16964/XK/2025');

-- desde lineas busco ID de la factura
SELECT 
   distinct NUMERO_FACTURA
   FROM (SELECT FACTURAS_COMPRAS_LIN.* ,DECODE(facturas_compras_lin.centro_coste,NULL,NULL,(SELECT lvcencos.nombre FROM centros_coste lvcencos WHERE lvcencos.codigo = facturas_compras_lin.centro_coste AND lvcencos.empresa = facturas_compras_lin.codigo_empresa)) D_CENTRO_COSTE,pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,pkconsgen.hay_replicacion_com_vta(facturas_compras_lin.num_albaran_int, facturas_compras_lin.codigo_empresa, facturas_compras_lin.linea_albaran) HAY_REPLICACION_VTA,CANTIDAD_FACTURADA V_CANTIDAD_FACTURADA,CENTRO_COSTE V_CENTRO_COSTE,CODIGO_ARTICULO V_CODIGO_ARTICULO,COALESCE((SELECT a.descripcion FROM albaran_compras_l a WHERE a.numero_doc_interno = facturas_compras_lin.num_albaran_int AND a.numero_linea = facturas_compras_lin.linea_albaran AND a.codigo_empresa = facturas_compras_lin.codigo_empresa), (SELECT a.descrip_comercial FROM articulos a WHERE a.codigo_articulo = facturas_compras_lin.codigo_articulo AND a.codigo_empresa = facturas_compras_lin.codigo_empresa)) V_DESCRIPCION_ARTICULO,dto_1 V_DTO_1,dto_2 V_DTO_2,dto_3 V_DTO_3,PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) V_IMPORTE_NETO,LINEA_ALBARAN V_LINEA_ALBARAN,(SELECT al.expediente_importacion FROM albaran_compras_l al WHERE al.numero_doc_interno = facturas_compras_lin.num_albaran_int AND al.numero_linea = facturas_compras_lin.numero_linea AND al.codigo_empresa = facturas_compras_lin.codigo_empresa) V_NUMERO_EXPEDIENTE,(SELECT c.numero_doc_ext FROM albaran_compras_c c WHERE c.numero_doc_interno = facturas_compras_lin.num_albaran_int AND c.codigo_empresa = facturas_compras_lin.codigo_empresa) V_NUM_ALBARAN_EXT,NUM_ALBARAN_INT V_NUM_ALBARAN_INT,DECODE((SELECT a.unidad_precio_coste FROM articulos a WHERE a.codigo_articulo = facturas_compras_lin.codigo_articulo AND a.codigo_empresa = facturas_compras_lin.codigo_empresa), 1, DECODE(unidades_facturadas, 0, 0, PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) / unidades_facturadas),  DECODE(unidades_facturadas2, 0, 0, PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) / unidades_facturadas2)) V_PRECIO_NETO,PKCONSGEN.PRECIO(precio_presentacion * pkconsgen.f_get_valor_cambio_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura), precio_presentacion, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) V_PRECIO_PRESENTACION,PRESENTACION V_PRESENTACION,facturas_compras_lin.tipo_factura V_TIPO_FACTURA,UNIDADES_FACTURADAS V_UNIDADES_FACTURADAS,UNIDADES_FACTURADAS2 V_UNIDADES_FACTURADAS2 FROM FACTURAS_COMPRAS_LIN) FACTURAS_COMPRAS_LIN 
   WHERE (CODIGO_EMPRESA='001') and (CODIGO_PROVEEDOR='000240') and (EJERCICIO='2025') and (   V_NUMERO_EXPEDIENTE='79');





SELECT 
   distinct NUMERO_FACTURA
            FROM (SELECT FACTURAS_COMPRAS_LIN.* ,DECODE(facturas_compras_lin.centro_coste,NULL,NULL,(SELECT lvcencos.nombre FROM centros_coste lvcencos WHERE lvcencos.codigo = facturas_compras_lin.centro_coste AND lvcencos.empresa = facturas_compras_lin.codigo_empresa)) D_CENTRO_COSTE,pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,pkconsgen.hay_replicacion_com_vta(facturas_compras_lin.num_albaran_int, facturas_compras_lin.codigo_empresa, facturas_compras_lin.linea_albaran) HAY_REPLICACION_VTA,CANTIDAD_FACTURADA V_CANTIDAD_FACTURADA,CENTRO_COSTE V_CENTRO_COSTE,CODIGO_ARTICULO V_CODIGO_ARTICULO,COALESCE((SELECT a.descripcion FROM albaran_compras_l a WHERE a.numero_doc_interno = facturas_compras_lin.num_albaran_int AND a.numero_linea = facturas_compras_lin.linea_albaran AND a.codigo_empresa = facturas_compras_lin.codigo_empresa), (SELECT a.descrip_comercial FROM articulos a WHERE a.codigo_articulo = facturas_compras_lin.codigo_articulo AND a.codigo_empresa = facturas_compras_lin.codigo_empresa)) V_DESCRIPCION_ARTICULO,dto_1 V_DTO_1,dto_2 V_DTO_2,dto_3 V_DTO_3,PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) V_IMPORTE_NETO,LINEA_ALBARAN V_LINEA_ALBARAN,(SELECT al.expediente_importacion FROM albaran_compras_l al WHERE al.numero_doc_interno = facturas_compras_lin.num_albaran_int AND al.numero_linea = facturas_compras_lin.numero_linea AND al.codigo_empresa = facturas_compras_lin.codigo_empresa) V_NUMERO_EXPEDIENTE,(SELECT c.numero_doc_ext FROM albaran_compras_c c WHERE c.numero_doc_interno = facturas_compras_lin.num_albaran_int AND c.codigo_empresa = facturas_compras_lin.codigo_empresa) V_NUM_ALBARAN_EXT,NUM_ALBARAN_INT V_NUM_ALBARAN_INT,DECODE((SELECT a.unidad_precio_coste FROM articulos a WHERE a.codigo_articulo = facturas_compras_lin.codigo_articulo AND a.codigo_empresa = facturas_compras_lin.codigo_empresa), 1, DECODE(unidades_facturadas, 0, 0, PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) / unidades_facturadas),  DECODE(unidades_facturadas2, 0, 0, PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) / unidades_facturadas2)) V_PRECIO_NETO,PKCONSGEN.PRECIO(precio_presentacion * pkconsgen.f_get_valor_cambio_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura), precio_presentacion, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) V_PRECIO_PRESENTACION,PRESENTACION V_PRESENTACION,facturas_compras_lin.tipo_factura V_TIPO_FACTURA,UNIDADES_FACTURADAS V_UNIDADES_FACTURADAS,UNIDADES_FACTURADAS2 V_UNIDADES_FACTURADAS2 FROM FACTURAS_COMPRAS_LIN) FACTURAS_COMPRAS_LIN 
            WHERE V_NUMERO_EXPEDIENTE= '25';

SELECT V_FECHA_FACTURA,
   V_NUMERO_FACTURA,
   V_NETO_FACTURA,
   V_LIQUIDO_FACTURA,
   V_PENDIENTE_PAGO,
   V_CODIGO_DIVISA,
   V_VALOR_CAMBIO,
   V_CODIGO_PROVEEDOR,
   D_CODIGO_PROVEEDOR,
   EJERCICIO,
   CODIGO_PROVEEDOR
   FROM (SELECT FACTURAS_COMPRAS_CAB.* ,DECODE(facturas_compras_cab.banco_asegurador,NULL,NULL,(SELECT lvba.nombre FROM bancos lvba WHERE lvba.codigo_rapido = facturas_compras_cab.banco_asegurador AND lvba.empresa = facturas_compras_cab.codigo_empresa)) D_BANCO_ASEGURADOR,(SELECT lvcc.nombre FROM caracteres_asiento lvcc WHERE lvcc.codigo = facturas_compras_cab.centro_contable AND lvcc.empresa = facturas_compras_cab.codigo_empresa) D_CENTRO_CONTABLE,(SELECT prlv.nombre FROM proveedores prlv WHERE prlv.codigo_rapido = facturas_compras_cab.codigo_proveedor AND codigo_empresa = facturas_compras_cab.codigo_empresa) D_CODIGO_PROVEEDOR,(SELECT lvfcp.nombre FROM formas_cobro_pago lvfcp WHERE lvfcp.codigo = facturas_compras_cab.forma_pago) D_FORMA_PAGO,(SELECT lvcpr.nombre FROM organizacion_compras lvcpr WHERE lvcpr.codigo_org_compras = facturas_compras_cab.organizacion_compras AND lvcpr.codigo_empresa = facturas_compras_cab.codigo_empresa) D_ORGANIZACION_COMPRAS,(SELECT lvtfc.descripcion FROM tipos_facturas_comp lvtfc WHERE lvtfc.codigo = facturas_compras_cab.tipo_factura AND lvtfc.tipo_documento = 'STD') D_TIPO_FACTURA,pkconsgen.fc_hay_archivos(codigo_empresa, numero_factura, ejercicio, codigo_proveedor, organizacion_compras, numero_registro) HAY_ARCHIVOS,pkconsgen.hay_archivos_x_id_digital(facturas_compras_cab.ID_DIGITAL, 'FACTURAS_COMPRAS_CAB') HAY_ARCHIVOS_X_ID_DIGITAL,pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,CENTRO_CONTABLE V_CENTRO_CONTABLE,PKCONSGEN.DIVISA(codigo_divisa) V_CODIGO_DIVISA,codigo_proveedor V_CODIGO_PROVEEDOR,DTO_1 V_DTO_1,DTO_2 V_DTO_2,DTO_3 V_DTO_3,DTO_5 V_DTO_5,DTO_6 V_DTO_6,DTO_PPAGO V_DTO_PPAGO,FECHA_FACTURA V_FECHA_FACTURA,FORMA_PAGO V_FORMA_PAGO,PKCONSGEN.IMPORTE(imp_fac_dto1, imp_fac_dto1_div, codigo_divisa) V_IMP_FAC_DTO1,PKCONSGEN.IMPORTE(imp_fac_dto2, imp_fac_dto2_div, codigo_divisa) V_IMP_FAC_DTO2,PKCONSGEN.IMPORTE(imp_fac_dto3, imp_fac_dto3_div, codigo_divisa) V_IMP_FAC_DTO3,PKCONSGEN.IMPORTE(imp_fac_dto5, imp_fac_dto5_div, codigo_divisa) V_IMP_FAC_DTO5,PKCONSGEN.IMPORTE(imp_fac_dto6, imp_fac_dto6_div, codigo_divisa) V_IMP_FAC_DTO6,PKCONSGEN.IMPORTE(imp_fac_dtoppago, imp_fac_dtoppago_div, codigo_divisa) V_IMP_FAC_DTOPPAGO,PKCONSGEN.IMPORTE(imp_rcgo_financiero, imp_rcgo_financiero_div, codigo_divisa) V_IMP_RCGO_FINANCIERO,PKCONSGEN.IMPORTE(imp_recargo_2, imp_recargo_2_div, codigo_divisa) V_IMP_RECARGO_2,PKCONSGEN.IMPORTE(imp_recargo_3, imp_recargo_3_div, codigo_divisa) V_IMP_RECARGO_3,PKCONSGEN.IMPORTE_TXT(liquido_factura, liquido_factura_div, codigo_divisa) V_LIQUIDO_FACTURA,PKCONSGEN.IMPORTE_TXT(importe_fac_neto, importe_fac_neto_div, codigo_divisa) V_NETO_FACTURA,numero_expediente V_NUMERO_EXPEDIENTE,NUMERO_FACTURA V_NUMERO_FACTURA,ORGANIZACION_COMPRAS V_ORGANIZACION_COMPRAS,DECODE(numero_asiento_borrador, NULL, PKCONSGEN.IMPORTE_TXT(liquido_factura, liquido_factura_div, codigo_divisa), PKCONSGEN.IMPORTE_PDTE_PAGO_DOC_TXT(codigo_empresa, numero_factura, fecha_factura, codigo_proveedor, codigo_divisa, liquido_factura, liquido_factura_div)) V_PENDIENTE_PAGO,RECARGO_2 V_RECARGO_2,RECARGO_3 V_RECARGO_3,RECARGO_FINANCIERO V_RECARGO_FINANCIERO,TIPO_FACTURA V_TIPO_FACTURA,USUARIO V_USUARIO,VALOR_CAMBIO V_VALOR_CAMBIO FROM FACTURAS_COMPRAS_CAB) FACTURAS_COMPRAS_CAB 
   WHERE codigo_proveedor = '001119' AND V_NUMERO_FACTURA = '00024297'  order by fecha_factura DESC;


select nombre from proveedores where codigo_rapido = '001119';


 productos ajenos y subfamilia precocinados ajenos

013 PRODUCTOS AJENOS 029 PRECOCINADOS AJENOS
   nombre común:
                                          400 QUESO CREMA JALAPEÑOS
      queso camembert                     404 QUESO CAMEMBERT
      queso cabra y cebolla caramelizada  405 QUESO CABRA Y CEBOLLA CARAMELIZADA

   presentación:                          190 AROS
      patata                              195 PATATA