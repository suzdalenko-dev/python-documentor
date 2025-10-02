import traceback
from django.http import JsonResponse
from compras.shop_repository.latest_arrivals_file import latest_arrivals
from compras.shop_repository.stock_calculation_file import stock_calculation
from froxa.utils.utilities.suzdal_logger import SuzdalLogger
from produccion.utils.sent_email_file import error_message_to_alexey


def defautl_shop_controller(request, action, entity, code, description): 

    action      = str(action).strip().lower()   
    entity      = str(entity).strip().lower()           
    code        = str(code).strip().lower()
    description = str(description).strip().lower()
    

    # <str:action>/<str:entity>/<str:code>/<str:description>/
    switch_query = {
        'latest_arrivals': lambda: latest_arrivals(request),      # http://127.0.0.1:8000/compras/get/0/0/latest_arrivals/
        'stock_calculation': lambda: stock_calculation(request),  # http://127.0.0.1:8000/compras/get/0/0/stock_calculation/
    }

    try:
        query_func = switch_query.get(description)
        result = query_func()
        return JsonResponse({"status": 200, 'message': 'ok', "data": result})
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        error_str = ''.join(traceback.format_exception(e))
        error_message_to_alexey(request, f"{e.__class__.__name__}: {e}\n{error_str}")
        SuzdalLogger.log(f"❌ Error en consulta: str{e} ❌")
        return JsonResponse({"status": 500,"message": "Ha ocurrido un error en el servidor.","error": str(e)}, status=500)