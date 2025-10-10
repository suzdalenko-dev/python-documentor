
from django.http import JsonResponse
from documentor.dom_repo.doc_public import all_doc
from documentor.dom_repo.tags_functions import all_tags
from mainapp.utils.utilities.suzdal_logger import SuzdalLogger


def public_switcher(request, entity, code, description):

    SuzdalLogger.log(request.get_full_path())
    entity      = str(entity).strip().lower()
    code        = str(code).strip().lower()
    description = str(description).strip().lower()

    switch_query = {
        'all_tags': lambda: all_tags(request),                  # http://127.0.0.1:8000/public/tag/get/all_tags/
        'all_doc': lambda: all_doc(request),                    # http://127.0.0.1:8000/public/doc/get/all_doc/





    }

    try:
        query_func = switch_query.get(description)
        result     = query_func()
        return JsonResponse({"status": 200, 'message': 'ok', "data": result})
    
    except Exception as e:
        SuzdalLogger.log(f"❌ Error en consulta: str{e} ❌")
        return JsonResponse({"status": 500,"message": "Ha ocurrido un error en el servidor.","error": str(e)}, status=500)

