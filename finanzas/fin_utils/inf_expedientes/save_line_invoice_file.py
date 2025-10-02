from datetime import datetime

from froxa.utils.utilities.funcions_file import get_current_date, get_short_date

def save_line_invoice_line(invoiceLine, chargeDate, currentDate, sqlRes, importe, importeCobrado):
    invoiceLine.updated           = get_current_date()
    invoiceLine.codigo_cliente    = sqlRes['CLIENTE']
    invoiceLine.cliente           = sqlRes['NOMBRE_CLIENTE']
    invoiceLine.org_comercial     = sqlRes['DESCRIPCION_ORG_COMER']
    invoiceLine.agente            = sqlRes['NOMBRE_AGENTE']
    invoiceLine.forma_cobro       = sqlRes['FORMA_COBRO']
    
    invoiceLine.fecha_factura     = sqlRes['FECHA_FACTURA']
    invoiceLine.fecha_vencimiento = sqlRes['FECHA_VENCIMIENTO']
    invoiceLine.fecha_cobro       = str(chargeDate)[:10]

    invoiceLine.importe           = float(importe or 0)
    
    importe_cobrado_real          = float(importeCobrado or 0)
    if float(importeCobrado or 0) > float(importe or 0):
        importe_cobrado_real      = float(importe or 0)
    invoiceLine.importe_cobrado   = importe_cobrado_real

    porcentaje_cobrado = (invoiceLine.importe_cobrado / invoiceLine.importe) * 100
    if invoiceLine.importe - 1 <= invoiceLine.importe_cobrado and invoiceLine.importe > 0 and invoiceLine.importe_cobrado > 0:
        invoiceLine.status_cobro = 'COBRADO'
    elif porcentaje_cobrado >= 85:
        invoiceLine.status_cobro = 'COBRADO'
    elif invoiceLine.importe > 0 and invoiceLine.importe_cobrado > 0:
        invoiceLine.status_cobro = 'PARCIAL'
    else:
        invoiceLine.status_cobro = 'PENDIENTE'

    if len(str(invoiceLine.fecha_factura)) == 10 and len(str(invoiceLine.fecha_cobro)) == 10:
        fecha_factura_dt = datetime.strptime(invoiceLine.fecha_factura, '%Y-%m-%d')
        fecha_cobro_dt = datetime.strptime(invoiceLine.fecha_cobro, '%Y-%m-%d')
        invoiceLine.dias_real_pago = (fecha_cobro_dt - fecha_factura_dt).days
        if invoiceLine.dias_real_pago < 0:
            invoiceLine.dias_real_pago = 0

    if len(str(invoiceLine.fecha_vencimiento)) == 10 and len(str(invoiceLine.fecha_cobro)) == 10:
        fecha_factura_dt = datetime.strptime(invoiceLine.fecha_vencimiento, '%Y-%m-%d')
        fecha_cobro_dt = datetime.strptime(invoiceLine.fecha_cobro, '%Y-%m-%d')
        invoiceLine.dias_exceso    = (fecha_cobro_dt - fecha_factura_dt).days
        if invoiceLine.dias_exceso < 0:
            invoiceLine.dias_exceso = 0

    if len(str(invoiceLine.fecha_vencimiento)) == 10:
        current_date_dt = get_short_date()
        if str(invoiceLine.fecha_vencimiento) >= str(current_date_dt):
            invoiceLine.status_vencimiento = 'NO VENCIDO'
        else:
            invoiceLine.status_vencimiento = 'VENCIDO'

    if sqlRes['DOCUMENTO_VIVO'] == 'N' and len(str(invoiceLine.fecha_cobro)) == 10:
        invoiceLine.status_cobro    = 'COBRADO'
        invoiceLine.importe_cobrado = invoiceLine.importe

    invoiceLine.save()