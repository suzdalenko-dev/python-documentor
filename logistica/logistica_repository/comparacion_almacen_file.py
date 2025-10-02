from froxa.utils.connectors.libra_connector import OracleConnector
from logistica.logistica_functions.fun_comparacion_almacen_98 import get_expediente_almacen_98, get_stock, get_textos, get_valor_cambio


def comparacion_almacen_98(request):
    oracle = OracleConnector()
    oracle.connect()
    out = []

    valor_cambio = get_valor_cambio(request, oracle)    
    expedinte_98 = get_expediente_almacen_98(request, oracle, valor_cambio)

    for r in expedinte_98:
        textos = get_textos(request, oracle, r['NUMERO_DOC_EXT'], valor_cambio)
        stock  = get_stock(request, oracle, r['NUMERO_DOC_EXT'], valor_cambio)
        out += [{'exped': r, 'textos': textos, 'stock': stock}] 
    
    for o in out:
        importe_textos_and_stock = 0
        for t in o['textos']:
            importe_textos_and_stock += float(t['IMPORTE_TOTAL_EUR'])
        for s in o['stock']:
            importe_textos_and_stock += float(s['IMPORTE_TOTAL_EUR'])
        o['exped']['IMPORTE_TEXTOS_AND_STOCK'] = importe_textos_and_stock

    oracle.close()
    return out












