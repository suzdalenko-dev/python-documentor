from django.http import HttpResponse, JsonResponse
from froxa.utils.utilities.suzdal_logger import SuzdalLogger
from zzircon.zz_repository.article_detail_file import article_detail
from zzircon.zz_repository.bizerba_file import bizerba_recent_lines, five_minutes
from zzircon.zz_repository.info_recipiente_file import info_recipiente_function
from zzircon.zz_repository.of_abiertas_file import ofs_abiertas_function
from zzircon.zz_repository.of_de_palet_file import of_de_palet_function
from zzircon.zz_repository.of_detalle_file import of_detalle_function
from zzircon.zz_repository.of_en_uso_file import of_en_uso_function



def zz_production_function(request, entity, code, description):

    SuzdalLogger.log(request.get_full_path())
    entity      = str(entity).strip().lower()
    code        = str(code).strip().lower()
    description = str(description).strip().lower()

    switch_query = {
        'ofs_abiertas': lambda: ofs_abiertas_function(),            # http://127.0.0.1:8000/zzircon/of/0/ofs_abiertas/
        'ofs_en_uso': lambda: of_en_uso_function(),                 # http://127.0.0.1:8000/zzircon/of/0/ofs_en_uso/
        'of_detalle': lambda: of_detalle_function(code),            # http://127.0.0.1:8000/zzircon/of/381/of_detalle/
        'of_de_palet': lambda: of_de_palet_function(code),          # http://127.0.0.1:8000/zzircon/palet/000000096/of_de_palet/
        'info_recipiente': lambda: info_recipiente_function(code),  # http://127.0.0.1:8000/zzircon/palet/000000728/info_recipiente/
        'bizerba-5-minutes': lambda: five_minutes(),                # http://127.0.0.1:8000/zzircon/bizerba/0/bizerba-5-minutes/
        'bizerba_recent_lines': lambda: bizerba_recent_lines(code), # http://127.0.0.1:8000/zzircon/bizerba/10/bizerba_recent_lines/
        'article_detail': lambda : article_detail(code),            # http://127.0.0.1:8000/zzircon/article/all/article_detail/
    }

    try:
        query_func = switch_query.get(description)
        result = query_func()
        return JsonResponse({"status": 200, 'message': 'ok', "data": result})
    
    except Exception as e:
        SuzdalLogger.log(f"❌ Error en consulta: str{e} ❌")
        return JsonResponse({"status": 500,"message": "Ha ocurrido un error en el servidor.","error": str(e)}, status=500)

