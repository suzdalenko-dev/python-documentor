from datetime import datetime
import json, re

def get_albaran_pendiente_de_facturar(oracle, expediente_codigo, cambios_diario, cambios_mes):
    sql_alb = """SELECT V_FECHA,
             V_NUMERO_DOC_EXT,
             V_NUMERO_DOC_INTERNO,
             V_CODIGO_ALMACEN,
             D_CODIGO_ALMACEN,
             V_IMPORTE_TOTAL_ALBARAN,
             V_DIVISA,
             NUMERO_DOC_INTERNO,
             V_NUMERO_EXPEDIENTE,
             V_HOJA_SEGUIMIENTO
             FROM (SELECT ALBARAN_COMPRAS_C.* ,(SELECT lvcc.nombre FROM caracteres_asiento lvcc WHERE lvcc.codigo = albaran_compras_c.centro_contable AND lvcc.empresa = albaran_compras_c.codigo_empresa) D_CENTRO_CONTABLE,(SELECT lval.nombre FROM almacenes lval WHERE lval.almacen = albaran_compras_c.codigo_almacen AND lval.codigo_empresa = albaran_compras_c.codigo_empresa) D_CODIGO_ALMACEN,(SELECT lvcpr.nombre FROM organizacion_compras lvcpr WHERE lvcpr.codigo_org_compras = albaran_compras_c.organizacion_compras AND lvcpr.codigo_empresa = albaran_compras_c.codigo_empresa) D_ORGANIZACION_COMPRAS,(SELECT lvtppco.descripcion FROM tipos_pedido_com lvtppco WHERE lvtppco.tipo_pedido = albaran_compras_c.tipo_pedido_com AND lvtppco.organizacion_compras = albaran_compras_c.organizacion_compras AND lvtppco.codigo_empresa = albaran_compras_c.codigo_empresa) D_TIPO_PEDIDO_COM,pkconsgen.ac_hay_archivos(codigo_empresa, numero_doc_interno) HAY_ARCHIVOS,pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,pkconsgen.hay_replicacion_com_vta(albaran_compras_c.numero_doc_interno, albaran_compras_c.codigo_empresa, NULL) HAY_REPLICACION_VTA,CENTRO_CONTABLE V_CENTRO_CONTABLE,CODIGO_ALMACEN V_CODIGO_ALMACEN,contador_gestion V_CONTADOR_GESTION,DECODE(deposito_proveedor, 'S', 'S', 'N', 'N', 'D', 'D', 'N') V_DEPOSITO,PKCONSGEN.DIVISA(PKCONSGEN.DIVISA_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno)) V_DIVISA,FECHA V_FECHA,fecha_asiento V_FECHA_ASIENTO,HOJA_SEGUIMIENTO V_HOJA_SEGUIMIENTO,PKCONSGEN.IMPORTE_TXT(PKCONSGEN.IMPORTE_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno, 'N'), PKCONSGEN.IMPORTE_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno, 'S'), PKCONSGEN.DIVISA_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno),PKCONSGEN.IMPORTE_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno, '2')) V_IMPORTE_TOTAL_ALBARAN,numero_asiento_borrador V_NUMERO_ASIENTO_BORRADOR,NUMERO_DOC_EXT V_NUMERO_DOC_EXT,NUMERO_DOC_INTERNO V_NUMERO_DOC_INTERNO,NUMERO_EXPEDIENTE V_NUMERO_EXPEDIENTE,ORGANIZACION_COMPRAS V_ORGANIZACION_COMPRAS,TIPO_PEDIDO_COM V_TIPO_PEDIDO_COM,USUARIO V_USUARIO FROM ALBARAN_COMPRAS_C) ALBARAN_COMPRAS_C 
             WHERE V_NUMERO_EXPEDIENTE = :expediente_codigo  AND codigo_empresa = '001' AND NVL(deposito_proveedor, 'N') != 'S' AND facturado = 'N' AND interno = 'N'  order by FECHA DESC"""

    rows_alb =  oracle.consult(sql_alb, {'expediente_codigo': expediente_codigo})

    albaranes_pendientes = []
    for record in rows_alb:
        fecha_albaran = record.get("V_FECHA")
        if not isinstance(fecha_albaran, datetime):
            # Intenta convertirlo desde string
            fecha_albaran = datetime.strptime(fecha_albaran, "%Y-%m-%d %H:%M:%S")

        record["V_FECHA"] = fecha_albaran.strftime("%Y-%m-%d")
        record['cambio_en_linea_albaran'] = get_cambio_linea_albaran(oracle,expediente_codigo,record['V_NUMERO_DOC_INTERNO'])
    
        valor_usd = parse_euro_number(record['V_IMPORTE_TOTAL_ALBARAN'])
        cambio    = parse_euro_number(record['cambio_en_linea_albaran'][0]['V_CAMBIO'])
        record['valor_albaran_suz']    = valor_usd * cambio
        record['precio_dolar_diario']  = get_cambio_diario(record['V_FECHA'], cambios_diario)
        record['precio_dolar_mensual'] = get_cambio_mensual(record['V_FECHA'][:7], cambios_mes)
        
        albaranes_pendientes.append(record)

    return albaranes_pendientes



