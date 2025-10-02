from django.http import JsonResponse
from froxa.utils.utilities.suzdal_logger import SuzdalLogger
from produccion.repository.embarcado_con_sin_cont.embarcado_file import embarcado_art_con_sin_cont, embarcado_get_all
from produccion.repository.equivalents_price.create_update_eq_file import create_update_equivalents
from produccion.repository.equivalents_price.recalc_equi_file import recalculate_equiv_with_contaner
from produccion.repository.price_projection.article_costs_file import delete_article_costs_all, delete_ingrediente_line, get_all_excel_editables_lines, get_articles_libra, get_datail_art_cost, line_costs_delete_alternative, line_costs_save_alternative, line_costs_update_percentage, save_art_cost_head, save_new_ingrediente_line, update_excel_line
from produccion.repository.price_projection.recalculate_price_file import recalculate_price_projections
from produccion.repository.produccion_contab_file import produccion_vs_contabilidad
from produccion.utils.sent_email_file import error_message_to_alexey


def production_default_controller(request, action, entity, code, description): 

    action      = str(action).strip().lower()   
    entity      = str(entity).strip().lower()           
    code        = str(code).strip().lower()
    description = str(description).strip().lower()
    
    # <str:action>/<str:entity>/<str:code>/<str:description>/
    switch_query = {
        'recalculate_price_projections': lambda: recalculate_price_projections(request),  # http://127.0.0.1:8000/produccion/get/0/0/recalculate_price_projections/
        'get_all_excel_editables_lines': lambda: get_all_excel_editables_lines(request),  # http://127.0.0.1:8000/produccion/get/0/0/get_all_excel_editables_lines/
        'update_excel_line': lambda: update_excel_line(request),                          # http://127.0.0.1:8000/produccion/put/0/0/update_excel_line/
        'get_articles_libra': lambda: get_articles_libra(request),                        # http://127.0.0.1:8000/produccion/get/0/0/get_articles_libra/ 
        'save_art_cost_head': lambda: save_art_cost_head(request),                        # http://127.0.0.1:8000/produccion/get/0/0/save_art_cost_head/ 
        'get_datail_art_cost': lambda: get_datail_art_cost(request),                      # http://127.0.0.1:8000/produccion/get/0/0/get_datail_art_cost/
        'save_new_ingrediente_line': lambda: save_new_ingrediente_line(request),          # http://127.0.0.1:8000/produccion/get/0/0/save_new_ingrediente_line/
        'delete_ingrediente_line': lambda: delete_ingrediente_line(request),              # http://127.0.0.1:8000/produccion/get/0/0/delete_ingrediente_line/
        'line_costs_save_alternative': lambda: line_costs_save_alternative(request),      # http://127.0.0.1:8000/produccion/get/0/0/line_costs_save_alternative/
        'line_costs_update_percentage': lambda: line_costs_update_percentage(request),    # http://127.0.0.1:8000/produccion/put/0/0/line_costs_update_percentage/
        'line_costs_delete_alternative': lambda: line_costs_delete_alternative(request),  # http://127.0.0.1:8000/produccion/put/0/0/line_costs_delete_alternative/
        'delete_article_costs_all': lambda: delete_article_costs_all(request),            # http://127.0.0.1:8000/produccion/put/0/0/delete_article_costs_all/

        'create_update_equivalents': lambda: create_update_equivalents(request, action, entity, code), # http://127.0.0.1:8000/produccion/get/0/0/create_update_equivalents/
        'recalculate_equiv_with_contaner': lambda: recalculate_equiv_with_contaner(request),           # http://127.0.0.1:8000/produccion/get/0/0/recalculate_equiv_with_contaner/
        
        'embarcado_art_con_sin_cont': lambda: embarcado_art_con_sin_cont(request),                     # http://127.0.0.1:8000/produccion/get/0/0/embarcado_art_con_sin_cont/
        'embarcado_get_all': lambda: embarcado_get_all(request),                                       # http://127.0.0.1:8000/produccion/get/0/0/embarcado_get_all/

        'produccion_vs_contabilidad': lambda: produccion_vs_contabilidad(request),                     # http://127.0.0.1:8000/produccion/get/0/0/produccion_vs_contabilidad/
    }

    try:
        query_func = switch_query.get(description)
        result = query_func()
        return JsonResponse({"status": 200, 'message': 'ok', "data": result})
    except Exception as e:
        error_message_to_alexey(request, e)
        SuzdalLogger.log(f"❌ Error en consulta: str{e} ❌")
        return JsonResponse({"status": 500,"message": "Ha ocurrido un error en el servidor.","error": str(e)}, status=500)