
from django.http import JsonResponse
from documentor.dom_repo.default_repo import first_function
from mainapp.utils.utilities.suzdal_logger import SuzdalLogger


def documentor_switcher(request, entity, code, description):

    SuzdalLogger.log(request.get_full_path())
    entity      = str(entity).strip().lower()
    code        = str(code).strip().lower()
    description = str(description).strip().lower()

    switch_query = {
        'first_function': lambda: first_function(request),            # http://127.0.0.1:8000/documentor/0/0/first_function/
        
    }

    try:
        query_func = switch_query.get(description)
        result = query_func()
        return JsonResponse({"status": 200, 'message': 'ok', "data": result})
    
    except Exception as e:
        SuzdalLogger.log(f"❌ Error en consulta: str{e} ❌")
        return JsonResponse({"status": 500,"message": "Ha ocurrido un error en el servidor.","error": str(e)}, status=500)

