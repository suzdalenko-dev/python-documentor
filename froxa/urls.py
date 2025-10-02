from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from calidad.cal_controllers.calidad_controller import calidad_default_controller
from compras.shopping_controllers.def_shop_controller import defautl_shop_controller
from finanzas.fin_controllers.fin_default_controller_file import fin_default_controller
from froxa.controllers.login_controller import login_function
from logistica.logistica_controllers.logistica_default_controller import log_default_controller
from powerbi.bi_controllers.default_bi_controller_file import bi_default_contoller
from produccion.controller.produccion_defalt_controller import production_default_controller
from produccion.utils.utilities import add_article_costs_head
from zzircon.zz_contollers.zz_controller import zz_production_function

def api_test(request):
    return JsonResponse({"mensaje": "Django pero que pasa aqui"})



urlpatterns = [
    path('zzircon/<str:entity>/<str:code>/<str:description>/', zz_production_function),
    path('calidad/<str:action>/<str:entity>/<str:code>/<str:description>/', calidad_default_controller),
    path('produccion/<str:action>/<str:entity>/<str:code>/<str:description>/', production_default_controller),
    path('finanzas/<str:action>/<str:entity>/<str:code>/<str:description>/', fin_default_controller),
    path('logistica/<str:action>/<str:entity>/<str:code>/<str:description>/', log_default_controller),
    path('compras/<str:action>/<str:entity>/<str:code>/<str:description>/', defautl_shop_controller),
    path('powerbi/<str:action>/<str:entity>/<str:code>/<str:description>/', bi_default_contoller),
    path('froxa/login/', login_function),

    path('produccion_add_articules/', add_article_costs_head), # http://127.0.0.1:8000/produccion_add_articules/
]

# hola hola