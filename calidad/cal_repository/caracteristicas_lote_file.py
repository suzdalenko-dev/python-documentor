from froxa.utils.connectors.libra_connector import OracleConnector


def caracteristicas_lote(request):
    palet   = str(request.GET.get('palet') or '').strip()
    article = str(request.GET.get('article') or '').strip()

    sql_add = ''

    if len(palet) >= 1:
        sql_add = " AND stocks_detallado.numero_palet = '"+palet+"' "

    if len(article) >= 1:
        sql_add += " AND stocks_detallado.codigo_articulo = '"+article+"' "

    if sql_add == '':
        return {'res': []}

    oracle = OracleConnector()
    oracle.connect()

    sql = """SELECT 
                (SELECT clccl.valor_fecha_1
                   FROM stocks_detallado sdccl, caracteristicas_lotes clccl, TITULOS_PERSONALIZ tccl, articulos accl
                   WHERE sdccl.codigo_articulo = clccl.codigo_articulo
                     AND sdccl.codigo_empresa = clccl.codigo_empresa
                     AND sdccl.numero_lote_int = clccl.numero_lote_int
                     AND sdccl.codigo_empresa = '001'
                     AND sdccl.numero_palet = stocks_detallado.numero_palet
                     AND clccl.codigo_empresa = accl.codigo_empresa
                     AND clccl.codigo_articulo = accl.codigo_articulo
                     AND tccl.codigo_empresa = accl.codigo_empresa
                     AND tccl.codigo_personaliz = accl.codigo_personaliz_lotes
                     AND sdccl.cantidad_unidad1 > 0) AS fecha_congelacion,
                stocks_detallado.numero_palet,
                (SELECT DESCRIP_COMERCIAL FROM ARTICULOS WHERE CODIGO_ARTICULO = stocks_detallado.codigo_articulo AND ROWNUM <= 1) AS DESCRIP_COMERCIAL,
                  caracteristicas_lotes.codigo_articulo,
                  caracteristicas_lotes.numero_lote_int,
                  caracteristicas_lotes.valor_alfa_1,
                  caracteristicas_lotes.d_valor_alfa_1,
                  caracteristicas_lotes.valor_alfa_2,
                  caracteristicas_lotes.d_valor_alfa_2,
                  caracteristicas_lotes.valor_alfa_3,
                  caracteristicas_lotes.d_valor_alfa_3,
                  caracteristicas_lotes.valor_alfa_4,
                  caracteristicas_lotes.d_valor_alfa_4,
                  caracteristicas_lotes.valor_alfa_5,
                  caracteristicas_lotes.d_valor_alfa_5,
                  caracteristicas_lotes.valor_alfa_6,
                  caracteristicas_lotes.d_valor_alfa_6,
                  caracteristicas_lotes.valor_alfa_7,
                  caracteristicas_lotes.d_valor_alfa_7,
                  caracteristicas_lotes.valor_alfa_8,
                  caracteristicas_lotes.d_valor_alfa_8,
                  caracteristicas_lotes.valor_alfa_9,
                  caracteristicas_lotes.d_valor_alfa_9,
                  caracteristicas_lotes.valor_alfa_10,
                  caracteristicas_lotes.d_valor_alfa_10
            FROM STOCKS_DETALLADO,
               (SELECT CARACTERISTICAS_LOTES.*,
               (SELECT NVL(lvpti.descripcion, lvtpd.descripcion) 
                  FROM titulos_personaliz_des lvtpd, titulos_personaliz_des_idioma lvpti WHERE lvpti.valor(+) = lvtpd.valor 
                     AND lvpti.numero(+) = lvtpd.numero AND lvpti.codigo_personaliz(+) = lvtpd.codigo_personaliz 
                     AND lvpti.empresa(+) = lvtpd.empresa AND lvtpd.valor = CARACTERISTICAS_LOTES.VALOR_ALFA_1 AND lvtpd.numero = 1 
                     AND lvtpd.codigo_personaliz = (SELECT AR.CODIGO_PERSONALIZ_LOTES FROM ARTICULOS AR WHERE AR.CODIGO_ARTICULO = CARACTERISTICAS_LOTES.CODIGO_ARTICULO AND AR.CODIGO_EMPRESA = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) 
                     AND lvtpd.empresa = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) D_VALOR_ALFA_1,
                     (SELECT NVL(lvpti.descripcion, lvtpd.descripcion) FROM titulos_personaliz_des lvtpd, titulos_personaliz_des_idioma lvpti WHERE lvpti.valor(+) = lvtpd.valor AND lvpti.numero(+) = lvtpd.numero 
                     AND lvpti.codigo_personaliz(+) = lvtpd.codigo_personaliz AND lvpti.empresa(+) = lvtpd.empresa AND lvtpd.valor = CARACTERISTICAS_LOTES.VALOR_ALFA_2 AND lvtpd.numero = 2 
                     AND lvtpd.codigo_personaliz = (SELECT AR.CODIGO_PERSONALIZ_LOTES FROM ARTICULOS AR WHERE AR.CODIGO_ARTICULO = CARACTERISTICAS_LOTES.CODIGO_ARTICULO AND AR.CODIGO_EMPRESA = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) 
                     AND lvtpd.empresa = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) D_VALOR_ALFA_2,
                     (SELECT NVL(lvpti.descripcion, lvtpd.descripcion) FROM titulos_personaliz_des lvtpd, titulos_personaliz_des_idioma lvpti WHERE lvpti.valor(+) = lvtpd.valor AND lvpti.numero(+) = lvtpd.numero 
                     AND lvpti.codigo_personaliz(+) = lvtpd.codigo_personaliz AND lvpti.empresa(+) = lvtpd.empresa AND lvtpd.valor = CARACTERISTICAS_LOTES.VALOR_ALFA_3 AND lvtpd.numero = 3 
                     AND lvtpd.codigo_personaliz = (SELECT AR.CODIGO_PERSONALIZ_LOTES FROM ARTICULOS AR WHERE AR.CODIGO_ARTICULO = CARACTERISTICAS_LOTES.CODIGO_ARTICULO AND AR.CODIGO_EMPRESA = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) 
                     AND lvtpd.empresa = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) D_VALOR_ALFA_3,
                     (SELECT NVL(lvpti.descripcion, lvtpd.descripcion) FROM titulos_personaliz_des lvtpd, titulos_personaliz_des_idioma lvpti WHERE lvpti.valor(+) = lvtpd.valor AND lvpti.numero(+) = lvtpd.numero 
                     AND lvpti.codigo_personaliz(+) = lvtpd.codigo_personaliz AND lvpti.empresa(+) = lvtpd.empresa AND lvtpd.valor = CARACTERISTICAS_LOTES.VALOR_ALFA_4 AND lvtpd.numero = 4 
                     AND lvtpd.codigo_personaliz = (SELECT AR.CODIGO_PERSONALIZ_LOTES FROM ARTICULOS AR WHERE AR.CODIGO_ARTICULO = CARACTERISTICAS_LOTES.CODIGO_ARTICULO AND AR.CODIGO_EMPRESA = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) 
                     AND lvtpd.empresa = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) D_VALOR_ALFA_4,(SELECT NVL(lvpti.descripcion, lvtpd.descripcion) FROM titulos_personaliz_des lvtpd, titulos_personaliz_des_idioma lvpti WHERE lvpti.valor(+) = lvtpd.valor 
                     AND lvpti.numero(+) = lvtpd.numero AND lvpti.codigo_personaliz(+) = lvtpd.codigo_personaliz  AND lvpti.empresa(+) = lvtpd.empresa AND lvtpd.valor = CARACTERISTICAS_LOTES.VALOR_ALFA_5 
                     AND lvtpd.numero = 5 AND lvtpd.codigo_personaliz = (SELECT AR.CODIGO_PERSONALIZ_LOTES FROM ARTICULOS AR WHERE AR.CODIGO_ARTICULO = CARACTERISTICAS_LOTES.CODIGO_ARTICULO AND AR.CODIGO_EMPRESA = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) 
                     AND lvtpd.empresa = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) D_VALOR_ALFA_5,(SELECT NVL(lvpti.descripcion, lvtpd.descripcion) FROM titulos_personaliz_des lvtpd, titulos_personaliz_des_idioma lvpti WHERE lvpti.valor(+) = lvtpd.valor 
                     AND lvpti.numero(+) = lvtpd.numero AND lvpti.codigo_personaliz(+) = lvtpd.codigo_personaliz  AND lvpti.empresa(+) = lvtpd.empresa 
                     AND lvtpd.valor = CARACTERISTICAS_LOTES.VALOR_ALFA_6 AND lvtpd.numero = 6 AND lvtpd.codigo_personaliz = (SELECT AR.CODIGO_PERSONALIZ_LOTES FROM ARTICULOS AR WHERE AR.CODIGO_ARTICULO = CARACTERISTICAS_LOTES.CODIGO_ARTICULO 
                     AND AR.CODIGO_EMPRESA = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) AND lvtpd.empresa = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) D_VALOR_ALFA_6,(SELECT NVL(lvpti.descripcion, lvtpd.descripcion) 
                     FROM titulos_personaliz_des lvtpd, titulos_personaliz_des_idioma lvpti WHERE lvpti.valor(+) = lvtpd.valor AND lvpti.numero(+) = lvtpd.numero AND lvpti.codigo_personaliz(+) = lvtpd.codigo_personaliz 
                      AND lvpti.empresa(+) = lvtpd.empresa AND lvtpd.valor = CARACTERISTICAS_LOTES.VALOR_ALFA_7 AND lvtpd.numero = 7 
                     AND lvtpd.codigo_personaliz = (SELECT AR.CODIGO_PERSONALIZ_LOTES FROM ARTICULOS AR WHERE AR.CODIGO_ARTICULO = CARACTERISTICAS_LOTES.CODIGO_ARTICULO AND AR.CODIGO_EMPRESA = CARACTERISTICAS_LOTES.CODIGO_EMPRESA)
                      AND lvtpd.empresa = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) D_VALOR_ALFA_7,(SELECT NVL(lvpti.descripcion, lvtpd.descripcion) FROM titulos_personaliz_des lvtpd, titulos_personaliz_des_idioma lvpti WHERE lvpti.valor(+) = lvtpd.valor 
                      AND lvpti.numero(+) = lvtpd.numero AND lvpti.codigo_personaliz(+) = lvtpd.codigo_personaliz  AND lvpti.empresa(+) = lvtpd.empresa AND lvtpd.valor = CARACTERISTICAS_LOTES.VALOR_ALFA_8 
                      AND lvtpd.numero = 8 AND lvtpd.codigo_personaliz = (SELECT AR.CODIGO_PERSONALIZ_LOTES FROM ARTICULOS AR WHERE AR.CODIGO_ARTICULO = CARACTERISTICAS_LOTES.CODIGO_ARTICULO AND AR.CODIGO_EMPRESA = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) 
                      AND lvtpd.empresa = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) D_VALOR_ALFA_8,(SELECT NVL(lvpti.descripcion, lvtpd.descripcion) FROM titulos_personaliz_des lvtpd, titulos_personaliz_des_idioma lvpti WHERE lvpti.valor(+) = lvtpd.valor 
                      AND lvpti.numero(+) = lvtpd.numero AND lvpti.codigo_personaliz(+) = lvtpd.codigo_personaliz  AND lvpti.empresa(+) = lvtpd.empresa AND lvtpd.valor = CARACTERISTICAS_LOTES.VALOR_ALFA_9 
                      AND lvtpd.numero = 9 AND lvtpd.codigo_personaliz = (SELECT AR.CODIGO_PERSONALIZ_LOTES FROM ARTICULOS AR WHERE AR.CODIGO_ARTICULO = CARACTERISTICAS_LOTES.CODIGO_ARTICULO AND AR.CODIGO_EMPRESA = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) 
                      AND lvtpd.empresa = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) D_VALOR_ALFA_9,(SELECT NVL(lvpti.descripcion, lvtpd.descripcion) FROM titulos_personaliz_des lvtpd, titulos_personaliz_des_idioma lvpti WHERE lvpti.valor(+) = lvtpd.valor 
                      AND lvpti.numero(+) = lvtpd.numero AND lvpti.codigo_personaliz(+) = lvtpd.codigo_personaliz  AND lvpti.empresa(+) = lvtpd.empresa AND lvtpd.valor = CARACTERISTICAS_LOTES.VALOR_ALFA_10 
                      AND lvtpd.numero = 10 AND lvtpd.codigo_personaliz = (SELECT AR.CODIGO_PERSONALIZ_LOTES FROM ARTICULOS AR WHERE AR.CODIGO_ARTICULO = CARACTERISTICAS_LOTES.CODIGO_ARTICULO AND AR.CODIGO_EMPRESA = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) 
                      AND lvtpd.empresa = CARACTERISTICAS_LOTES.CODIGO_EMPRESA) D_VALOR_ALFA_10 FROM CARACTERISTICAS_LOTES) CARACTERISTICAS_LOTES WHERE (STOCKS_DETALLADO.CODIGO_ARTICULO=CARACTERISTICAS_LOTES.CODIGO_ARTICULO 
                      and STOCKS_DETALLADO.CODIGO_EMPRESA=CARACTERISTICAS_LOTES.CODIGO_EMPRESA and STOCKS_DETALLADO.NUMERO_LOTE_INT=CARACTERISTICAS_LOTES.NUMERO_LOTE_INT AND STOCKS_DETALLADO.CANTIDAD_UNIDAD1 > 0) 
                      AND (stocks_detallado.codigo_empresa = '001') 
                      AND ROWNUM <= 1111
                      """+sql_add+""" ORDER BY stocks_detallado.numero_palet DESC, stocks_detallado.codigo_articulo DESC"""
    
    res = oracle.consult(sql)
    oracle.close()

    return {'palet': palet, 'article': article, 'res': res}
    