def get_cambio_linea_albaran(oracle, expediente_codigo, doc_interno):
    sql_cam = """SELECT V_EXPEDIENTE_IMPORTACION,
    V_CAMBIO,
    NUMERO_DOC_INTERNO
    FROM (SELECT ALBARAN_COMPRAS_L.* ,pkconsgen.f_descrip_centro_doc_albcmplin(codigo_empresa, numero_doc_interno, centro_coste) D_CENTRO_COSTE,pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,pkconsgen.hay_replicacion_com_vta(albaran_compras_l.numero_doc_interno, albaran_compras_l.codigo_empresa, albaran_compras_l.numero_linea) HAY_REPLICACION_VTA,pkconsgen.hay_textos_albcompra(codigo_empresa, numero_doc_interno, numero_linea) HAY_TEXTOS,CAMBIO V_CAMBIO,CANTIDAD_ENTREGADA V_CANTIDAD_ENTREGADA,NVL(CANTIDAD_FACTURADA, 0) V_CANTIDAD_FACTURADA,CENTRO_COSTE V_CENTRO_COSTE,CODIGO_ARTICULO V_CODIGO_ARTICULO,COALESCE(albaran_compras_l.descripcion,(SELECT a.descrip_comercial FROM articulos a WHERE a.codigo_articulo=albaran_compras_l.codigo_articulo AND a.codigo_empresa=albaran_compras_l.codigo_empresa)) V_DESCRIPCION,DECODE(albaran_compras_l.numero_lote_int,NULL,NULL,(SELECT lvhl.descripcion_lote FROM historico_lotes lvhl WHERE lvhl.numero_lote_int = albaran_compras_l.numero_lote_int AND lvhl.codigo_articulo = albaran_compras_l.codigo_articulo AND lvhl.codigo_empresa = albaran_compras_l.codigo_empresa)) V_DESCRIPCION_LOTE,DECODE(albaran_compras_l.numero_lote_int,NULL,NULL,(SELECT lvhl.descripcion_lote2 FROM historico_lotes lvhl WHERE lvhl.numero_lote_int = albaran_compras_l.numero_lote_int AND lvhl.codigo_articulo = albaran_compras_l.codigo_articulo AND lvhl.codigo_empresa = albaran_compras_l.codigo_empresa)) V_DESCRIPCION_LOTE2,pkconsgen.f_get_status_devolucion(codigo_empresa, numero_doc_interno, numero_linea, status) V_DEVOLUCION,dtos_acumulados V_DTOS_ACUMULADOS,dto_1 V_DTO_1,dto_2 V_DTO_2,dto_3 V_DTO_3,dto_4 V_DTO_4,dto_5 V_DTO_5,dto_6 V_DTO_6,dto_und V_DTO_UND,dto_und_cad V_DTO_UND_CAD,EXPEDIENTE_IMPORTACION V_EXPEDIENTE_IMPORTACION,idto_1 V_IDTO_1,idto_2 V_IDTO_2,idto_3 V_IDTO_3,idto_4 V_IDTO_4,idto_5 V_IDTO_5,idto_6 V_IDTO_6,idto_und V_IDTO_UND,idto_und_cad V_IDTO_UND_CAD,PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, divisa, importe_lin_neto_div2) V_IMPORTE_LIN_NETO,PKCONSGEN.IMPORTE(NVL(importe_portes, 0), NVL(importe_portes_div, 0), divisa) V_IMP_PORTES,NUMERO_LINEA_PEDIDO V_NUMERO_LINEA_PEDIDO,COALESCE(numero_lote_int, pkconsgen.get_numero_lote_int_albcom(codigo_empresa, codigo_articulo, numero_doc_interno, numero_linea)) V_NUMERO_LOTE_INT,NUMERO_PEDIDO V_NUMERO_PEDIDO,PKCONSGEN.IMPORTE(precio_neto * cambio, precio_neto, divisa, precio_neto * cambio * cambio_div2) V_PRECIO_NETO,PKCONSGEN.IMPORTE(precio_presentacion * cambio, precio_presentacion, divisa, precio_presentacion * cambio * cambio_div2) V_PRECIO_PRESENTACION,PRESENTACION V_PRESENTACION,SERIE_PEDIDO V_SERIE_PEDIDO,UNIDADES_ALMACEN V_UNIDADES_ALMACEN,UNIDAD_ALMACEN2 V_UNIDAD_ALMACEN2,UNID_DIS V_UNID_DIS,UNID_EXP V_UNID_EXP,UNID_SOB V_UNID_SOB,UNID_SUB V_UNID_SUB FROM ALBARAN_COMPRAS_L) ALBARAN_COMPRAS_L 
    WHERE CODIGO_EMPRESA='001' and NUMERO_DOC_INTERNO=:doc_interno and V_EXPEDIENTE_IMPORTACION = :expediente_codigo"""

    res = [] 
    rows_cam =  oracle.consult(sql_cam, {'doc_interno':doc_interno, 'expediente_codigo': expediente_codigo})

    for record in rows_cam:
        res.append(record)
    return res 


