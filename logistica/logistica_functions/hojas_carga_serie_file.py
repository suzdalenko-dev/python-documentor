from datetime import date
import json
import threading
from froxa.utils.connectors.libra_connector import OracleConnector
from django.db import connection
from logistica.logistica_repository.desglose_cliente import lineas_cliente
from logistica.models import OrderArtcilesRegionalLoads



def get_refresh_head_02(request):
    # postgreSQL request
    cursor = connection.cursor()
    cursor.execute("""SELECT 
                        l.load_id       AS load_id,
                        l.load_date     AS load_date,
                        l.matricula     AS matricula,
                        l.conductor     AS conductor,
                        l.ejercicio     AS ejercicio,
                        (BOOL_AND(COALESCE(l.clicked, 0) = 1))::int AS clicked,
                        (SELECT SUM(ll.cajas_real) FROM logistica_orderartcilesregionalloads ll WHERE ll.load_id = l.load_id AND ll.ejercicio = l.ejercicio) AS cajas_real,
                        (SELECT SUM(ll.kg_real) FROM logistica_orderartcilesregionalloads ll WHERE ll.load_id = l.load_id AND ll.ejercicio = l.ejercicio) AS kg_real
                    FROM logistica_orderartcilesregionalloads l
                    WHERE l.load_date IN (
                        SELECT DISTINCT l2.load_date FROM logistica_orderartcilesregionalloads l2 ORDER BY l2.load_date DESC LIMIT 7
                    )
                    GROUP BY l.load_id, l.load_date, l.matricula, l.conductor, l.ejercicio
                    ORDER BY l.load_date DESC, l.load_id DESC""")

    rows          = cursor.fetchall()
    columns       = [col[0] for col in cursor.description]
    beatriz_loads = [dict(zip(columns, row)) for row in rows]

    out        = []
    array_date = []
    for load in beatriz_loads:
      if load['load_date'] not in array_date:
          array_date += [load['load_date']]

    for d in array_date:
      loads = [load for load in beatriz_loads if load['load_date'] == d]
      out += [{'date': d, 'loads': loads}]

    threading.Thread(target=refresh_gema_loading_sheet02,  daemon=True).start()
    return {'res': out}



def get_refresh_custom_load_02(request,  year, carga):
    lines = OrderArtcilesRegionalLoads.objects.filter(ejercicio=year, load_id=carga).values('load_id', 'load_date', 'ejercicio', 'matricula', 'conductor', 'article_code', 'article_name', 'preparado', 'pedido', 'und_ped', 'cajas_ped', 'codigo_familia', 'clicked', 'cajas_real', 'kg_real', 'desglose', 'desglose_ticado').order_by('article_name')
    lines = list(lines)

    threading.Thread(target=refresh_gema_loading_sheet02,  daemon=True).start()
    return {'lines': lines, 'year': year, 'carga': carga}



