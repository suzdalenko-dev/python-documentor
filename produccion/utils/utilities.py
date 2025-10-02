from django.http import JsonResponse

from froxa.utils.utilities.funcions_file import crear_excel_sin_pandas
from froxa.utils.utilities.smailer_file import SMailer


def add_article_costs_head(request):
  
    excel = [{'x': 'Costo', 'y': '1234567890'}, {'x': 'Precio', 'y': '0.9876543'}]
    file_url = crear_excel_sin_pandas(excel, '3', 'exemplo-excel')

    message_info = SMailer.send_email(
        ['alexey.suzdalenko@froxa.com'],
        'Excel ejemplo',
        'Excel ejemplo2',
        file_url[0]
    )

    return JsonResponse({'excel': excel, 'file_url': file_url})