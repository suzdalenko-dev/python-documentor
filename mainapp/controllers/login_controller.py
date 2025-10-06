from django.http import JsonResponse
from mainapp.repostory.login_file import login, token_role_permissions
from mainapp.utils.utilities.suzdal_logger import SuzdalLogger



def login_switcher(request, route_name): 
    
    switch_query = {
        'login':                    lambda: login(request),            
        'token_role_permissions':   lambda: token_role_permissions(request),            
    }

    try:
        query_func = switch_query.get(route_name)
        result = query_func()
        return JsonResponse({"data": result})
    
    except Exception as e:
        SuzdalLogger.log(f"❌ Error en consulta: str{e} ❌")
        return JsonResponse({"status": 500,"message": "Ha ocurrido un error en el servidor.","error": str(e)}, status=500)


