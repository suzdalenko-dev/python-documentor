# http://127.0.0.1:8000/finanzas/get/0/0/payments_and_receipts/

from django.db import connection
from finanzas.fin_utils.inf_expedientes.save_line_invoice_file import save_line_invoice_line
from finanzas.models import InvoicesSales
from froxa.utils.connectors.libra_connector import OracleConnector
from froxa.utils.utilities.funcions_file import get_current_date, invoices_list_of_current_month



def payments_and_receipts(request):
    currentDate = get_current_date()
    #   InvoicesSales.objects.all().delete()
    #   with connection.cursor() as cursor:
    #       cursor.execute("ALTER SEQUENCE finanzas_invoicessales_id_seq RESTART WITH 1;")
    #   return 1

    numInvoices = 0
    x = []
    oracle = OracleConnector()
    oracle.connect()
    
    fechas_mes_a_mes = invoices_list_of_current_month()
    for start_month, end_month in fechas_mes_a_mes:
        sql2 = """SELECT 
                        FORMA_COBRO,
                        TO_NUMBER(fv.LIQUIDO_FACTURA) AS LIQUIDO_FACTURA,
                        
                        NVL(
                            (
                                SELECT TO_NUMBER(MAX(hc.IMPORTE)) 
                                FROM HISTORICO_COBROS hc
                                WHERE hc.DOCUMENTO = fv.NUMERO_FRA_CONTA AND hc.CODIGO_CLIENTE = fv.CLIENTE AND hc.FECHA_FACTURA = fv.FECHA_FACTURA AND ROWNUM=1
                            ), 
                                0
                            ) AS IMPORTE_COBRADO,
                        NVL(
                            (
                                SELECT TO_NUMBER(MAX(ha.IMPORTE))
                                FROM HISTORICO_DETALLADO_APUNTES ha
                                WHERE ha.DOCUMENTO = fv.NUMERO_FRA_CONTA AND ha.EMPRESA = fv.EMPRESA AND ha.CODIGO_ENTIDAD = fv.CLIENTE AND ha.CODIGO_CONCEPTO in ('COB', 'REM') AND DIARIO = 'BANC' AND ha.ENTIDAD = 'CL' AND ROWNUM = 1
                            ), 
                                0
                        ) AS IMPORTE_COBRADO_2,

                        TO_CHAR(fv.FECHA_FACTURA, 'YYYY-MM-DD') AS FECHA_FACTURA,
                        TO_CHAR(fv.FECHA_FACTURA, 'YYYY') AS EJERCICIO,
                        fv.EMPRESA, 
                        fv.CLIENTE, 
                        fv.NUMERO_FRA_CONTA AS DOCUMENTO,

                        (SELECT cli.NOMBRE || ' ' || cli.CODIGO_RAPIDO 
                            FROM VA_CLIENTES cli
                            WHERE cli.CODIGO_RAPIDO = fv.CLIENTE 
                              AND cli.CODIGO_EMPRESA = fv.EMPRESA 
                              AND ROWNUM = 1
                        ) AS NOMBRE_CLIENTE,

                        (SELECT org.NOMBRE
                            FROM VA_CLIENTES cli
                            JOIN ORGANIZACION_COMERCIAL org
                              ON cli.ORG_COMER = org.CODIGO_ORG_COMER
                             AND cli.CODIGO_EMPRESA = org.CODIGO_EMPRESA
                            WHERE cli.CODIGO_RAPIDO = fv.CLIENTE
                              AND cli.CODIGO_EMPRESA = fv.EMPRESA
                              AND ROWNUM = 1
                        ) AS DESCRIPCION_ORG_COMER,

                        (SELECT ag.NOMBRE
                        FROM agentes_clientes ac, agentes ag
                        WHERE ac.CODIGO_CLIENTE = fv.CLIENTE
                          AND ac.AGENTE = ag.CODIGO
                          AND ROWNUM = 1
                        ) AS NOMBRE_AGENTE,

                       NVL(
                            (
                                SELECT TO_CHAR(MAX(FV_VCTOS.FECHA_VENCIMIENTO), 'YYYY-MM-DD')
                                FROM FACTURAS_VENTAS_VCTOS FV_VCTOS
                                WHERE FV_VCTOS.NUMERO_SERIE = fv.NUMERO_SERIE
                                  AND FV_VCTOS.NUMERO_FACTURA = fv.NUMERO_FACTURA
                                  AND FV_VCTOS.CLIENTE = fv.CLIENTE
                                  AND FV_VCTOS.FORMA_COBRO = fv.FORMA_COBRO
                            ),
                            (
                                SELECT TO_CHAR(MAX(hc.FECHA_VENCIMIENTO), 'YYYY-MM-DD')
                                FROM HISTORICO_COBROS hc
                                WHERE hc.DOCUMENTO = fv.NUMERO_FRA_CONTA 
                                  AND hc.CODIGO_CLIENTE = fv.CLIENTE 
                                  AND hc.FECHA_FACTURA = fv.FECHA_FACTURA 
                            )
                        ) AS FECHA_VENCIMIENTO,

                        'S' AS DOCUMENTO_VIVO,

                        NVL(
                            (
                                SELECT TO_CHAR(MAX(ha.FECHA_ASIENTO), 'YYYY-MM-DD')
                                FROM HISTORICO_DETALLADO_APUNTES ha
                                WHERE ha.DOCUMENTO = fv.NUMERO_FRA_CONTA AND ha.EMPRESA = fv.EMPRESA AND ha.CODIGO_ENTIDAD = fv.CLIENTE AND ha.CODIGO_CONCEPTO in ('COB', 'REM') AND DIARIO = 'BANC' AND ha.ENTIDAD = 'CL'
                            ), 'dont_charged'
                        ) AS FECHA_ASIENTO_COBRO

                    FROM 
                        facturas_ventas fv
                    WHERE 
                        'suzdalenko'='suzdalenko'
                        AND fv.FECHA_FACTURA >= TO_DATE('2025-02-01', 'YYYY-MM-DD')
                        AND fv.FECHA_FACTURA >= TO_DATE(:start_month, 'YYYY-MM-DD') AND fv.FECHA_FACTURA <= TO_DATE(:end_month, 'YYYY-MM-DD')
                        AND fv.LIQUIDO_FACTURA > 0
                        AND fv.CLIENTE NOT IN ('003146')
                        AND EXISTS (
                            SELECT 1
                            FROM VA_CLIENTES cli
                            JOIN ORGANIZACION_COMERCIAL org
                              ON org.CODIGO_ORG_COMER = cli.ORG_COMER
                             AND org.CODIGO_EMPRESA   = cli.CODIGO_EMPRESA
                            WHERE cli.CODIGO_RAPIDO   = fv.CLIENTE
                              AND cli.CODIGO_EMPRESA  = fv.EMPRESA
                              AND org.CODIGO_ORG_COMER IN ('01','02','03','04')  -- ← aquí
                        )
                    ORDER BY 
                        fv.FECHA_FACTURA, 
                        fv.NUMERO_FRA_CONTA
                """

        invoices = oracle.consult(sql2, {'start_month':start_month, 'end_month':end_month}) or []

        # listado facturas
        for invoice in invoices:
            documentoString = str(invoice['DOCUMENTO']).strip()
            yearString      = str(invoice['EJERCICIO']).strip()

            if invoice['FECHA_ASIENTO_COBRO'] == 'dont_charged':
                Factura_Viva = 'N'
                if float(invoice['IMPORTE_COBRADO'] or 0) != float(invoice['LIQUIDO_FACTURA'] or 0):
                    # damos por cobrada si ya no hay nada vivo
                    sqlFactViva = """SELECT * FROM HISTORICO_COBROS hc WHERE hc.DOCUMENTO = :documentoString"""
                    sqlFactViva = oracle.consult(sqlFactViva, {'documentoString':documentoString}) or []
                    if len(sqlFactViva) > 0:
                        for sqlF in sqlFactViva:
                            if sqlF['DOCUMENTO_VIVO'] == 'S':
                                Factura_Viva = 'S'
                
                invoice['DOCUMENTO_VIVO'] = Factura_Viva

                # buscar numero agrupacion
                agrupacionesSql = """select * from AGRUPACIONES_DESGLOSES WHERE DOCUMENTO = :documentoString"""
                existeNumeroAgrupacion = oracle.consult(agrupacionesSql, {'documentoString':documentoString})
                if existeNumeroAgrupacion  is not None and len(existeNumeroAgrupacion) > 0:
                    numeros_dags       = []
                    numeros_agrupacion = []
                    for dagLine in existeNumeroAgrupacion:
                        num_agrupacion = str(dagLine['NUMERO_AGRUPACION']).strip()
                        if num_agrupacion not in numeros_agrupacion:
                            numeros_agrupacion += [num_agrupacion]
                            dagsSql = """SELECT * FROM AGRUPACIONES_DESGLOSES WHERE NUMERO_AGRUPACION = :num_agrupacion"""
                            getDagsLine = oracle.consult(dagsSql, {'num_agrupacion':num_agrupacion})
                            if getDagsLine  is not None and len(getDagsLine) > 0:
                                for dLine in getDagsLine:
                                    documentoDag = str(dLine['DOCUMENTO']).strip()                                   
                                    if documentoDag != documentoString:
                                        if documentoDag not in numeros_dags:
                                            numeros_dags += [documentoDag]
                                            sqlEsFactura = """SELECT 1 FROM facturas_ventas fv WHERE fv.numero_fra_conta = :documentoDag"""
                                            esFactura    = oracle.consult(sqlEsFactura, {'documentoDag': documentoDag})
                                            # quito las facturas rectificativas que se mezclan con los dags
                                            if esFactura is not None and len(esFactura) > 0:
                                                continue
                                            if "23/A" in documentoDag:
                                                continue
                                           
                                            saleLine, created = InvoicesSales.objects.get_or_create(documento=documentoString, ejercicio=yearString)
                                            
                                            chargeSql  = """select TO_CHAR(hda.FECHA_ASIENTO, 'YYYY-MM-DD') AS FECHA_COBRO
                                                            from historico_detallado_apuntes hda, HISTORICO_COBROS hc
                                                            where hda.DOCUMENTO = hc.DOCUMENTO 
                                                                AND hda.DOCUMENTO = :documentoDag 
                                                                AND hda.CODIGO_CONCEPTO IN ('COB', 'REM') 
                                                                AND hda.ENTIDAD = 'CL'
                                                                AND hda.CODIGO_ENTIDAD = hc.CODIGO_CLIENTE
                                                            ORDER BY hda.FECHA_ASIENTO DESC
                                                        """
                                            chargeInfo = oracle.consult(chargeSql, {'documentoDag':documentoDag})
                      
                                            if chargeInfo is not None and len(chargeInfo) > 0:
                                                invoice['fecha_cobro_dag_TOP'] = f"A COBRADO {documentoDag} {chargeInfo[0]['FECHA_COBRO']}"
                                                save_line_invoice_line(saleLine, chargeInfo[0]['FECHA_COBRO'], currentDate, invoice, invoice['LIQUIDO_FACTURA'], invoice['IMPORTE_COBRADO'])
                                            else:
                                                # puede ser que el dag ha cobrado el CLIENTE PADRE
                                                sqlMov = """select TO_CHAR(FECHA_MOVIMIENTO, 'YYYY-MM-DD') AS FECHA_MOVIMIENTO
                                                            from HISTORICO_MOV_CARTERA
                                                            where NUMERO_AGRUPACION = :num_agrupacion and DOCUMENTO = :documentoDag"""
                                                sqlMov = oracle.consult(sqlMov, {'num_agrupacion':num_agrupacion, 'documentoDag':documentoDag})
                                                if sqlMov is not None and len(sqlMov) > 0:
                                                    FECHA_COBRO_MOV = sqlMov[0]['FECHA_MOVIMIENTO']
                                                    invoice['fecha_cobro_dag_BOTTOM'] = f"FECHA_COBRO_MOV {FECHA_COBRO_MOV}"
                                                    save_line_invoice_line(saleLine, FECHA_COBRO_MOV, currentDate, invoice, invoice['LIQUIDO_FACTURA'], invoice['IMPORTE_COBRADO'])
                                                else:
                                                    # si no lo ha cobrado el padre:
                                                    # aqui estan las facturas con el DAG no cobrado aun
                                                    invoice['fecha_cobro_dag_BOTTOM'] = f"A NO COBRADO DAG BOTTOM {documentoDag}"
                                                    save_line_invoice_line(saleLine, "", currentDate, invoice, invoice['LIQUIDO_FACTURA'], 0)

                else:
                    sql02 = """select TO_CHAR(FECHA_ASIENTO, 'YYYY-MM-DD') AS FECHA_ASIENTO_MANO
                                                                from HISTORICO_DETALLADO_APUNTES
                                                                where documento = :documentoString AND DIARIO = 'VENT' AND CODIGO_CONCEPTO = 'COB' AND CODIGO_ENTIDAD = :codigoCliente"""
                    sql02 = oracle.consult(sql02, {'documentoString':documentoString, 'codigoCliente':invoice['CLIENTE']})
                    if sql02 is not None and len(sql02) > 0:
                        saleLine, created = InvoicesSales.objects.get_or_create(documento=documentoString, ejercicio=yearString)
                        save_line_invoice_line(saleLine, sql02[0]['FECHA_ASIENTO_MANO'], currentDate, invoice, invoice['LIQUIDO_FACTURA'], invoice['LIQUIDO_FACTURA'])
                    else:
                        saleLine, created = InvoicesSales.objects.get_or_create(documento=documentoString, ejercicio=yearString)
                        save_line_invoice_line(saleLine, "", currentDate, invoice, invoice['LIQUIDO_FACTURA'], 0)
            else:

                saleLine, created = InvoicesSales.objects.get_or_create(documento=documentoString, ejercicio=yearString)
                # print(invoice)

                # cobrado total para las facturas que se pagan en veces:
                sqlCobradoTotal = """SELECT NVL(SUM(hc.IMPORTE_COBRADO), 0) AS IMPORTE_COBRADO FROM HISTORICO_COBROS hc WHERE hc.DOCUMENTO = :documentoString"""
                sqlCobradoTotal = oracle.consult(sqlCobradoTotal, {'documentoString':documentoString}) or []
                

                # solo parcialmente cobrada FL1/000011
                if len(sqlCobradoTotal) > 0 and float(sqlCobradoTotal[0]['IMPORTE_COBRADO'] or 0) > 0: # float(invoice['IMPORTE_COBRADO'] or 0)
                    invoice['IMPORTE_COBRADO'] = float(sqlCobradoTotal[0]['IMPORTE_COBRADO'])
                
                # cobrado en veces G14
                sqlCobradoGiro = """SELECT NVL(SUM(IMPORTE), 0) AS IMPORTE_COBRADO FROM HISTORICO_DETALLADO_APUNTES hda WHERE hda.DOCUMENTO = :documentoString AND DIARIO = 'BANC' AND CODIGO_CONCEPTO = 'REM' AND CODIGO_ENTIDAD = :codigoCliente"""
                sqlCobradoGiro = oracle.consult(sqlCobradoGiro, {'documentoString':documentoString, 'codigoCliente':invoice['CLIENTE']}) or []
                

                if len(sqlCobradoGiro) > 0 and float(sqlCobradoGiro[0]['IMPORTE_COBRADO'] or 0) > float(invoice['IMPORTE_COBRADO'] or 0):
                    invoice['IMPORTE_COBRADO'] = float(sqlCobradoGiro[0]['IMPORTE_COBRADO'])

                # soluciono problema facturas tipo FR1/001564 con "IMPORTE_COBRADO_2": "-0.01",
                if len(str(invoice['FECHA_ASIENTO_COBRO'])) == 10 and float(invoice['IMPORTE_COBRADO_2'] or 0) < 0 and float(invoice['IMPORTE_COBRADO'] or 0) == 0:
                    invoice['IMPORTE_COBRADO'] = invoice['LIQUIDO_FACTURA']

                # soluciono problema facturas tipo FR1/000499 con "IMPORTE_COBRADO": 236.26, "IMPORTE_COBRADO_2": "376.07",
                if len(str(invoice['FECHA_ASIENTO_COBRO'])) == 10 and float(invoice['IMPORTE_COBRADO_2'] or 0) > float(invoice['IMPORTE_COBRADO'] or 0):
                    invoice['IMPORTE_COBRADO'] = invoice['IMPORTE_COBRADO_2']
    
                # solicion para la factura FR1/007183 FR1/009812 
                sqlMovCartera = """select NVL(SUM(IMPORTE_COBRADO), 0) AS IMPORTE_COBRADO, 
                                        NVL(SUM(IMPORTE_SUSTITUIDO), 0) AS IMPORTE_SUSTITUIDO 
                                        FROM HISTORICO_MOV_CARTERA 
                                        WHERE documento = :documentoString AND CODIGO_CLIENTE = :codigoCliente AND TIPO_MOVIMIENTO = 'CONSR'"""
                sqlMovCartera = oracle.consult(sqlMovCartera, {'documentoString': documentoString, 'codigoCliente': invoice['CLIENTE'] }) or []

                if len(sqlMovCartera) > 0 and (float(sqlMovCartera[0]['IMPORTE_COBRADO'] or 0) >= float(invoice['LIQUIDO_FACTURA'] or 0) or float(sqlMovCartera[0]['IMPORTE_SUSTITUIDO'] or 0) >= float(invoice['LIQUIDO_FACTURA'] or 0) - 22):
                    invoice['IMPORTE_COBRADO_MOV']    = float(sqlMovCartera[0]['IMPORTE_COBRADO'] or 0)
                    invoice['IMPORTE_SUSTITUIDO_MOV'] = float(sqlMovCartera[0]['IMPORTE_SUSTITUIDO'] or 0)
                    if float(sqlMovCartera[0]['IMPORTE_SUSTITUIDO'] or 0) >= float(sqlMovCartera[0]['IMPORTE_COBRADO'] or 0):
                        invoice['IMPORTE_COBRADO'] = float(invoice['LIQUIDO_FACTURA'] or 0)
                    else:
                        invoice['IMPORTE_COBRADO'] = float(invoice['LIQUIDO_FACTURA'] or 0)

                # FR1/001533 ?¿
                sqlPorCuenta = """select NVL(SUM(IMPORTE), 0) AS IMPORTE_COBRADO_CUENTA 
                                from HISTORICO_DETALLADO_APUNTES where documento = :documentoString AND signo='H' AND CODIGO_ENTIDAD = :codigoCliente 
                                    and CODIGO_CUENTA IN (4300010,4300011,4300020,4300030,4300040,4300090,4309010,4310010,4310020,4310030,4310040,4311010,4312000,4315010,4315020,4360010,4360020,4360030,4360040,4380000,4380020)"""
                sqlPorCuenta = oracle.consult(sqlPorCuenta, {'documentoString': documentoString, 'codigoCliente': invoice['CLIENTE'] }) or []
                
                if len(sqlPorCuenta) > 0 and float(sqlPorCuenta[0]['IMPORTE_COBRADO_CUENTA'] or 0) >= float(invoice['LIQUIDO_FACTURA'] or 0):
                    invoice['IMPORTE_COBRADO'] = float(invoice['LIQUIDO_FACTURA'] or 0)          

                Factura_Viva = 'N'
                if float(invoice['IMPORTE_COBRADO'] or 0) != float(invoice['LIQUIDO_FACTURA'] or 0):
                    # damos por cobrada si ya no hay nada vivo
                    sqlFactViva = """SELECT * FROM HISTORICO_COBROS hc WHERE hc.DOCUMENTO = :documentoString"""
                    sqlFactViva = oracle.consult(sqlFactViva, {'documentoString':documentoString}) or []
                    if len(sqlFactViva) > 0:
                        for sqlF in sqlFactViva:
                            if sqlF['DOCUMENTO_VIVO'] == 'S':
                                Factura_Viva = 'S'
                
                invoice['DOCUMENTO_VIVO'] = Factura_Viva

                save_line_invoice_line(saleLine, invoice['FECHA_ASIENTO_COBRO'], currentDate, invoice, invoice['LIQUIDO_FACTURA'], invoice['IMPORTE_COBRADO'])





            # x += [invoice]
            numInvoices += 1

    

    oracle.close()
    return numInvoices





"""
FX1/000035 -- 2 vencimiento sin pagar y mill items
FN1/000067 -- sin cobrar , documento en vivo
FN1/000068 -- sin cobrar , documento en vivo
FN1/000757 -- COBRADO "DOCUMENTO_VIVO": "N"


"""