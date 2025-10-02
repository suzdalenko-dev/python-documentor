from froxa.utils.utilities.funcions_file import get_current_date
from froxa.utils.utilities.smailer_file import SMailer


def aviso_expediente_sin_precio(request, expedientes_sin_precio):

    is_shoppig = str(request.GET.get('shopping')).strip()

    if expedientes_sin_precio and len(expedientes_sin_precio) > 0 and is_shoppig == 'true':

        lista_expedientes = ", ".join(map(str, expedientes_sin_precio))
        
        body_message = f"""<h1>Aviso Libra - Expedientes sin precio final</h1>
                <p>Hola, estos expedientes no tienen gastos imputados:</p>
                <p><strong>{lista_expedientes}</strong></p>
        """
        
        SMailer.send_email(
            ['kateryna.kosheleva@froxa.com', 'alejandra.ungidos@froxa.com', 'alexey.suzdalenko@froxa.com'],
            'Expedientes sin precio final ( sin gastos imputados ) hay que imputar gastos en todas las hojas de seguimiento',
            body_message,
            'none'
        )

        # ['kateryna.kosheleva@froxa.com', 'alejandra.ungidos@froxa.com', 'alexey.suzdalenko@froxa.com'],
        # ['alexey.suzdalenko@froxa.com'],
        # D:\froxa-backend\produccion\utils\sent_email_file.py



def error_message_to_alexey(request, message):
    full_url = request.build_absolute_uri()
    body_message = f"""<p><strong>{full_url}</strong></p>
                       <p><strong>{str(message)}</strong></p>"""
    SMailer.send_email(
            ['alexey.suzdalenko@froxa.com'],
            'Error App Informes',
            body_message,
            'none'
        )