def parse_euro_number(euro_str):
    if euro_str is None or str(euro_str).strip() in ("", "None"):
        return 0.0

    euro_str = str(euro_str).strip()

    if euro_str.startswith(','):
        euro_str = '0' + euro_str

    if ',' in euro_str:
        euro_str = euro_str.replace('.', '').replace(',', '.')
    else:
        euro_str = euro_str

    if re.match(r'^\d+(\.\d+)?$', euro_str):
        return float(euro_str)
    else:
        raise ValueError(f"Formato inválido para número: '{euro_str}'")
    


def get_cambio_diario(fechaDelDia, cambios_diario):  
    for item in cambios_diario:
        if item["FECHA_VALOR"] == fechaDelDia:
            return item

    return None



def get_cambio_mensual(fechaDelMes, cambios_mes):
    yyyymm = fechaDelMes.replace("-", "")  # "2025-05" → "202505"

    for item in cambios_mes:
        if item["GC2"] == yyyymm:
            return item

    return None

################################################

def get_albaran_facturado(oracle, expediente_codigo, cambios_diario, cambios_mes):
    sql_alb_fac = """SELECT V_FECHA,
            V_NUMERO_DOC_EXT,
            V_NUMERO_DOC_INTERNO,
            V_CODIGO_ALMACEN,
            D_CODIGO_ALMACEN,
            V_IMPORTE_TOTAL_ALBARAN,
            V_DIVISA,
            NUMERO_DOC_INTERNO,
            V_NUMERO_EXPEDIENTE,V_HOJA_SEGUIMIENTO 
        FROM (SELECT ALBARAN_COMPRAS_C.* ,(SELECT lvcc.nombre FROM caracteres_asiento lvcc WHERE lvcc.codigo = albaran_compras_c.centro_contable AND lvcc.empresa = albaran_compras_c.codigo_empresa) D_CENTRO_CONTABLE,(SELECT lval.nombre FROM almacenes lval WHERE lval.almacen = albaran_compras_c.codigo_almacen AND lval.codigo_empresa = albaran_compras_c.codigo_empresa) D_CODIGO_ALMACEN,(SELECT lvcpr.nombre FROM organizacion_compras lvcpr WHERE lvcpr.codigo_org_compras = albaran_compras_c.organizacion_compras AND lvcpr.codigo_empresa = albaran_compras_c.codigo_empresa) D_ORGANIZACION_COMPRAS,(SELECT lvtppco.descripcion FROM tipos_pedido_com lvtppco WHERE lvtppco.tipo_pedido = albaran_compras_c.tipo_pedido_com AND lvtppco.organizacion_compras = albaran_compras_c.organizacion_compras AND lvtppco.codigo_empresa = albaran_compras_c.codigo_empresa) D_TIPO_PEDIDO_COM,pkconsgen.ac_hay_archivos(codigo_empresa, numero_doc_interno) HAY_ARCHIVOS,pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,pkconsgen.hay_replicacion_com_vta(albaran_compras_c.numero_doc_interno, albaran_compras_c.codigo_empresa, NULL) HAY_REPLICACION_VTA,CENTRO_CONTABLE V_CENTRO_CONTABLE,CODIGO_ALMACEN V_CODIGO_ALMACEN,contador_gestion V_CONTADOR_GESTION,DECODE(deposito_proveedor, 'S', 'S', 'N', 'N', 'D', 'D', 'N') V_DEPOSITO,PKCONSGEN.DIVISA(PKCONSGEN.DIVISA_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno)) V_DIVISA,FECHA V_FECHA,fecha_asiento V_FECHA_ASIENTO,HOJA_SEGUIMIENTO V_HOJA_SEGUIMIENTO,PKCONSGEN.IMPORTE_TXT(PKCONSGEN.IMPORTE_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno, 'N'), PKCONSGEN.IMPORTE_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno, 'S'), PKCONSGEN.DIVISA_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno),PKCONSGEN.IMPORTE_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno, '2')) V_IMPORTE_TOTAL_ALBARAN,numero_asiento_borrador V_NUMERO_ASIENTO_BORRADOR,NUMERO_DOC_EXT V_NUMERO_DOC_EXT,NUMERO_DOC_INTERNO V_NUMERO_DOC_INTERNO,NUMERO_EXPEDIENTE V_NUMERO_EXPEDIENTE,ORGANIZACION_COMPRAS V_ORGANIZACION_COMPRAS,TIPO_PEDIDO_COM V_TIPO_PEDIDO_COM,USUARIO V_USUARIO FROM ALBARAN_COMPRAS_C) ALBARAN_COMPRAS_C 
        WHERE  V_NUMERO_EXPEDIENTE = :expediente_codigo AND codigo_empresa = '001' AND NVL(deposito_proveedor, 'N') != 'S' AND facturado = 'S' AND interno = 'N'  order by FECHA DESC"""

    rows_alb_fac = oracle.consult(sql_alb_fac, {'expediente_codigo': expediente_codigo})

    albaranes_pendientes = []
    for record in rows_alb_fac:
        fecha_albaran = record.get("V_FECHA")
        if not isinstance(fecha_albaran, datetime):
            fecha_albaran = datetime.strptime(fecha_albaran, "%Y-%m-%d %H:%M:%S")
            record["V_FECHA"] = fecha_albaran.strftime("%Y-%m-%d")
            record['cambio_en_linea_albaran'] = get_cambio_linea_albaran(oracle, expediente_codigo, record['V_NUMERO_DOC_INTERNO'])
            
        valor_usd = parse_euro_number(record['V_IMPORTE_TOTAL_ALBARAN'])
        cambio    = parse_euro_number(record['cambio_en_linea_albaran'][0]['V_CAMBIO'])
        record['valor_albaran_suz'] = valor_usd * cambio
        record['precio_dolar_diario']  = get_cambio_diario(record['V_FECHA'], cambios_diario)
        record['precio_dolar_mensual'] = get_cambio_mensual(record['V_FECHA'][:7], cambios_mes)
        
        albaranes_pendientes.append(record)

    return albaranes_pendientes



