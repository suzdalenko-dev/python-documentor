select divisa_origen,
       divisa_destino,
       fecha_valor,
       valor_compra,
       valor_venta
  from (
   select cambio_divisas.*,
          (
             select lvdiv.nombre
               from divisas lvdiv
              where lvdiv.codigo = cambio_divisas.divisa_destino
          ) d_divisa_destino,
          (
             select lvdiv.nombre
               from divisas lvdiv
              where lvdiv.codigo = cambio_divisas.divisa_origen
          ) d_divisa_origen
     from cambio_divisas
) cambio_divisas
 order by fecha_valor desc,
          divisa_origen,
          divisa_destino