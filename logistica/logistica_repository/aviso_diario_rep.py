



from froxa.utils.connectors.libra_connector import OracleConnector
from froxa.utils.utilities.funcions_file import crear_excel_sin_pandas, get_short_date, notify_logger
from froxa.utils.utilities.smailer_file import SMailer
from logistica.logistica_functions.fun_aviso_diario import get_containers_for_today
from logistica.logistica_functions.fun_comparacion_almacen_98 import get_stock, get_textos


def aviso_diario_comp_98(request):
    # aviso diario de los albaranes en el caso que el albaran 98 no tiene al menos 1 albaran correspondiente de almacen y 1 de gastos

    oracle = OracleConnector()
    oracle.connect()
    avisos = []
    out    = []
    
    containers = get_containers_for_today(oracle)

    for r in containers:
        textos = get_textos(request, oracle, r['NUMERO_DOC_EXT'], -1)
        stock  = get_stock(request, oracle, r['NUMERO_DOC_EXT'], -2)

        out += [{'exped': r, 'textos': textos, 'stock': stock }] # stock

    oracle.close()
    
    message = ''
    for o in out:
        if len(o['textos']) == 0 or len(o['stock']) == 0:
            if len(o['textos']) == 0:
                message += ' No encontramos albaran de gastos, '
            if len(o['stock']) == 0:
                message += ' No encontramos albaran de entrada almacén, '
            avisos += [{'Fecha': o['exped']['FECHA_SUPERVISION'],  'Doc. Exterior': o['exped']['NUMERO_DOC_EXT'],  'Doc. Interior': o['exped']['NUMERO_DOC_INTERNO'],  'Almacen': o['exped']['CODIGO_ALMACEN']+' '+o['exped']['D_ALMACEN'], 'Proveedor': o['exped']['CODIGO_PROVEEDOR']+' '+o['exped']['D_CODIGO_PROVEEDOR'],  'Aviso': message }]
            message = ''


    file_url = None
    if len(avisos)> 0:
        file_url = crear_excel_sin_pandas(avisos, '0', 'alm98')

        message_info = SMailer.send_email(
            ['almacen@froxa.com', 'alexey.suzdalenko@froxa.com'], # 'almacen@froxa.com' 'almacen@froxa.com', probar en produccion haber si llega el mensaje 'almacen@froxa.com',
            'Aviso Libra - Consulta Albaranes de compra',
            'Los albaranes de entrada del almacén 98 no coinciden con los albaranes de compra de los almacenes 00, 01, 02, E01, E02, E03, E04, E05, E06 y 25 <br><br> <a href="http://informes/dashboard/#almacen-importacion-vs-resto">Informe comparación albaranes 98</a>',
            file_url[0]
        )

        notify_logger(message_info)

    return {'avisos': avisos, 'file_url': file_url}