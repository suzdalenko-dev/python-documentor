
from django.http import JsonResponse
from documentor.dom_repo.doc_functions import doc_by_id
from documentor.dom_repo.pb_doc_public import all_doc
from documentor.dom_repo.pb_expied_functions import exp_doc
from documentor.dom_repo.pb_tags_functions import get_my_tags, get_tags_dep
from documentor.dom_repo.serve_doc_functions import serve_document
from mainapp.utils.utilities.suzdal_logger import SuzdalLogger


def public_switcher(request, entity, code, description):

    SuzdalLogger.log(request.get_full_path())
    entity      = str(entity).strip().lower()
    code        = str(code).strip().lower()
    description = str(description).strip().lower()


    if description == 'serve_document':
        # http://127.0.0.1:8000/public/doc/get/serve_document/      
        return serve_document(request)


    switch_query = {
        'get_my_tags': lambda: get_my_tags(request),                # http://127.0.0.1:8000/public/tag/get/all_tags/
        'get_tags_dep': lambda: get_tags_dep(request),              # http://127.0.0.1:8000/public/tag/get/get_tags_dep/

        'all_doc': lambda: all_doc(request),                        # http://127.0.0.1:8000/public/doc/get/all_doc/
        'doc_by_id': lambda: doc_by_id(request),                    # http://127.0.0.1:8000/public/doc/get/doc_by_id/
        'exp_doc': lambda: exp_doc(request),                        # http://127.0.0.1:8000/public/doc/get/exp_doc/
    }

    try:
        query_func = switch_query.get(description)
        result     = query_func()
        return JsonResponse({"status": 200, 'message': 'ok', "data": result})
    
    except Exception as e:
        SuzdalLogger.log(f"❌ Error en consulta: str{e} ❌")
        return JsonResponse({"status": 500,"message": "Ha ocurrido un error en el servidor.","error": str(e)}, status=500)