def refresh_gema_loading_sheet02():
    last_year = date.today().year - 1
    
    oracle = OracleConnector()
    oracle.connect()
    sql = """SELECT TO_CHAR(mhc.FECHA_CARGA, 'YYYY-MM-DD') AS FECHA_CARGA, mhc.MATRICULA, mhc.CONDUCTOR,
                 mhc.EJERCICIO,
                 mhc.NUMERO_PROPUESTA
          FROM MA_HOJA_CARGA mhc
          WHERE mhc.SERIE_HOJA_CARGA = '02'
            AND mhc.STATUS_PROPUESTA = 'A'
            AND mhc.CODIGO_EMPRESA = '001'
            AND (mhc.USUARIO_VALIDACION IS NOT NULL OR mhc.FECHA_VALIDACION IS NOT NULL)
            AND mhc.ALMACEN IN ('00','01','02')
            AND mhc.EJERCICIO >= :last_year
            AND TRUNC(mhc.FECHA_CARGA) IN (
                SELECT fecha
                FROM (
                    SELECT DISTINCT TRUNC(FECHA_CARGA) AS fecha
                    FROM MA_HOJA_CARGA
                    WHERE CODIGO_EMPRESA = '001'
                    ORDER BY fecha DESC
                    FETCH FIRST 7 ROWS ONLY
                )
            )
          ORDER BY mhc.FECHA_CARGA DESC, mhc.NUMERO_PROPUESTA DESC
          """

    head_data = oracle.consult(sql, {'last_year': last_year})
    
    for head in head_data:
        sql = """SELECT ma_hoja_carga.numero_propuesta,
                  pedidos_ventas_lin.articulo,
                  articulos.codigo_familia,
                  pedidos_ventas_lin.descripcion_articulo,
                  NVL(sum(PEDIDOS_VENTAS_LIN.UNI_RESALM) , 0) PREPARADO,
                  NVL(sum(PEDIDOS_VENTAS_LIN.UNI_PEDALM) , 0) PEDIDO,
                  NVL(sum(PEDIDOS_VENTAS_LIN.UNI_PEDSOB) , 0) UND_PED,
                  NVL(sum(PEDIDOS_VENTAS_LIN.UNI_PEDALM2), 0) CAJAS_PED, 
                  (SELECT MIN(art.TIPO_CADENA_LOGISTICA) FROM articulos art WHERE art.CODIGO_ARTICULO = pedidos_ventas_lin.articulo) TIPO_CADENA_LOGISTICA
            FROM MA_HOJA_CARGA, PEDIDOS_VENTAS, PEDIDOS_VENTAS_LIN, ARTICULOS 
            WHERE PEDIDOS_VENTAS.NUMERO_PEDIDO=PEDIDOS_VENTAS_LIN.NUMERO_PEDIDO
              and PEDIDOS_VENTAS.NUMERO_SERIE=PEDIDOS_VENTAS_LIN.NUMERO_SERIE
              and PEDIDOS_VENTAS.EJERCICIO=PEDIDOS_VENTAS_LIN.EJERCICIO 
              and PEDIDOS_VENTAS.ORGANIZACION_COMERCIAL=PEDIDOS_VENTAS_LIN.ORGANIZACION_COMERCIAL 
              and PEDIDOS_VENTAS.EMPRESA=PEDIDOS_VENTAS_LIN.EMPRESA 
              and MA_HOJA_CARGA.CODIGO_EMPRESA=PEDIDOS_VENTAS_LIN.EMPRESA 
              and MA_HOJA_CARGA.NUMERO_PROPUESTA=PEDIDOS_VENTAS_LIN.NUMERO_PROPUESTA 
              and MA_HOJA_CARGA.SERIE_HOJA_CARGA=PEDIDOS_VENTAS_LIN.SERIE_HOJA_CARGA 
              and ARTICULOS.CODIGO_ARTICULO=PEDIDOS_VENTAS_LIN.ARTICULO 
              and ARTICULOS.CODIGO_EMPRESA=PEDIDOS_VENTAS_LIN.EMPRESA 
              AND ma_hoja_carga.codigo_empresa = '001'
              AND pedidos_ventas_lin.empresa = '001'
              AND articulos.codigo_empresa = '001'
              AND ma_hoja_carga.serie_hoja_carga = '02' 
              AND ma_hoja_carga.ejercicio = :year
              AND ma_hoja_carga.numero_propuesta = :carga  
              GROUP BY ma_hoja_carga.numero_propuesta, pedidos_ventas_lin.articulo, articulos.codigo_familia, pedidos_ventas_lin.descripcion_articulo
              ORDER BY pedidos_ventas_lin.descripcion_articulo ASC"""
        lines = oracle.consult(sql, {'year': head['EJERCICIO'], 'carga': head['NUMERO_PROPUESTA']}) or []
        head['lines'] = lines
 

    year_load_articles_used = []

    for head1 in head_data:
        if head1.get('lines'):
            for line in head1['lines']:
                
                line['clientes_desglose'] = []            # ejemplo 3082
                if line['TIPO_CADENA_LOGISTICA'] == 'PV':
                  datos_desgloshe = lineas_cliente(oracle, head1['EJERCICIO'], head1['NUMERO_PROPUESTA'], line['ARTICULO'])
                  if len(datos_desgloshe) > 1:
                    line['clientes_desglose'] = datos_desgloshe
                
                
                obj, created = OrderArtcilesRegionalLoads.objects.get_or_create(ejercicio=head1['EJERCICIO'], load_id=head1['NUMERO_PROPUESTA'], article_code=line['ARTICULO'])
                obj.load_date = head1['FECHA_CARGA']
                obj.matricula = head1['MATRICULA']
                obj.conductor = head1['CONDUCTOR']

                obj.article_name   = line['DESCRIPCION_ARTICULO']
                obj.cajas_ped      = line['CAJAS_PED']
                obj.codigo_familia = line['CODIGO_FAMILIA']
                obj.pedido         = line['PEDIDO']
                obj.preparado      = line['PREPARADO']
                obj.und_ped        = line['UND_PED']

                obj.desglose       = json.dumps(line['clientes_desglose'])
                if not obj.desglose_ticado:
                  obj.desglose_ticado = json.dumps([])

                obj.save()
                year_load_articles_used += [str(head1['EJERCICIO'])+ str(head1['NUMERO_PROPUESTA'])+str(line['ARTICULO'])]


    # delete old recordsfor head1 in head_data:
    
    for head3 in head_data:
      all_lines = OrderArtcilesRegionalLoads.objects.filter(ejercicio=head3['EJERCICIO'], load_id=head3['NUMERO_PROPUESTA'])
      for db_line in all_lines:
        key = str(db_line.ejercicio)+str(db_line.load_id)+str(db_line.article_code)
        if key not in year_load_articles_used:
          OrderArtcilesRegionalLoads.objects.filter(ejercicio=head3['EJERCICIO'], load_id=head3['NUMERO_PROPUESTA'], article_code=db_line.article_code).delete()

    
    oracle.close()
    return head_data





