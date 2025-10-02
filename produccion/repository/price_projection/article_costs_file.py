from datetime import datetime
import json
from froxa.utils.connectors.libra_connector import OracleConnector
from produccion.models import ArticleCostsHead, ArticleCostsLines, ExcelLinesEditable


def get_all_excel_editables_lines(request):
    excelLines = ExcelLinesEditable.objects.all().values('id', 'article_code', 'article_name', 'precio_padre_act', 'inicio_coste_act', 'rendimiento', 'precio_materia_prima', 'precio_aceite', 'precio_servicios', 'aditivos', 'mod', 'embalajes', 'amort_maq', 'moi', 'final_coste_act', 'final_coste_mas1', 'final_coste_mas2', 'final_coste_mas3', 'precio_padre_mas_gastos', 'precio_estandar', 'precio_estandar_con_gastos').order_by('article_name')
    excelLines = list(excelLines)
    return excelLines


# 40022
def update_excel_line(request):
    id               = request.POST.get('id')

    eEditable                  = ExcelLinesEditable.objects.get(id=id)
    eEditable.rendimiento      = float(request.POST.get('rendimiento') or 1)
    eEditable.precio_aceite    = float(request.POST.get('precio_aceite') or 0)
    eEditable.precio_servicios = float(request.POST.get('precio_servicios') or 0)
    eEditable.aditivos         = float(request.POST.get('aditivos') or 0)
    eEditable.mod              = float(request.POST.get('mod') or 0)
    eEditable.embalajes        = float(request.POST.get('embalajes') or 0)
    eEditable.amort_maq        = float(request.POST.get('amort_maq') or 0)
    eEditable.moi              = float(request.POST.get('moi') or 0)
   
    sum_editables = eEditable.precio_aceite + eEditable.precio_servicios + eEditable.aditivos + eEditable.mod + eEditable.embalajes + eEditable.amort_maq + eEditable.moi

    eEditable.precio_materia_prima    = eEditable.precio_padre_act / eEditable.rendimiento
    eEditable.precio_padre_mas_gastos = eEditable.precio_padre_act / eEditable.rendimiento + sum_editables
    eEditable.final_coste_act         = (float(eEditable.inicio_coste_act  or 0) / float(eEditable.rendimiento)) + sum_editables
    eEditable.final_coste_mas1        = (float(eEditable.inicio_coste_mas1 or 0) / float(eEditable.rendimiento)) + sum_editables
    eEditable.final_coste_mas2        = (float(eEditable.inicio_coste_mas2 or 0) / float(eEditable.rendimiento)) + sum_editables
    eEditable.final_coste_mas3        = (float(eEditable.inicio_coste_mas3 or 0) / float(eEditable.rendimiento)) + sum_editables
    eEditable.save()
    return {'res':'ok'}




def get_articles_libra(request):
    oracle = OracleConnector()
    oracle.connect()
    sql = """SELECT CODIGO_ARTICULO, DESCRIP_COMERCIAL FROM ARTICULOS"""
    res = oracle.consult(sql)
    oracle.close()
    return res



def save_art_cost_head(request):
    code = request.POST.get('code')
    name = request.POST.get('name')
    artHead, created = ArticleCostsHead.objects.get_or_create(article_code=code)
    artHead.article_name = name
    # if created:
    #     artHead.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    artHead.save()
    
    eEditable, created = ExcelLinesEditable.objects.get_or_create(article_code=code)
    eEditable.article_name = name
    eEditable.save()

    return {'code': artHead.article_code}



def get_datail_art_cost(request):
    code = request.GET.get('code')
    artHead  = ArticleCostsHead.objects.filter(article_code=code).values('id', 'article_code', 'article_name')
    artHead  = list(artHead)
    artLines = ArticleCostsLines.objects.filter(parent_article=code).values('id', 'parent_article', 'article_code', 'article_name', 'percentage', 'alternative').order_by('id')
    artLines = list(artLines)
    # exLines  = ExcelLinesEditable.objects.filter(article_code=code).values('article_code', 'article_name')
    # exLines  = list(exLines)

    return {'artHead':artHead, 'artLines':artLines}



def save_new_ingrediente_line(request):
    parent = request.POST.get('parent')
    code = request.POST.get('code')
    name = request.POST.get('name')
    artCost = ArticleCostsLines()
    artCost.parent_article = parent
    artCost.article_code   = code
    artCost.article_name   = name
    artCost.alternative    = json.dumps([])
    artCost.percentage     = 0
    artCost.save()
    return {'artCost':artCost.id}



def delete_ingrediente_line(request):
    lineCostId = request.GET.get('id')
    ArticleCostsLines.objects.filter(id=lineCostId).delete()
    return {'res':'ok'}



def line_costs_save_alternative(request):
    line_cost_id = request.POST.get('line_cost_id')
    code         = request.POST.get('code')
    name         = request.POST.get('name')

    artCost      = ArticleCostsLines.objects.get(id=line_cost_id)
    jsonData     = json.loads(artCost.alternative)
    jsonData    += [{'code':code, 'name':name }]
    artCost.alternative = json.dumps(jsonData)
    artCost.save()



def line_costs_update_percentage(request):
    line_id = request.GET.get('line_id')
    value   = request.GET.get('value')
    artCost = ArticleCostsLines.objects.get(id=line_id)
    artCost.percentage = float(value)
    artCost.save()



def line_costs_delete_alternative(request):
    id        = request.GET.get('id')
    code      = request.GET.get('code')
    artCosts  = ArticleCostsLines.objects.get(id=id)
    array_alt = json.loads(artCosts.alternative)
    array_alt = [alt for alt in array_alt if alt.get('code') != code]
    artCosts.alternative = json.dumps(array_alt)
    artCosts.save()
    



def delete_article_costs_all(request):
    code = request.GET.get('code')
    ArticleCostsHead.objects.filter(article_code=code).delete()
    ArticleCostsLines.objects.filter(parent_article=code).delete()
    ExcelLinesEditable.objects.filter(article_code=code).delete()