from datetime import datetime
from finanzas.fin_utils.inf_expedientes.get_albaran_pendiente_de_facturar_file import get_albaran_facturado, get_albaran_no_facturables, get_albaran_pendiente_de_facturar, get_facturas
from froxa.utils.connectors.libra_connector import OracleConnector

def get_list_expdientes(request):
    oracle = OracleConnector()
    oracle.connect()

    # 1. cambio del dia a la hora de generarse el documento !!!
    sql_diario = """SELECT DIVISA_ORIGEN, 
                    DIVISA_DESTINO, 
                    FECHA_VALOR,
                    VALOR_COMPRA,
                    VALOR_VENTA
                    FROM (SELECT cambio_divisas.* ,
                    (SELECT lvdiv.nombre FROM divisas lvdiv WHERE lvdiv.codigo = cambio_divisas.divisa_destino) D_DIVISA_DESTINO,
                    (SELECT lvdiv.nombre FROM divisas lvdiv WHERE lvdiv.codigo = cambio_divisas.divisa_origen) D_DIVISA_ORIGEN FROM cambio_divisas) cambio_divisas 
                    where fecha_valor >= '01/02/2025' 
                    order by fecha_valor asc"""


    rows_diario  = oracle.consult(sql_diario)


    cambios_diario = []
    for record in rows_diario:
        fecha_valor = record.get("FECHA_VALOR")

        if isinstance(fecha_valor, datetime):
            fecha_dt = fecha_valor
        else:
            try:
                fecha_dt = datetime.strptime(fecha_valor, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                fecha_dt = datetime.strptime(fecha_valor, "%Y-%m-%d")

        record["FECHA_VALOR"] = fecha_dt.strftime("%Y-%m-%d")
        record["TIME_SORT"] = fecha_dt.strftime("%Y%m")

        cambios_diario.append(record)
   
    
    # 2. cambio del mes
    sql_mes = """SELECT GC1,D_GC1,GC2, GN1 FROM (SELECT EMPRESA GC1,DECODE(froxa_seguros_cambio.empresa,NULL,NULL,(SELECT lvemp.nombre FROM empresas_conta lvemp WHERE lvemp.codigo = froxa_seguros_cambio.empresa)) D_GC1,PERIODO GC2,CAMBIO GN1,NULL GN2,NULL GN3,NULL GN4,NULL GN5,NULL GN6,NULL GN7,NULL GN8,NULL GN9,NULL GN10,NULL GN11,NULL GN12,NULL GN13,NULL GN14,NULL GN15,NULL GN16,NULL GN17,NULL GN18,NULL GN19,NULL GN20,NULL GN21,NULL GN22,NULL GN23,NULL GN24,NULL GN25,NULL GC3,NULL GC4,NULL GC5,NULL GC6,NULL GC7,NULL GC8,NULL GC9,NULL GC10,NULL GC11,NULL GC12,NULL GC13,NULL GC14,NULL GC15,NULL GC16,NULL GC17,NULL GC18,NULL GC19,NULL GC20,NULL GC21,NULL GC22,NULL GC23,NULL GC24,NULL GC25,NULL GD1,NULL GD2,NULL GD3,NULL GD4,NULL GD5,NULL GD6,NULL GD7,NULL GD8,NULL GD9,NULL GD10,NULL GD11,NULL GD12,NULL GD13,NULL GD14,NULL GD15,NULL GD16,NULL GD17,NULL GD18,NULL GD19,NULL GD20,NULL GD21,NULL GD22,NULL GD23,NULL GD24,NULL GD25,NULL GCHECK1,NULL GCHECK2,NULL GCHECK3,NULL GCHECK4,NULL GCHECK5,NULL GCHECK6,NULL GCHECK7,NULL GCHECK8,NULL GCHECK9,NULL GCHECK10,NULL GCHECK11,NULL GCHECK12,NULL GCHECK13,NULL GCHECK14,NULL GCHECK15,NULL GCHECK16,NULL GCHECK17,NULL GCHECK18,NULL GCHECK19,NULL GCHECK20,NULL GCHECK21,NULL GCHECK22,NULL GCHECK23,NULL GCHECK24,NULL GCHECK25,NULL N1,NULL N2,NULL N3,NULL N4,NULL N5,NULL N6,NULL N7,NULL N8,NULL N9,NULL N10,NULL N11,NULL N12,NULL N13,NULL N14,NULL N15,NULL N16,NULL N17,NULL N18,NULL N19,NULL N20,NULL N21,NULL N22,NULL N23,NULL N24,NULL N25,NULL N26,NULL N27,NULL N28,NULL N29,NULL N30,NULL C1,NULL C2,NULL C3,NULL C4,NULL C5,NULL C6,NULL C7,NULL C8,NULL C9,NULL C10,NULL C11,NULL C12,NULL C13,NULL C14,NULL C15,NULL C16,NULL C17,NULL C18,NULL C19,NULL C20,NULL C21,NULL C22,NULL C23,NULL C24,NULL C25,NULL C26,NULL C27,NULL C28,NULL C29,NULL C30,NULL D1,NULL D2,NULL D3,NULL D4,NULL D5,NULL D6,NULL D7,NULL D8,NULL D9,NULL D10,NULL D11,NULL D12,NULL D13,NULL D14,NULL D15,NULL D16,NULL D17,NULL D18,NULL D19,NULL D20,NULL D21,NULL D22,NULL D23,NULL D24,NULL D25,NULL D26,NULL D27,NULL D28,NULL D29,NULL D30,NULL CHECK1,NULL CHECK2,NULL CHECK3,NULL CHECK4,NULL CHECK5,NULL CHECK6,NULL CHECK7,NULL CHECK8,NULL CHECK9,NULL CHECK10,NULL CHECK11,NULL CHECK12,NULL CHECK13,NULL CHECK14,NULL CHECK15,NULL CHECK16,NULL CHECK17,NULL CHECK18,NULL CHECK19,NULL CHECK20,NULL CHECK21,NULL CHECK22,NULL CHECK23,NULL CHECK24,NULL CHECK25,NULL CHECK26,NULL CHECK27,NULL CHECK28,NULL CHECK29,NULL CHECK30,NULL LIST1,NULL LIST2,NULL LIST3,NULL LIST4,NULL LIST5,NULL LIST6,NULL LIST7,NULL LIST8,NULL LIST9,NULL LIST10,NULL TEXTAREA1,NULL TEXTAREA2,NULL D_GC2,NULL D_GC3,NULL D_GC4,NULL D_GC5,NULL D_GC6,NULL D_GC7,NULL D_GC8,NULL D_GC9,NULL D_GC10,NULL D_GC11,NULL D_GC12,NULL D_GC13,NULL D_GC14,NULL D_GC15,NULL D_GC16,NULL D_GC17,NULL D_GC18,NULL D_GC19,NULL D_GC20,NULL D_GC21,NULL D_GC22,NULL D_GC23,NULL D_GC24,NULL D_GC25,NULL D_GN0,NULL D_GN1,NULL D_GN2,NULL D_GN3,NULL D_GN4,NULL D_GN5,NULL D_GN6,NULL D_GN7,NULL D_GN8,NULL D_GN9,NULL D_GN10,NULL D_GN11,NULL D_GN12,NULL D_GN13,NULL D_GN14,NULL D_GN15,NULL D_GN16,NULL D_GN17,NULL D_GN18,NULL D_GN19,NULL D_GN20,NULL D_GN21,NULL D_GN22,NULL D_GN23,NULL D_GN24,NULL D_GN25,NULL D_C1,NULL D_C2,NULL D_C3,NULL D_C4,NULL D_C5,NULL D_C6,NULL D_C7,NULL D_C8,NULL D_C9,NULL D_C10,NULL D_C11,NULL D_C12,NULL D_C13,NULL D_C14,NULL D_C15,NULL D_C16,NULL D_C17,NULL D_C18,NULL D_C19,NULL D_C20,NULL D_C21,NULL D_C22,NULL D_C23,NULL D_C24,NULL D_C25,NULL D_C26,NULL D_C27,NULL D_C28,NULL D_C29,NULL D_C30,NULL D_N1,NULL D_N2,NULL D_N3,NULL D_N4,NULL D_N5,NULL D_N6,NULL D_N7,NULL D_N8,NULL D_N9,NULL D_N10,NULL D_N11,NULL D_N12,NULL D_N13,NULL D_N14,NULL D_N15,NULL D_N16,NULL D_N17,NULL D_N18,NULL D_N19,NULL D_N20,NULL D_N21,NULL D_N22,NULL D_N23,NULL D_N24,NULL D_N25,NULL D_N26,NULL D_N27,NULL D_N28,NULL D_N29,NULL D_N30,NULL GN0,NULL GD0,rowid int_rowid FROM FROXA_SEGUROS_CAMBIO) FROXA_SEGUROS_CAMBIO WHERE 8=8/*INIQRY*/  order by GC2"""

    rows_mes = oracle.consult(sql_mes)

    cambios_mes = []
    for mes in rows_mes:
        cambios_mes.append(mes)

    # 3. dame expedientes en $
    sql_exp ="""select CODIGO, 
        (select nombre from proveedores where codigo_rapido = PROVEEDOR) as NOMBRE_PROVEEDOR,
        PROVEEDOR, FECHA_EXPEDIENTE, VALOR_CAMBIO, USUARIO_APERTURA, USUARIO_RESPONSABLE
        from EXPEDIENTES_IMP
        where divisa = 'USD' and FECHA_EXPEDIENTE >= :dateFrom and FECHA_EXPEDIENTE <= :dateTo
        order by CODIGO desc"""

    dateFrom = '2025-01-01' # request.GET.get('dateFrom') CON LAS FECHAS FILTRAMOS AL FINAL, NO AQUI !!!
    dateFrom = date_obj = datetime.strptime(dateFrom, "%Y-%m-%d")
    dateFrom = date_obj.strftime("%d/%m/%Y")
    dateTo   = '2035-01-01' # request.GET.get('dateTo')
    dateTo   = date_obj = datetime.strptime(dateTo, "%Y-%m-%d")
    dateTo   = date_obj.strftime("%d/%m/%Y")

    rows_exp = oracle.consult(sql_exp, {'dateFrom':dateFrom, 'dateTo':dateTo})
    
    expedientes = []
    for record in rows_exp:
        fecha = record.get("FECHA_EXPEDIENTE")
        if isinstance(fecha, datetime):
            record["FECHA_EXPEDIENTE"] = fecha.strftime("%Y-%m-%d")
        expedientes.append(record)


    for expediente in expedientes:
        expediente['_'] = ""
        expediente['ALB_PENDIENTE_DE_FACTURAR'] = []
        expediente['ALB_FACTURADOS']            = []
        expediente['ALB_NO_FACTURABLES']        = []
        expediente['FACTURAS']                  = []

    for expediente in expedientes:
        expediente['_'] = ""
        expediente['ALB_PENDIENTE_DE_FACTURAR'] = get_albaran_pendiente_de_facturar(oracle, expediente['CODIGO'], cambios_diario, cambios_mes)
        expediente['ALB_FACTURADOS']            = get_albaran_facturado(oracle, expediente['CODIGO'], cambios_diario, cambios_mes)
        expediente['ALB_NO_FACTURABLES']        = get_albaran_no_facturables(oracle, expediente['CODIGO'], cambios_diario, cambios_mes) 
        expediente['FACTURAS']                  = get_facturas(oracle, expediente['CODIGO'], expediente['PROVEEDOR'], cambios_diario, cambios_mes)

    oracle.close()

    fecha_factura_desde = request.GET.get('dateFrom')
    fecha_factura_hasta = request.GET.get('dateTo')

    # return {'fecha_factura_desde': fecha_factura_desde, 'fecha_factura_hasta': fecha_factura_hasta}

    # filtro las facturas obtenidas al final por las fechas de usuario

    exped_con_factura = []
    for exp in expedientes:
        addThisExpediente = 0
        if len(exp['FACTURAS']) > 0:
            list_albaranes_facturados = exp['ALB_FACTURADOS']
            for albaran in list_albaranes_facturados:
                if albaran['V_FECHA'] >= fecha_factura_desde and albaran['V_FECHA'] <= fecha_factura_hasta:
                    addThisExpediente = 1

        if addThisExpediente == 1:
            exped_con_factura += [exp]


    return exped_con_factura

