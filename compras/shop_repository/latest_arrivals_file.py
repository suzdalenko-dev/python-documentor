from collections import defaultdict
from compras.only_sql.latest_arrivals_sql import get_latest_arrivals
from froxa.utils.connectors.libra_connector import OracleConnector


def latest_arrivals(request):
    oracle = OracleConnector()
    oracle.connect()

    res = get_latest_arrivals(request, oracle)
    

    no_cnt = [x for x in res if (x.get('CONTENEDOR') or '').upper() != 'CNT']
    si_cnt = [x for x in res if (x.get('CONTENEDOR') or '').upper() == 'CNT']
    ordered = no_cnt + si_cnt


    out = []
    contract_uniques = []

    for row in ordered:
        name = row['D_DESCRIPCION_EXPEDIENTE']+row['FECHA_PREV_LLEGADA']
        if name not in contract_uniques:
            contract_uniques += [name]
            out += [{'id':name, 'lines': []}]

    
    for o in out:
        for order in ordered:
            name = order['D_DESCRIPCION_EXPEDIENTE']+order['FECHA_PREV_LLEGADA']
            if o['id'] == name:
                o['lines'] += [order]


    oracle.close()
    
    return out