###################################################################################


def get_albaran_no_facturables(oracle, expediente_codigo, cambios_diario, cambios_mes):
    sql_no_fac = """SELECT V_FECHA,
            V_NUMERO_DOC_EXT,
            V_NUMERO_DOC_INTERNO,
            V_CODIGO_ALMACEN,
            D_CODIGO_ALMACEN,
            V_IMPORTE_TOTAL_ALBARAN,
            V_DIVISA,
            NUMERO_DOC_INTERNO,
            V_NUMERO_EXPEDIENTE,V_HOJA_SEGUIMIENTO 
        FROM (SELECT ALBARAN_COMPRAS_C.* ,(SELECT lvcc.nombre FROM caracteres_asiento lvcc WHERE lvcc.codigo = albaran_compras_c.centro_contable AND lvcc.empresa = albaran_compras_c.codigo_empresa) D_CENTRO_CONTABLE,(SELECT lval.nombre FROM almacenes lval WHERE lval.almacen = albaran_compras_c.codigo_almacen AND lval.codigo_empresa = albaran_compras_c.codigo_empresa) D_CODIGO_ALMACEN,(SELECT lvcpr.nombre FROM organizacion_compras lvcpr WHERE lvcpr.codigo_org_compras = albaran_compras_c.organizacion_compras AND lvcpr.codigo_empresa = albaran_compras_c.codigo_empresa) D_ORGANIZACION_COMPRAS,(SELECT lvtppco.descripcion FROM tipos_pedido_com lvtppco WHERE lvtppco.tipo_pedido = albaran_compras_c.tipo_pedido_com AND lvtppco.organizacion_compras = albaran_compras_c.organizacion_compras AND lvtppco.codigo_empresa = albaran_compras_c.codigo_empresa) D_TIPO_PEDIDO_COM,pkconsgen.ac_hay_archivos(codigo_empresa, numero_doc_interno) HAY_ARCHIVOS,pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,pkconsgen.hay_replicacion_com_vta(albaran_compras_c.numero_doc_interno, albaran_compras_c.codigo_empresa, NULL) HAY_REPLICACION_VTA,CENTRO_CONTABLE V_CENTRO_CONTABLE,CODIGO_ALMACEN V_CODIGO_ALMACEN,contador_gestion V_CONTADOR_GESTION,DECODE(deposito_proveedor, 'S', 'S', 'N', 'N', 'D', 'D', 'N') V_DEPOSITO,PKCONSGEN.DIVISA(PKCONSGEN.DIVISA_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno)) V_DIVISA,FECHA V_FECHA,fecha_asiento V_FECHA_ASIENTO,HOJA_SEGUIMIENTO V_HOJA_SEGUIMIENTO,PKCONSGEN.IMPORTE_TXT(PKCONSGEN.IMPORTE_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno, 'N'), PKCONSGEN.IMPORTE_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno, 'S'), PKCONSGEN.DIVISA_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno),PKCONSGEN.IMPORTE_ALBARAN_COMPRAS(codigo_empresa, numero_doc_interno, '2')) V_IMPORTE_TOTAL_ALBARAN,numero_asiento_borrador V_NUMERO_ASIENTO_BORRADOR,NUMERO_DOC_EXT V_NUMERO_DOC_EXT,NUMERO_DOC_INTERNO V_NUMERO_DOC_INTERNO,NUMERO_EXPEDIENTE V_NUMERO_EXPEDIENTE,ORGANIZACION_COMPRAS V_ORGANIZACION_COMPRAS,TIPO_PEDIDO_COM V_TIPO_PEDIDO_COM,USUARIO V_USUARIO FROM ALBARAN_COMPRAS_C) ALBARAN_COMPRAS_C 
        WHERE  V_NUMERO_EXPEDIENTE = :expediente_codigo AND codigo_empresa = '001' AND NVL(deposito_proveedor, 'N') != 'S' AND facturado = 'N' AND interno = 'S'  order by FECHA DESC"""

    rows_no_fac =  oracle.consult(sql_no_fac, {'expediente_codigo': expediente_codigo})

    albaranes_pendientes = []
    for record in rows_no_fac:
        fecha_albaran = record.get("V_FECHA")
        if not isinstance(fecha_albaran, datetime):
            fecha_albaran = datetime.strptime(fecha_albaran, "%Y-%m-%d %H:%M:%S")
            record["V_FECHA"] = fecha_albaran.strftime("%Y-%m-%d")
            record['cambio_en_linea_albaran'] = cambio_en_no_facturables(oracle, record['V_NUMERO_DOC_INTERNO'])
            
        valor_usd = parse_euro_number(record['V_IMPORTE_TOTAL_ALBARAN'])
        cambio    = parse_euro_number(record['cambio_en_linea_albaran'][0]['V_CAMBIO'])
        record['valor_albaran_suz'] = valor_usd * cambio
        record['precio_dolar_diario']  = get_cambio_diario(record['V_FECHA'], cambios_diario)
        record['precio_dolar_mensual'] = get_cambio_mensual(record['V_FECHA'][:7], cambios_mes)
        
        albaranes_pendientes.append(record)

    return albaranes_pendientes



