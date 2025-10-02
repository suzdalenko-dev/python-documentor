from compras.only_sql.stock_sql import get_stok_data_sql
from froxa.utils.connectors.libra_connector import OracleConnector
from produccion.utils.get_me_stock_file import get_me_stock_now


def stock_calculation(request):
    oracle     = OracleConnector()
    oracle.connect()

    stock = get_stok_data_sql(request, oracle)
    return {'stock': stock}






"""
1. solo me interesa el DISPG DISPONIBLE GENERAL situacion del STOCK
pero no quite que muestre el select con C       AJUSTE STOCKS COMPRAS
                                        CADUC   CADUCADO
                                        CALID   CALIDAD / RETENIDO / SANIDAD
                                        DEPA    DEPOSITO ADUANERO
                                        DISPG   DISPONIBLE GENERAL !!!!
                                        FINAL

2. MERCADO 10 NACIONAL, 30 COMPARTIDO
3. TIPO MATERIAL 010 MATERIA PRIMA, 
                 030 PRODUCTO FABRICADO, 
                 040 PRODUCTO COMERCIAL
"""









"""
a las 11 de la noche aviso almacen@froxa.com

aviso a Gema de los palets que hay:
    Desde almacen: 90 PRODUCCION / FABRICA 
    Hasta almacen: 90 PRODUCCION / FABRICA

    Desde Codigo Entrada: PRODUCCION CODIGO ENTRADA MAQUILA FM
    Hasta cod. Entrada:   PRODUCCION CODIGO ENTRADA MAQUILA FM
"""