def regional_clicked(request):
  ejercicio    = request.GET.get('ejercicio')
  load_id      = request.GET.get('load_id')
  article_code = request.GET.get('article_code')

  line = OrderArtcilesRegionalLoads.objects.get(ejercicio=ejercicio, load_id=load_id, article_code=article_code)
  line.clicked = 0 if line.clicked == 1 else 1
  line.save()

  return {'article_code': line.article_code, 'load_id': line.load_id, 'ejercicio': line.ejercicio, 'clicked': line.clicked}


def regional_update(request):
  ejercicio    = request.POST.get('ejercicio')
  load_id      = request.POST.get('load_id')
  article_code = request.POST.get('article_code')
  cajas_real   = float(request.POST.get('cajas')) or 0
  kg_real      = float(request.POST.get('kg')) or 0
  action       = request.POST.get('action')
  cliente      = str(request.POST.get('cliente'))

  line         = OrderArtcilesRegionalLoads.objects.get(ejercicio=ejercicio, load_id=load_id, article_code=article_code)

  if action == 'update_desglose': 
    ticado_desg = json.loads(line.desglose_ticado) or []
    if len(ticado_desg) > 0:
      found = False
      for d in ticado_desg:
        if str(d['cliente']) == cliente:
          d['cajas'] = cajas_real
          d['kg']    = kg_real
          found = True
          break
      if found == True:
        line.desglose_ticado = json.dumps(ticado_desg)
      else:
        ticado_desg += [{'cliente': cliente, 'cajas': cajas_real, 'kg': kg_real}]
        line.desglose_ticado = json.dumps(ticado_desg)
    else:
      x = {'cliente': cliente, 'cajas': cajas_real, 'kg': kg_real}
      line.desglose_ticado = json.dumps([x])

    cajas_total = 0
    kg_total = 0
    ticado_desg = json.loads(line.desglose_ticado)
    for t in ticado_desg:
       cajas_total += t['cajas']
       kg_total    += t['kg']
    
    line.cajas_real = cajas_total
    line.kg_real    = kg_total


  if action == 'update_linea':    
    line.cajas_real = cajas_real
    line.kg_real    = kg_real
  line.save()
  return {'ejercicio': ejercicio}