def cambio_en_no_facturables(oracle, numero_doc_interno):
    sql_camb = """SELECT V_CAMBIO 
            FROM (SELECT ALBARAN_COMPRAS_L.* ,pkconsgen.f_descrip_centro_doc_albcmplin(codigo_empresa, numero_doc_interno, centro_coste) D_CENTRO_COSTE,pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,pkconsgen.hay_replicacion_com_vta(albaran_compras_l.numero_doc_interno, albaran_compras_l.codigo_empresa, albaran_compras_l.numero_linea) HAY_REPLICACION_VTA,pkconsgen.hay_textos_albcompra(codigo_empresa, numero_doc_interno, numero_linea) HAY_TEXTOS,CAMBIO V_CAMBIO,CANTIDAD_ENTREGADA V_CANTIDAD_ENTREGADA,NVL(CANTIDAD_FACTURADA, 0) V_CANTIDAD_FACTURADA,CENTRO_COSTE V_CENTRO_COSTE,CODIGO_ARTICULO V_CODIGO_ARTICULO,COALESCE(albaran_compras_l.descripcion,(SELECT a.descrip_comercial FROM articulos a WHERE a.codigo_articulo=albaran_compras_l.codigo_articulo AND a.codigo_empresa=albaran_compras_l.codigo_empresa)) V_DESCRIPCION,DECODE(albaran_compras_l.numero_lote_int,NULL,NULL,(SELECT lvhl.descripcion_lote FROM historico_lotes lvhl WHERE lvhl.numero_lote_int = albaran_compras_l.numero_lote_int AND lvhl.codigo_articulo = albaran_compras_l.codigo_articulo AND lvhl.codigo_empresa = albaran_compras_l.codigo_empresa)) V_DESCRIPCION_LOTE,DECODE(albaran_compras_l.numero_lote_int,NULL,NULL,(SELECT lvhl.descripcion_lote2 FROM historico_lotes lvhl WHERE lvhl.numero_lote_int = albaran_compras_l.numero_lote_int AND lvhl.codigo_articulo = albaran_compras_l.codigo_articulo AND lvhl.codigo_empresa = albaran_compras_l.codigo_empresa)) V_DESCRIPCION_LOTE2,pkconsgen.f_get_status_devolucion(codigo_empresa, numero_doc_interno, numero_linea, status) V_DEVOLUCION,dtos_acumulados V_DTOS_ACUMULADOS,dto_1 V_DTO_1,dto_2 V_DTO_2,dto_3 V_DTO_3,dto_4 V_DTO_4,dto_5 V_DTO_5,dto_6 V_DTO_6,dto_und V_DTO_UND,dto_und_cad V_DTO_UND_CAD,EXPEDIENTE_IMPORTACION V_EXPEDIENTE_IMPORTACION,idto_1 V_IDTO_1,idto_2 V_IDTO_2,idto_3 V_IDTO_3,idto_4 V_IDTO_4,idto_5 V_IDTO_5,idto_6 V_IDTO_6,idto_und V_IDTO_UND,idto_und_cad V_IDTO_UND_CAD,PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, divisa, importe_lin_neto_div2) V_IMPORTE_LIN_NETO,PKCONSGEN.IMPORTE(NVL(importe_portes, 0), NVL(importe_portes_div, 0), divisa) V_IMP_PORTES,NUMERO_LINEA_PEDIDO V_NUMERO_LINEA_PEDIDO,COALESCE(numero_lote_int, pkconsgen.get_numero_lote_int_albcom(codigo_empresa, codigo_articulo, numero_doc_interno, numero_linea)) V_NUMERO_LOTE_INT,NUMERO_PEDIDO V_NUMERO_PEDIDO,PKCONSGEN.IMPORTE(precio_neto * cambio, precio_neto, divisa, precio_neto * cambio * cambio_div2) V_PRECIO_NETO,PKCONSGEN.IMPORTE(precio_presentacion * cambio, precio_presentacion, divisa, precio_presentacion * cambio * cambio_div2) V_PRECIO_PRESENTACION,PRESENTACION V_PRESENTACION,SERIE_PEDIDO V_SERIE_PEDIDO,UNIDADES_ALMACEN V_UNIDADES_ALMACEN,UNIDAD_ALMACEN2 V_UNIDAD_ALMACEN2,UNID_DIS V_UNID_DIS,UNID_EXP V_UNID_EXP,UNID_SOB V_UNID_SOB,UNID_SUB V_UNID_SUB FROM ALBARAN_COMPRAS_L) ALBARAN_COMPRAS_L 
            WHERE CODIGO_EMPRESA='001' and NUMERO_DOC_INTERNO=:numero_doc_interno
            """
    res = []
    rows_camb = oracle.consult(sql_camb, {'numero_doc_interno':numero_doc_interno})
    for record in rows_camb:
        res.append(record)
    return res 


