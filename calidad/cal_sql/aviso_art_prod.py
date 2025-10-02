def ofs_activas(oracle):
        sql = """SELECT ofc.ORDEN_DE_FABRICACION,
                    ofc.CODIGO_ARTICULO AS ARTICULO_FABRICADO,
                    (SELECT art.DESCRIP_COMERCIAL FROM articulos art WHERE art.codigo_articulo = ofc.CODIGO_ARTICULO) D_ARTICULO_FABRICADO,
                    EJERCICIO_PERIODO
                FROM ORDENES_FABRICA_CAB ofc
                WHERE ofc.SITUACION_OF = 'A'"""
    
        ofs = oracle.consult(sql) or []
        return ofs

# llega 1229

def ingredients_in_the_recipe(oracle, of_id):
        sql = """SELECT
                    c.NUM_LINEA, 
                    c.CODIGO_ARTICULO_COMPO CODIGO_ENGREDIENTE,
                    (SELECT art.DESCRIP_COMERCIAL FROM articulos art WHERE art.codigo_articulo = c.CODIGO_ARTICULO_COMPO) D_INGREDIENTE
                FROM   ORDENES_FABRICA_CAB ofc, ESTRUCTURAS_COMPO c, ESTRUCTURAS_CAB h
                WHERE ofc.ORDEN_DE_FABRICACION = :of_id
                    AND ofc.CODIGO_ARTICULO    = c.CODIGO_ARTICULO
                    AND ofc.CODIGO_ORG_PLANTA = h.CODIGO_ORG_PLANTA
                    AND ofc.CODIGO_EMPRESA    = h.CODIGO_EMPRESA
                    AND c.CODIGO_EMPRESA      = h.CODIGO_EMPRESA
                    AND c.CODIGO_ORG_PLANTA   = h.CODIGO_ORG_PLANTA
                    AND c.CODIGO_ARTICULO     = h.CODIGO_ARTICULO
                    AND c.CODIGO_PRESENTACION = h.CODIGO_PRESENTACION
                    AND c.VERSION_ESTRU       = h.VERSION_ESTRU
                    AND h.SITU_ESTRU = 'V'
                    AND  TRUNC(SYSDATE) BETWEEN TRUNC(h.FECHA_VALIDEZ_DESDE) AND TRUNC(h.FECHA_VALIDEZ_HASTA)"""
        
        ingredients = oracle.consult(sql, {'of_id': of_id}) or []
        return ingredients



def get_equivalents(oracle, article_code, line_id):
        sql = """select CODIGO_ARTICULO_EQUIV
                from ESTRUCTURAS_COMPO_EQUIV
                where CODIGO_ARTICULO = :article_code AND NUM_LINEA = :line_id"""
        equivalents = oracle.consult(sql, {'article_code': article_code, 'line_id': line_id}) or []
        return equivalents


def used_in_factory(oracle, of_id, year_number):
        sql = """select orden_de_fabricacion,
                       codigo_componente,
                       ( select descrip_comercial from articulos where codigo_empresa = ordenes_fabrica_compo.codigo_empresa and codigo_articulo = ordenes_fabrica_compo.codigo_componente) compo_desc_comercial
                from ordenes_fabrica_compo
                where codigo_empresa = '001'and orden_de_fabricacion = :of_id and ejercicio = :year_number"""
        used = oracle.consult(sql, {'of_id': of_id, 'year_number': year_number}) or []
        return used