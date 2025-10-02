import json
from froxa.utils.utilities.funcions_file import json_encode_one
from produccion.models import DetalleEntradasEquivCC, EquivalentsHead


def create_update_equivalents(request, action, entity, code):
    if action == 'get':
        equi = EquivalentsHead.objects.all().values('id', 'article_name', 'alternative', 'kg_act', 'price_act', 'kg0', 'price0', 'kg1', 'price1', 'kg2', 'price2', 'kg3', 'price3', 'precio_estandar_equival').order_by('id')
        equi = list(equi)
        return equi
    
    if action == 'create':
        name = str(request.POST.get('group_name')).strip()
        equiv, created = EquivalentsHead.objects.get_or_create(article_name=name)
        equiv.alternative = json.dumps([])
        equiv.save()

    if action == 'get_one':                                 # http://127.0.0.1:8000/produccion/get_one/0/2/create_update_equivalents/                        
        eqOne = EquivalentsHead.objects.get(id=code)
        eqOne = json_encode_one(eqOne)
        return eqOne
    
    if action == 'save_one':
        eqOne = EquivalentsHead.objects.get(id=code)
        eqOne.article_name = str(request.POST.get('group_name')).strip()
        eqOne.save()

    if action == 'save_item_equiv':                         # http://127.0.0.1:8000/produccion/save_item_equiv/0/0/create_update_equivalents/  
        eqOne = EquivalentsHead.objects.get(id=request.POST.get('id'))
        listEquiv = json.loads(eqOne.alternative)
        new_code = str(request.POST.get('code')).strip()
        new_name = str(request.POST.get('name')).strip()
        already_exists = any(item.get('code') == new_code for item in listEquiv)
        if not already_exists:
            listEquiv.append({'code': new_code, 'name': new_name})
            eqOne.alternative = json.dumps(listEquiv)
            eqOne.save()

    if action == 'delete_item':                             # http://127.0.0.1:8000/produccion/delete_item/0/0/create_update_equivalents/
        eqOne        = EquivalentsHead.objects.get(id=request.POST.get('id'))
        listEquiv    = json.loads(eqOne.alternative)
        delete_code  = str(request.POST.get('code')).strip()
        updated_list = [item for item in listEquiv if item.get('code') != delete_code]
        if len(updated_list) != len(listEquiv):
            eqOne.alternative = json.dumps(updated_list)
            eqOne.save()


    if action == 'get_structure':                          # http://127.0.0.1:8000/produccion/get_structure/0/0/create_update_equivalents/
        equi = DetalleEntradasEquivCC.objects.all().values('id', 'name', 'entrada', 'stock_actual', 'pcm_actual', 'consumo_prod', 'consumo_vent', 'entrada_kg', 'entrada_eur', 'calc_kg', 'calc_eur').order_by('id')
        equi = list(equi)
        return equi