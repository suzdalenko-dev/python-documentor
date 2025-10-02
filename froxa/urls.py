from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from froxa.controllers.login_controller import login_function
from zzircon.zz_contollers.zz_controller import zz_production_function

def api_test(request):
    return JsonResponse({"mensaje": "Django pero que pasa aqui"})



urlpatterns = [
    path('zzircon/<str:entity>/<str:code>/<str:description>/', zz_production_function),
    path('calidad/<str:action>/<str:entity>/<str:code>/<str:description>/', calidad_default_controller),
    path('produccion/<str:action>/<str:entity>/<str:code>/<str:description>/', production_default_controller),
    path('finanzas/<str:action>/<str:entity>/<str:code>/<str:description>/', fin_default_controller),
    path('logistica/<str:action>/<str:entity>/<str:code>/<str:description>/', log_default_controller),
    path('froxa/login/', login_function),

]

# hola hola