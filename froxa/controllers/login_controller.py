from django.http import JsonResponse
from froxa.models import Userfroxa
from froxa.utils.utilities.funcions_file import get_client_ip, get_current_date
from froxa.utils.utilities.suzdal_logger import SuzdalLogger


def login_function(request): 
    action   = request.POST.get('action') or request.GET.get('action')
    username = request.POST.get('username') or request.GET.get('username')
    password = request.POST.get('password') or request.GET.get('password')

    try:
        if action == 'login':
            user = Userfroxa.objects.filter(name=username).first()
            if not user:
                return JsonResponse({"status": 404, "message": "Usuario no encontrado."})
            if user.password != password:
                return JsonResponse({"status": 401, "message": "Contraseña incorrecta."})

            num_visitas = int(user.num_visit) if user.num_visit is not None else 0
            currentIp = get_client_ip(request)
            if currentIp not in ['127.0.0.1','192.168.1.131']:
                if num_visitas == 0:
                    user.num_visit = 1
                    user.first_visit = get_current_date()
                else:
                    user.last_visit = get_current_date()
                    user.num_visit += 1
                    user.ip = user.ip or ''
                    if currentIp not in user.ip:
                        user.ip += currentIp + ' '
            
            user.save()

            return JsonResponse({"data": {"username": user.name, "role": user.role, "permissions": user.permissions, "id": user.id, 'action_pass': user.action_pass}})
    
        return JsonResponse({"data": {}})

    except Exception as e:
        return JsonResponse({ "status": 500, "message": "Error interno del servidor", "error": str(e)}, status=500)


