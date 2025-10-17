
from django.http import JsonResponse
from documentor.dom_repo.doc_functions import create_new_doc
from documentor.dom_repo.tags_functions import create_tag, delete_tag, get_department_tags, get_user_tags
from documentor.dom_repo.user_functions import get_user_email
from mainapp.repostory.login_file import check_user_request
from mainapp.utils.utilities.suzdal_logger import SuzdalLogger


def documentor_switcher(request, entity, code, description):

    check_jwt, payload = check_user_request(request)
    if check_jwt == False:
        return JsonResponse({"status": 401, "message": "No autorizado, token invalido o expirado."}, status=401)

    SuzdalLogger.log(request.get_full_path())
    entity      = str(entity).strip().lower()
    code        = str(code).strip().lower()
    description = str(description).strip().lower()

    switch_query = {
        'create_tag': lambda: create_tag(request, payload),             # http://127.0.0.1:8000/documentor/tag/post/create_tag/
        'get_user_tags': lambda: get_user_tags(request, payload),
        'delete_tag': lambda: delete_tag(request, payload),
        'get_department_tags': lambda: get_department_tags(request, payload),

        
        'get_user_email': lambda: get_user_email(request, payload),


        'create_new_doc': lambda: create_new_doc(request, payload),
    }

    try:
        query_func = switch_query.get(description)
        result     = query_func()
        return JsonResponse({"status": 200, 'message': 'ok', "data": result})
    
    except Exception as e:
        SuzdalLogger.log(f"❌ Error en consulta: str{e} ❌")
        return JsonResponse({"status": 500,"message": "Ha ocurrido un error en el servidor.","error": str(e)}, status=500)

