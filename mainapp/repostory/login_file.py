import random
from django.http import JsonResponse
from mainapp.models import Users
from mainapp.utils.utilities.funcions_file import get_client_ip, get_current_date, get_keys
from mainapp.utils.utilities.jwt_file import JWTManager
from mainapp.utils.utilities.smailer_file import SMailer


def login(request):
    action     = request.POST.get('action')     or ""
    username   = request.POST.get('username')   or ""
    password   = request.POST.get('password')   or ""
    email_code = request.POST.get('email_code') or ""

    try:
        if action == 'login':
            user = Users.objects.filter(name=username).first()
            if not user:
                return {"status": 404, "message": "Usuario no encontrado."}
            if user.password != password:
                return {"status": 401, "message": "Contraseña incorrecta."}

            num_visitas = int(user.num_visit) if user.num_visit is not None else 0
            currentIp = get_client_ip(request)
            if currentIp not in ['127.0.0.1x','192.168.1.131x']:
                if num_visitas == 0:
                    user.num_visit = 1
                    user.first_visit = get_current_date()
                else:
                    user.last_visit = get_current_date()
                    user.num_visit += 1
                    user.ip = user.ip or ''
                    if currentIp not in user.ip:
                        user.ip += currentIp + ' '

            # I am sending the email code from frontend
            # tiempo expiracion 1 dia
            if len(str(email_code)) > 1 and email_code != user.email_code:
                return {'id': user.id, 'aviso': 'codigo-incorrecto'} 
            
            if len(str(email_code)) > 1 and email_code == user.email_code:
                jwtm = JWTManager()
                payload = {"id": user.id, "username": user.name, "role": user.role, "permissions": user.permissions, 'action_pass': user.action_pass}
                token = jwtm.encode(payload, days=1) 
                user.email_code = '*'
                user.save()
                return {"id": user.id, "username": user.name, "role": user.role, "permissions": user.permissions, 'action_pass': user.action_pass, "token": token, 'aviso': 'codigo-correcto'}
          

            # user is login, next step send email code
            email_code       = f"{random.randint(0, 999999):06d}"
            user.email_code  = email_code 
            SMailer.send_email([user.email],'Código login DOCUMENTOR', 'Código login DOCUMENTOR '+email_code, None)
            user.save()
            return {"id": user.id, "username": user.name, "role": user.role, "permissions": user.permissions, 'action_pass': user.action_pass, 'aviso': 'credenciales-correctos'}
    
        return {}

    except Exception as e:
        return { "status": 500, "message": "Error interno del servidor", "error": str(e)}
    


def token_role_permissions(request):
    """
    Extrae el token JWT del header Authorization, lo valida,
    y devuelve el rol y permisos del usuario si es correcto.
    """
    try:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return {"status": 200, "message": "Token no enviado", "token": "no"}

        token = auth_header.split(" ")[1].strip()
        jwtm  = JWTManager()
        ok, payload = jwtm.decode(token)

        if not ok or payload is None:
            return {"status": 200, "message": "Token inválido o expirado", "token": "no"}

        id = payload.get("id")
        user = Users.objects.filter(id=id).first()

        return {"token": "ok", "message": "Token valido", "username": user.name, "role": user.role, "permissions": user.permissions, 'action_pass': user.action_pass, "id": user.id}
        

    except Exception as e:
        return {"status": 500, "message": "Error al verificar token"+str(e), "token": "no"}