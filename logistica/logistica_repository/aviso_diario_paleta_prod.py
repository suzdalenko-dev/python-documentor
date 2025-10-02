from froxa.utils.connectors.libra_connector import OracleConnector
from froxa.utils.utilities.funcions_file import crear_excel_sin_pandas, notify_logger
from froxa.utils.utilities.smailer_file import SMailer
from logistica.logistica_functions.fun_aviso_pal_prod import get_list_palets_prod


def aviso_diario_paleta_produccion(request):
    # aviso diario sobre palets que pueden quedar en produccion

    oracle = OracleConnector()
    oracle.connect()
    palets = get_list_palets_prod(request, oracle) or []

    oracle.close()

    if len(palets) > 0:

        file_url = crear_excel_sin_pandas(palets, '1', 'aviso-palets-prod')

        message_info = SMailer.send_email(
            ['almacen@froxa.com', 'alexey.suzdalenko@froxa.com'],
            'Aviso Libra - Existen paletas en PRODUCCIÓN sin ubicar ',
            'Aviso Libra - Paletas en producción - almacén 90, código entrada PRODUCCION, tipo situación CALID',
            file_url[0]
        )

        notify_logger(message_info)

    return {'x': [], 'palets': palets}