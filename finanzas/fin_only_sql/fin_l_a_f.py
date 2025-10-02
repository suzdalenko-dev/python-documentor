def fin_latest_arrivals(request, conn):
    first  = request.GET.get('first')
    second = request.GET.get('second')
    sql = """SELECT  articulos.codigo_familia,
                    articulos.d_codigo_familia,
                    expedientes_articulos_embarque.articulo,
                    (SELECT DESCRIP_COMERCIAL FROM ARTICULOS WHERE CODIGO_ARTICULO = expedientes_articulos_embarque.articulo AND ROWNUM = 1) AS DESCRIP_COMERCIAL,
                    expedientes_hojas_seguim.num_expediente,
                    expedientes_hojas_seguim.num_hoja,
                    expedientes_articulos_embarque.contenedor,
                    expedientes_imp.forma_envio,

                    TO_CHAR(expedientes_imp.FECHA_EXPEDIENTE, 'DD/MM/YYYY') AS FECHA_CONTRATO,
                    SUBSTR(expedientes_hojas_seguim.OBSERVACIONES, 1, 7) AS C_BAN,

                    expedientes_articulos_embarque.cantidad cantidad1,
                    expedientes_imp.LUGAR_EMBARQUE,
                    expedientes_imp.LUGAR_DESEMBARQUE,
            expedientes_articulos_embarque.presentacion,
            expedientes_articulos_embarque.destino_especial,
            expedientes_articulos_embarque.deposito_aduanero,
            expedientes_articulos_embarque.precio,
            expedientes_articulos_embarque.importe,
            DECODE(NVL(EXPEDIENTES_IMP.VALOR_CAMBIO,0) , 0, expedientes_articulos_embarque.precio , expedientes_articulos_embarque.precio * EXPEDIENTES_IMP.VALOR_CAMBIO) precio_por_valor_cambio,
            coalesce(EXPEDIENTES_HOJAS_SEGUIM.VALOR_CAMBIO, EXPEDIENTES_IMP.VALOR_CAMBIO,1) VALOR_CAMBIO,
            SUBSTR(expedientes_hojas_seguim.tipo_cambio, 1, 1) tipo_cambio,
            1 / coalesce(EXPEDIENTES_HOJAS_SEGUIM.VALOR_CAMBIO, EXPEDIENTES_IMP.VALOR_CAMBIO,1) VALOR_CAMBIO2,
            DECODE(coalesce(EXPEDIENTES_HOJAS_SEGUIM.VALOR_CAMBIO, EXPEDIENTES_IMP.VALOR_CAMBIO,1), 
                   0, expedientes_articulos_embarque.precio, 
                   expedientes_articulos_embarque.precio * coalesce(EXPEDIENTES_HOJAS_SEGUIM.VALOR_CAMBIO, EXPEDIENTES_IMP.VALOR_CAMBIO,1)) precio_por_valor_cambio2,
                   (((SELECT SUM(hs.importe_portes) FROM reparto_portes_hs hs WHERE hs.codigo_empresa = expedientes_hojas_seguim.empresa AND hs.numero_expediente = expedientes_hojas_seguim.num_expediente AND hs.hoja_seguimiento = expedientes_hojas_seguim.num_hoja 
                 and hs.codigo_articulo = expedientes_articulos_embarque.articulo) / DECODE(articulos.unidad_valoracion, 1, expedientes_articulos_embarque.cantidad_unidad1, 2, expedientes_articulos_embarque.cantidad_unidad2)) + (expedientes_articulos_embarque.precio *
                    DECODE(expedientes_hojas_seguim.tipo_cambio, 'E', DECODE(expedientes_imp.cambio_asegurado, 'S', expedientes_imp.valor_cambio, 'N', 1), 'S', expedientes_hojas_seguim.valor_cambio, 'N',coalesce(EXPEDIENTES_HOJAS_SEGUIM.VALOR_CAMBIO, EXPEDIENTES_IMP.VALOR_CAMBIO,1)))) precio_con_gastos,
                    expedientes_imp.d_clave_arancel,
                    expedientes_hojas_seguim.d_situacion_logistica,
                    expedientes_hojas_seguim.documentacion_x_contenedor,
                    
                    -- expedientes_hojas_seguim.FECHA_PREV_EMBARQUE,
                    -- expedientes_hojas_seguim.FECHA_EMBARQUE,
                    COALESCE(expedientes_hojas_seguim.FECHA_EMBARQUE, expedientes_hojas_seguim.FECHA_PREV_EMBARQUE) FECHA_EMBARQUE,
                    
                    expedientes_hojas_seguim.FECHA_PREV_LLEGADA,

                    expedientes_hojas_seguim.OBSERVACIONES,

                    expedientes_imp.d_plantilla,
                    NVL(EXPEDIENTES_HOJAS_SEGUIM.PROVEEDOR,EXPEDIENTES_IMP.PROVEEDOR) PROVEEDOR,
                    expedientes_hojas_seguim.d_proveedor_hoja,
                    expedientes_imp.d_descripcion_expediente,
                    expedientes_hojas_seguim.codigo_entrada,
                    expedientes_hojas_seguim.id_seguro_cambio,
                    (select nombre from bancos b, Seguros_cambio c
                        where b.codigo_rapido = c.banco
                        and b.empresa = c.empresa
                        and c.id = expedientes_hojas_seguim.id_seguro_cambio) id_seguro_cambio2,
                    (SELECT MAX(DOCUMENTO) FROM SEGUROS_CAMBIO c WHERE c.ID = expedientes_hojas_seguim.id_seguro_cambio) DOCUMENTO_SEGUROS_CAMBIO,
                    (select SUM(IMPORTE) from  Seguros_cambio c where  c.id = expedientes_hojas_seguim.id_seguro_cambio) importe_seguros_cambio,
                    expedientes_hojas_seguim.carta_credito,
                    (SELECT MAX(FECHA_VENCIMIENTO) FROM CARTAS_CREDITO C WHERE C.NUMERO_CARTA_CREDITO = expedientes_hojas_seguim.CARTA_CREDITO ) FECHA_VENCIMIENTO
                    FROM (SELECT ARTICULOS.*,DECODE(articulos.codigo_familia,NULL,NULL,(SELECT lvfm.descripcion FROM familias lvfm WHERE lvfm.codigo_familia = articulos.codigo_familia AND lvfm.numero_tabla = 1 AND lvfm.codigo_empresa = articulos.codigo_empresa)) D_CODIGO_FAMILIA FROM ARTICULOS) ARTICULOS,(SELECT EXPEDIENTES_IMP.*,DECODE(expedientes_imp.clave_arancel,NULL,NULL,(SELECT lvarimp.descripcion FROM aranceles_imp lvarimp WHERE lvarimp.clave_arancel = expedientes_imp.clave_arancel AND lvarimp.codigo_empresa = expedientes_imp.empresa)) D_CLAVE_ARANCEL,DECODE(expedientes_imp.plantilla,NULL,NULL,(SELECT lvpltimp.nombre FROM plantillas_impor lvpltimp WHERE lvpltimp.codigo = expedientes_imp.plantilla AND lvpltimp.empresa = expedientes_imp.empresa)) D_PLANTILLA,(SELECT lvexpc.descripcion FROM expedientes_cab lvexpc WHERE lvexpc.codigo = expedientes_imp.codigo AND lvexpc.empresa = expedientes_imp.empresa) D_DESCRIPCION_EXPEDIENTE FROM EXPEDIENTES_IMP) EXPEDIENTES_IMP,(SELECT EXPEDIENTES_HOJAS_SEGUIM.*,(SELECT DESCRIPCION FROM EXPEDIENTES_HOJAS_SITUACION WHERE CODIGO=EXPEDIENTES_HOJAS_SEGUIM.SITUACION_LOGISTICA) D_SITUACION_LOGISTICA,NVL((SELECT pr.nombre
             FROM proveedores pr
            WHERE pr.codigo_rapido = expedientes_hojas_seguim.proveedor
            AND pr.codigo_empresa = expedientes_hojas_seguim.empresa),(SELECT pr.nombre
            FROM proveedores pr, expedientes_imp ei
            WHERE ei.codigo = expedientes_hojas_seguim.num_expediente
            AND ei.empresa = expedientes_hojas_seguim.empresa
            AND pr.codigo_rapido = ei.proveedor
            AND pr.codigo_empresa = ei.empresa)) D_PROVEEDOR_HOJA,(SELECT LISTAGG(EC.NUM_CARTA_CREDITO, ',') within group (order by EC.NUM_CARTA_CREDITO)
            FROM EXPEDIENTES_HOJAS_SEGUIM_MOV EC
            WHERE EC.NUM_EXPEDIENTE = EXPEDIENTES_HOJAS_SEGUIM.NUM_EXPEDIENTE
            AND EC.NUM_HOJA = EXPEDIENTES_HOJAS_SEGUIM.NUM_HOJA
            AND  EC.EMPRESA = EXPEDIENTES_HOJAS_SEGUIM.EMPRESA) CARTA_CREDITO FROM EXPEDIENTES_HOJAS_SEGUIM) EXPEDIENTES_HOJAS_SEGUIM,(SELECT EXPEDIENTES_ARTICULOS_EMBARQUE.*,(SELECT (SELECT DECODE(usuarios.tipo_desc_art,'V',articulos.descrip_comercial, 'C',articulos.descrip_compra, 'T',articulos.descrip_tecnica,articulos.descrip_comercial) FROM usuarios WHERE usuarios.usuario=pkpantallas.usuario_validado) FROM articulos WHERE articulos.codigo_articulo = expedientes_articulos_embarque.articulo AND articulos.codigo_empresa  =expedientes_articulos_embarque.empresa) D_ARTICULO,(SELECT DECODE(AR.UNIDAD_PRECIO_COSTE,1,CANTIDAD_UNIDAD1*PRECIO,CANTIDAD_UNIDAD2*PRECIO) FROM ARTICULOS AR WHERE AR.CODIGO_ARTICULO =  EXPEDIENTES_ARTICULOS_EMBARQUE.ARTICULO AND AR.CODIGO_EMPRESA = EXPEDIENTES_ARTICULOS_EMBARQUE.EMPRESA) IMPORTE FROM EXPEDIENTES_ARTICULOS_EMBARQUE) EXPEDIENTES_ARTICULOS_EMBARQUE,EXPEDIENTES_CONTENEDORES WHERE (expedientes_contenedores.num_expediente=expedientes_articulos_embarque.num_expediente
            and expedientes_contenedores.num_hoja=expedientes_articulos_embarque.num_hoja
            and expedientes_contenedores.empresa=expedientes_articulos_embarque.empresa
            AND expedientes_contenedores.linea=expedientes_articulos_embarque.linea_contenedor
            and expedientes_hojas_seguim.num_expediente=expedientes_articulos_embarque.num_expediente
            and expedientes_hojas_seguim.num_hoja=expedientes_articulos_embarque.num_hoja
            and expedientes_hojas_seguim.empresa=expedientes_articulos_embarque.empresa
            and expedientes_imp.codigo=expedientes_hojas_seguim.num_expediente
            and expedientes_imp.empresa=expedientes_hojas_seguim.empresa
            and expedientes_articulos_embarque.empresa='001'
            AND articulos.codigo_articulo=expedientes_articulos_embarque.articulo
            AND articulos.codigo_empresa=expedientes_articulos_embarque.empresa
            AND ('' IS NULL OR
            EXISTS(SELECT 1
            FROM expedientes_contenedores ec
            WHERE ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND contenedor LIKE '')) AND ('' IS NULL OR
            EXISTS(SELECT 1
            FROM expedientes_contenedores ec
            WHERE ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND tipo='')) AND ('' IS NULL OR
            (EXISTS(SELECT 1
            FROM con_impor co,expedientes_hojas_seguim_con ec
            WHERE co.codigo=ec.concepto
            AND co.tipo='PO'
            AND co.codigo_empresa=ec.empresa
            AND ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND proveedor=''))) AND ('' IS NULL OR
            (EXISTS(SELECT 1
            FROM con_impor co,expedientes_hojas_seguim_con ec
            WHERE co.codigo=ec.concepto
            AND co.tipo='FL'
            AND ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND proveedor=''))) AND ('' IS NULL OR
            (EXISTS(SELECT 1
            FROM con_impor co,expedientes_hojas_seguim_con ec
            WHERE co.codigo=ec.concepto
            AND co.tipo='DE'
            AND co.codigo_empresa=ec.empresa
            AND ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND proveedor=''))) AND ('' IS NULL OR
            EXISTS(SELECT 1
            FROM expedientes_hojas_seguim_mov ec
            WHERE ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND num_carta_credito LIKE '')) AND ('' IS NULL OR
            EXISTS(SELECT 1
            FROM expedientes_hojas_seguim_mov ec
            WHERE ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND num_bill_lading LIKE '')) AND ('' IS NULL OR
            EXISTS(SELECT 1
            FROM expedientes_articulos_embarque ec
            WHERE ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND ec.lote LIKE ''))
            AND ('' IS NULL OR
            EXISTS(SELECT 1 FROM expedientes_hojas_seguim_mov ec
            WHERE ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND numero_booking LIKE ''))
            AND ('' IS NULL OR
            EXISTS(SELECT 1
            FROM expedientes_hojas_seguim_mov ec
            WHERE ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND banco LIKE ''))
            AND ('' IS NULL OR expedientes_hojas_seguim.numero_dua LIKE '' OR
            (EXISTS(SELECT 1
            FROM expedientes_contenedores_docs ec
            WHERE ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja =expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND codigo_dua LIKE '') OR expedientes_imp.numero_dua LIKE ''))
            AND ('' IS NULL OR
            EXISTS(SELECT 1
            FROM expedientes_hojas_seguim_mov ec
            WHERE ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND ec.cod_movimiento
            IN (SELECT col_value FROM TABLE(pktmp_select_in.split_cadena_vch2('')))
            )) AND ('' IS NULL OR
            NOT EXISTS(SELECT 1
            FROM expedientes_hojas_seguim_mov ec
            WHERE ec.num_expediente=expedientes_hojas_seguim.num_expediente
            AND ec.num_hoja=expedientes_hojas_seguim.num_hoja
            AND ec.empresa=expedientes_hojas_seguim.empresa
            AND ec.cod_movimiento IN (SELECT col_value FROM TABLE(pktmp_select_in.split_cadena_vch2(''))))) AND ('' IS NULL OR
            EXISTS(SELECT 1
            FROM albaran_compras_c ac
            WHERE ac.numero_expediente=expedientes_hojas_seguim.num_expediente
            AND ac.codigo_EMPRESA=expedientes_hojas_seguim.EMPRESA
            AND (ac.hoja_seguimiento IS NULL OR ac.hoja_seguimiento=expedientes_hojas_seguim.num_hoja)
            AND ac.numero_doc_interno=''))
            AND ('' IS NULL OR
            EXISTS(SELECT 1
            FROM facturas_compras_lin fc,albaran_compras_l al,albaran_compras_c ac
            WHERE ac.numero_expediente=expedientes_hojas_seguim.num_expediente
            AND ac.codigo_empresa=expedientes_hojas_seguim.empresa
            AND (ac.hoja_seguimiento IS NULL OR ac.hoja_seguimiento=expedientes_hojas_seguim.num_hoja)
            AND al.numero_doc_interno=ac.numero_doc_interno
            AND al.codigo_empresa=ac.codigo_empresa
            AND fc.num_albaran_int=al.numero_doc_interno
            AND fc.linea_albaran=al.numero_linea
            AND fc.numero_factura=''
            AND fc.codigo_empresa=al.codigo_empresa))
            AND ('' IS NULL OR NVL(expedientes_hojas_seguim.proveedor,(SELECT ei.proveedor FROM expedientes_imp ei WHERE ei.codigo=expedientes_hojas_seguim.num_expediente AND ei.empresa=expedientes_hojas_seguim.empresa))='')
            AND (('' IS NULL AND '' IS NULL AND '' IS NULL AND '' IS NULL) OR
            EXISTS (SELECT 1
            FROM pedidos_ventas pv
            WHERE pv.empresa=expedientes_hojas_seguim.empresa
            AND pv.numero_expediente=expedientes_hojas_seguim.num_expediente
            AND (pv.hoja_seguimiento IS NULL OR pv.hoja_seguimiento=expedientes_hojas_seguim.num_hoja)
            AND (pv.organizacion_comercial= '' OR '' IS NULL)
            AND (pv.ejercicio= '' OR '' IS NULL)
            AND (pv.numero_pedido= '' OR '' IS NULL)
            AND (pv.numero_serie= '' OR '' IS NULL)
            AND NVL(pv.anulado, 'N') = 'N'))
            AND (('' IS NULL AND '' IS NULL AND '' IS NULL AND '' IS NULL) OR
            EXISTS (SELECT 1
            FROM albaran_ventas pv
            WHERE pv.empresa=expedientes_hojas_seguim.empresa
            AND pv.numero_expediente=expedientes_hojas_seguim.num_expediente
            AND (pv.hoja_seguimiento IS NULL OR pv.hoja_seguimiento=expedientes_hojas_seguim.num_hoja)
            AND (pv.organizacion_comercial= '' OR '' IS NULL)
            AND (pv.ejercicio= '' OR '' IS NULL)
            AND (pv.numero_albaran= '' OR '' IS NULL)
            AND (pv.numero_serie= '' OR '' IS NULL)
            AND NVL(pv.anulado, 'N') = 'N'))
            AND (('' IS NULL AND '' IS NULL AND '' IS NULL) OR
            EXISTS (SELECT 1
            FROM albaran_ventas pv
            WHERE pv.empresa=expedientes_hojas_seguim.empresa
            AND pv.numero_expediente=expedientes_hojas_seguim.num_expediente
            AND (pv.hoja_seguimiento IS NULL OR pv.hoja_seguimiento=expedientes_hojas_seguim.num_hoja)
            AND (pv.ejercicio_factura='' OR '' IS NULL)
            AND (pv.numero_factura='' OR '' IS NULL)
            AND (pv.numero_serie_fra='' OR '' IS NULL)
            AND NVL(pv.anulado, 'N') = 'N'))
            AND ('' is null or exists (select 1 from expedientes_imp_agentes ea where ea.numero_expediente = expedientes_imp.codigo and ea.agente = '' and ea.empresa = expedientes_imp.empresa)) AND (EXPEDIENTES_HOJAS_SEGUIM.STATUS NOT IN ('C'))) AND (articulos.codigo_empresa = '001') AND (expedientes_imp.empresa = '001') AND (expedientes_hojas_seguim.empresa = '001') AND (expedientes_articulos_embarque.EMPRESA='001') AND (expedientes_contenedores.empresa = '001') 
            
            
            
            -- AND expedientes_hojas_seguim.num_expediente IN (285)
            AND expedientes_hojas_seguim.codigo_entrada IS NULL
            AND expedientes_hojas_seguim.fecha_prev_llegada >= TO_DATE(:first, 'YYYY-MM-DD') AND expedientes_hojas_seguim.fecha_prev_llegada <= TO_DATE(:second, 'YYYY-MM-DD')
            
            ORDER BY expedientes_hojas_seguim.fecha_prev_llegada ASC,
                  expedientes_articulos_embarque.contenedor ASC,
                  FECHA_EMBARQUE ASC
            """
    

    res = conn.consult(sql, {'first':first, 'second':second})

    return res    