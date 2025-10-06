from django.urls import path
from django.http import JsonResponse
from mainapp.controllers.login_controller import login_switcher
from documentor.documentor_controllers.default_controller import documentor_switcher

def api_test(request):
    return JsonResponse({"mensaje": "Django pero que pasa aqui"})



urlpatterns = [
    path('documentor/<str:entity>/<str:code>/<str:description>/', documentor_switcher),
    path('mainapp/<str:route_name>/', login_switcher),


]