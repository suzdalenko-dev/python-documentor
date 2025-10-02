
from froxa.utils.connectors.libra_connector import OracleConnector

# info recipiente desde sql de la pagina vista 360 pestaña Stock
# la informacion coicide con el informe Radiofrecuencia > "Info. Recipiente"
# sql sacada por la conclusion propia ya que en la vista 360 no hay consulta


def info_recipiente_function(pal_code):
    sql = """select CODIGO_ALMACEN,
               D_CODIGO_ALMACEN,
               tipo_situacion AS TIPO_SITUACION,
               numero_lote_int AS NUMERO_LOTE_INT,
               numero_palet AS NUMERO_PALET,
               presentacion AS PRESENTACION,
               v_fecha_creacion AS FECHA_CREACION,
               v_fecha_caducidad AS FECHA_CADUCIDAD,
               bloqueo_invent AS BLOQUEO_INVENT,
               v_descripcion_lote AS NOMBRE_ARTICULO,
               codigo_articulo AS CODIGO_ARTICULO,
               cantidad_presentacion AS CANTIDAD,
               v_numero_ubicacion AS UBICACION
          from (
           select stocks_detallado.*,
                  null cantidad__barras,
                  (
                     select lval.nombre
                       from almacenes lval
                      where lval.almacen = stocks_detallado.codigo_almacen
                        and lval.codigo_empresa = stocks_detallado.codigo_empresa
                  ) D_CODIGO_ALMACEN,
                  (
                     select lvaz.descripcion
                       from almacenes_zonas lvaz
                      where lvaz.codigo_zona = stocks_detallado.codigo_zona
                        and lvaz.codigo_almacen = stocks_detallado.codigo_almacen
                        and lvaz.codigo_empresa = stocks_detallado.codigo_empresa
                  ) d_codigo_zona,
                  (
                     select lvprs.descripcion
                       from presentaciones lvprs
                      where lvprs.codigo = stocks_detallado.presentacion
                  ) d_presentacion,
                  decode(
                     stocks_detallado.numero_lote_int,
                     null,
                     null,
                     (
                        select lvhl.descripcion_lote
                          from historico_lotes lvhl
                         where lvhl.numero_lote_int = stocks_detallado.numero_lote_int
                           and lvhl.codigo_articulo = stocks_detallado.codigo_articulo
                           and lvhl.codigo_empresa = stocks_detallado.codigo_empresa
                     )
                  ) v_descripcion_lote,
                  decode(
                     numero_lote_int,
                     null,
                     decode(
                        numero_serie_int,
                        null,
                        null,
                        nvl(
                           (
                              select h.fecha_caducidad
                                from historico_series h
                               where h.codigo_articulo = stocks_detallado.codigo_articulo
                                 and h.numero_serie_int = stocks_detallado.numero_serie_int
                                 and h.codigo_empresa = stocks_detallado.codigo_empresa
                           ),
                           fecha_caducidad
                        )
                     ),
                     nvl(
                        (
                           select h.fecha_caducidad
                             from historico_lotes h
                            where h.codigo_articulo = stocks_detallado.codigo_articulo
                              and h.numero_lote_int = stocks_detallado.numero_lote_int
                              and h.codigo_empresa = stocks_detallado.codigo_empresa
                        ),
                        fecha_caducidad
                     )
                  ) v_fecha_caducidad,
                  decode(
                     numero_lote_int,
                     null,
                     decode(
                        numero_serie_int,
                        null,
                        null,
                        nvl(
                           (
                              select h.fecha_creacion
                                from historico_series h
                               where h.codigo_articulo = stocks_detallado.codigo_articulo
                                 and h.numero_serie_int = stocks_detallado.numero_serie_int
                                 and h.codigo_empresa = stocks_detallado.codigo_empresa
                           ),
                           fecha_creacion
                        )
                     ),
                     nvl(
                        (
                           select h.fecha_creacion
                             from historico_lotes h
                            where h.codigo_articulo = stocks_detallado.codigo_articulo
                              and h.numero_lote_int = stocks_detallado.numero_lote_int
                              and h.codigo_empresa = stocks_detallado.codigo_empresa
                        ),
                        fecha_creacion
                     )
                  ) v_fecha_creacion,
                  numero_ubicacion v_numero_ubicacion
             from stocks_detallado
        ) stocks_detallado
        where numero_palet = :pal_code and codigo_empresa = '001' and cantidad_presentacion != 0"""
    
    oracle = OracleConnector()
    oracle.connect()
    res = oracle.consult(sql, {"pal_code": pal_code})
    oracle.close()
    return res

            