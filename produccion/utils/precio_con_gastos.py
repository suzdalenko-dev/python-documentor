def consultar_precio_con_gastos(oracle, exp_id, art_code, cantidad):
    sql = """select ( ( (
               select sum(hs.importe_portes)
                 from reparto_portes_hs hs
                where hs.codigo_empresa = expedientes_hojas_seguim.empresa
                  and hs.numero_expediente = expedientes_hojas_seguim.num_expediente
                  and hs.hoja_seguimiento = expedientes_hojas_seguim.num_hoja
                  and hs.codigo_articulo = expedientes_articulos_embarque.articulo
            ) / decode(
               articulos.unidad_valoracion,
               1,
               expedientes_articulos_embarque.cantidad_unidad1,
               2,
               expedientes_articulos_embarque.cantidad_unidad2
            ) ) + ( expedientes_articulos_embarque.precio * decode(
               expedientes_hojas_seguim.tipo_cambio,
               'E',
               decode(
                  expedientes_imp.cambio_asegurado,
                  'S',
                  expedientes_imp.valor_cambio,
                  'N',
                  1
               ),
               'S',
               expedientes_hojas_seguim.valor_cambio,
               'N',
               coalesce(
                  expedientes_hojas_seguim.valor_cambio,
                  expedientes_imp.valor_cambio,
                  1
               )
            ) ) ) n10
              from (
               select articulos.*
                 from articulos
            ) articulos,
                   (
                      select expedientes_imp.*
                        from expedientes_imp
                   ) expedientes_imp,
                   (
                      select expedientes_hojas_seguim.*
                        from expedientes_hojas_seguim
                   ) expedientes_hojas_seguim,
                   (
                      select expedientes_articulos_embarque.*
                        from expedientes_articulos_embarque
                   ) expedientes_articulos_embarque,
                   expedientes_contenedores
             where ( expedientes_contenedores.num_expediente = expedientes_articulos_embarque.num_expediente
               and expedientes_contenedores.num_hoja = expedientes_articulos_embarque.num_hoja
               and expedientes_contenedores.empresa = expedientes_articulos_embarque.empresa
               and expedientes_contenedores.linea = expedientes_articulos_embarque.linea_contenedor
               and expedientes_hojas_seguim.num_expediente = expedientes_articulos_embarque.num_expediente
               and expedientes_hojas_seguim.num_hoja = expedientes_articulos_embarque.num_hoja
               and expedientes_hojas_seguim.empresa = expedientes_articulos_embarque.empresa
               and expedientes_imp.codigo = expedientes_hojas_seguim.num_expediente
               and expedientes_imp.empresa = expedientes_hojas_seguim.empresa
               and expedientes_articulos_embarque.empresa = '001'
               and articulos.codigo_articulo = expedientes_articulos_embarque.articulo
               and articulos.codigo_empresa = expedientes_articulos_embarque.empresa
               and ( expedientes_hojas_seguim.status not in ( 'C' ) ) )
               and ( expedientes_contenedores.contenedor is null
                or expedientes_contenedores.contenedor != 'CNT' )
               and expedientes_hojas_seguim.num_expediente = :exp_id
               and expedientes_articulos_embarque.articulo = :art_code
               """
        
    res = oracle.consult(sql, {'exp_id':exp_id, 'art_code': art_code})
    return res