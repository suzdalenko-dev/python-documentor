from calidad.cal_sql.aviso_art_prod import get_equivalents, ingredients_in_the_recipe, ofs_activas, used_in_factory
from froxa.models import Notify
from froxa.utils.connectors.libra_connector import OracleConnector
from froxa.utils.utilities.funcions_file import crear_excel_sin_pandas, get_current_date
from froxa.utils.utilities.smailer_file import SMailer


def aviso_articulo_receta(request):
    oracle = OracleConnector()
    oracle.connect

    # 1. active manufacturing orders
    # ordenes fabricacion activas
    all_notice   = []
    sent_notice  = []
    message_info = []
    ofs          = ofs_activas(oracle)
    
    # 2. bring ingredientes
    for o in ofs:
        o['recipe_ingredients'] = ingredients_in_the_recipe(oracle, o['ORDEN_DE_FABRICACION'])


    # 3. bring possible equivalents
    for o1 in ofs:
        for ing in o1['recipe_ingredients']:
            ing['equivalents'] = get_equivalents(oracle, o1['ARTICULO_FABRICADO'], ing['NUM_LINEA'])


    # 4. put all items in use together in an array
    for o2 in ofs:
        all_in_use       = []
        for ing2 in o2['recipe_ingredients']:
            if ing2['CODIGO_ENGREDIENTE'] not in all_in_use:
                all_in_use += [ing2['CODIGO_ENGREDIENTE']]
                for equiv11 in ing2['equivalents']:
                    if equiv11['CODIGO_ARTICULO_EQUIV'] not in all_in_use:
                        all_in_use += [equiv11['CODIGO_ARTICULO_EQUIV']]

        o2['all_in_use'] = [all_in_use]


    # 5. bring items used in the factory for productions
    for o3 in ofs:
        o3['factory_used'] = used_in_factory(oracle, o3['ORDEN_DE_FABRICACION'], o3['EJERCICIO_PERIODO'])

    # 6. compparison between those used in the factory and in the recipe
    for o4 in ofs:
        array_all_in_use = []

        if len(o4['all_in_use']) > 0:
            array_all_in_use = o4['all_in_use'][0]
        
        for item_f in o4['factory_used']:
            if item_f['CODIGO_COMPONENTE'] not in array_all_in_use:
                notice = {'year': o4['EJERCICIO_PERIODO'], 'of': o4['ORDEN_DE_FABRICACION'], 'code_fab': o4['ARTICULO_FABRICADO'], 'd_fab': o4['D_ARTICULO_FABRICADO'], 'ing_code': item_f['CODIGO_COMPONENTE'], 'd_ing': item_f['COMPO_DESC_COMERCIAL']}
                all_notice += [notice]

    # 7. Check that the message has not been sent
    for i_notice in all_notice:
        line = Notify.objects.filter(year=i_notice['year'], of_id=i_notice['of'], art_notice=i_notice['ing_code']) or []
        if len(line) == 0:
            sent_notice += [{'OF': i_notice['of'], 'ARTICULO_FABRICADO': i_notice['code_fab']+' '+i_notice['d_fab'], 'INGREDIENTE_FUERA_DE_LA_RECETA': i_notice['ing_code']+' '+i_notice['d_ing']}]
            
        
    # 8. Sent email
    if len(sent_notice) > 0:
        file_url = crear_excel_sin_pandas(sent_notice, '1', 'aviso-artuculos-of-fuera-de-la-receta')
        message_info = SMailer.send_email(
            ['calidad@froxa.com', 'sara.fernandez@froxa.com', 'alexey.suzdalenko@froxa.com'],
            'Aviso Libra - Artículos empleados en OF no incluidos en la receta',
            'Aviso Libra - Artículos empleados en OF no incluidos en la receta',
            file_url[0]
        )
        for i_notice2 in all_notice:
            for m in message_info:
                line = Notify.objects.get_or_create(year=i_notice2['year'], of_id=i_notice2['of'], art_notice=i_notice2['ing_code'], email=m['email'])[0]
                line.email    = m['email']
                line.sent     = m['sent']
                line.message  = 'Aviso Libra - Artículos empleados en OF no incluidos en la receta'
                line.file     = m['file']
                line.time_log = get_current_date()
                line.save()

    oracle.close()
    return {'ofs': ofs, 'all_notice': all_notice, 'sent_notice': sent_notice, 'message_info': message_info}






