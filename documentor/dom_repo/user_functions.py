from mainapp.models import Users


def get_user_email(request, payload):
    user_id = payload.get("user_id")
    user  = Users.objects.get(id=int(user_id))
    return {'email': user.email}