#####################################################################



def get_facturas(oracle, expediente_codigo, codigo_proveedor, cambios_diario, cambios_mes):
    # desde lineas de facturas (no se si son tambien de albaranes) busco POSIBLES NUMERO_FACTURA
    # y luego busco las facturas con ese numero de factura
    sql_fac = """SELECT 
            distinct NUMERO_FACTURA
            FROM (SELECT FACTURAS_COMPRAS_LIN.* ,
            DECODE(facturas_compras_lin.centro_coste,NULL,NULL,(SELECT lvcencos.nombre FROM centros_coste lvcencos WHERE lvcencos.codigo = facturas_compras_lin.centro_coste AND lvcencos.empresa = facturas_compras_lin.codigo_empresa)) D_CENTRO_COSTE,
            pkconsgen.hay_asociacion_crm(codigo_empresa, id_crm) HAY_ASOCIACION_CRM,
            pkconsgen.hay_replicacion_com_vta(facturas_compras_lin.num_albaran_int, facturas_compras_lin.codigo_empresa, facturas_compras_lin.linea_albaran) HAY_REPLICACION_VTA,
            CANTIDAD_FACTURADA V_CANTIDAD_FACTURADA,
            CENTRO_COSTE V_CENTRO_COSTE,
            CODIGO_ARTICULO V_CODIGO_ARTICULO,
            COALESCE((SELECT a.descripcion FROM albaran_compras_l a WHERE a.numero_doc_interno = facturas_compras_lin.num_albaran_int AND a.numero_linea = facturas_compras_lin.linea_albaran AND a.codigo_empresa = facturas_compras_lin.codigo_empresa), 
            (SELECT a.descrip_comercial FROM articulos a WHERE a.codigo_articulo = facturas_compras_lin.codigo_articulo AND a.codigo_empresa = facturas_compras_lin.codigo_empresa)) V_DESCRIPCION_ARTICULO,dto_1 V_DTO_1,dto_2 V_DTO_2,dto_3 V_DTO_3,
            PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, 
            pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) V_IMPORTE_NETO,
            LINEA_ALBARAN V_LINEA_ALBARAN,(SELECT al.expediente_importacion FROM albaran_compras_l al WHERE al.numero_doc_interno = facturas_compras_lin.num_albaran_int AND al.numero_linea = facturas_compras_lin.numero_linea AND al.codigo_empresa = facturas_compras_lin.codigo_empresa) V_NUMERO_EXPEDIENTE,(SELECT c.numero_doc_ext FROM albaran_compras_c c WHERE c.numero_doc_interno = facturas_compras_lin.num_albaran_int AND c.codigo_empresa = facturas_compras_lin.codigo_empresa) V_NUM_ALBARAN_EXT,NUM_ALBARAN_INT V_NUM_ALBARAN_INT,DECODE((SELECT a.unidad_precio_coste FROM articulos a WHERE a.codigo_articulo = facturas_compras_lin.codigo_articulo AND a.codigo_empresa = facturas_compras_lin.codigo_empresa), 1, DECODE(unidades_facturadas, 0, 0, PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) / unidades_facturadas),  DECODE(unidades_facturadas2, 0, 0, PKCONSGEN.IMPORTE(importe_lin_neto, importe_lin_neto_div, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) / unidades_facturadas2)) V_PRECIO_NETO,PKCONSGEN.PRECIO(precio_presentacion * pkconsgen.f_get_valor_cambio_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura), precio_presentacion, pkconsgen.f_get_divisa_faccomp(facturas_compras_lin.codigo_empresa, facturas_compras_lin.numero_factura, facturas_compras_lin.codigo_proveedor, facturas_compras_lin.ejercicio, facturas_compras_lin.tipo_factura)) V_PRECIO_PRESENTACION,PRESENTACION V_PRESENTACION,facturas_compras_lin.tipo_factura V_TIPO_FACTURA,UNIDADES_FACTURADAS V_UNIDADES_FACTURADAS,UNIDADES_FACTURADAS2 V_UNIDADES_FACTURADAS2 FROM FACTURAS_COMPRAS_LIN) FACTURAS_COMPRAS_LIN 
            WHERE V_NUMERO_EXPEDIENTE= :expediente_codigo"""
    
    rows_fac = oracle.consult (sql_fac, {'expediente_codigo': expediente_codigo})
    posibles_numeros_facturas = []
    for record in rows_fac:
        posibles_numeros_facturas.append(record)

    sqlX = """SELECT V_FECHA_FACTURA,
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
        WHERE codigo_proveedor = :codigo_proveedor AND V_NUMERO_FACTURA = :numero_factura  order by fecha_factura DESC"""
    
    facturas_por_expeidente = []
    

    for factura in posibles_numeros_facturas:
        rowsX = oracle.consult(sqlX, {'codigo_proveedor': codigo_proveedor, 'numero_factura': factura['NUMERO_FACTURA']})
 
        for record in rowsX:
            valor_usd = parse_euro_number(record['V_NETO_FACTURA'])
            cambio    = parse_euro_number(record['V_VALOR_CAMBIO'])
            record['valor_factura_suz'] = valor_usd * cambio
            record['V_FECHA_FACTURA'] = record['V_FECHA_FACTURA'][:10]
            record['precio_dolar_diario']  = get_cambio_diario(record['V_FECHA_FACTURA'], cambios_diario)
            record['precio_dolar_mensual'] = get_cambio_mensual(record['V_FECHA_FACTURA'][:7], cambios_mes)
            facturas_por_expeidente.append(record)
        
    return facturas_por_expeidente