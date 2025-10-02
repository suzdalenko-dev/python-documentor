from django.db import models

# logistica_orderlistbelinloads

class OrderListBelinLoads(models.Model):
    load_id          = models.IntegerField(null=True, db_index=True)
    load_week        = models.TextField(null=True)
    load_date        = models.TextField(null=True)
    
    truck_id         = models.IntegerField(null=True, db_index=True)
    truck_name       = models.TextField(null=True)

    order_id         = models.TextField(null=True)

    articles         = models.TextField(null=True)
    clicked          = models.IntegerField(null=True)
    click_info       = models.TextField(null=True)
    palets           = models.FloatField(null=True)

    client_id        = models.TextField(null=True)
    client_name      = models.TextField(null=True)
    orden            = models.IntegerField(null=True)

    input_palets     = models.FloatField(null=True)


# Crear/modificar hojas de carga (menu punto)
# logistica_orderartcilesregionalloads 

class OrderArtcilesRegionalLoads(models.Model):
    load_id          = models.TextField(null=True, db_index=True)
    load_date        = models.TextField(null=True, db_index=True)
    ejercicio        = models.TextField(null=True, db_index=True)
    matricula        = models.TextField(null=True)
    conductor        = models.TextField(null=True)

    article_code     = models.TextField(null=True, db_index=True)
    article_name     = models.TextField(null=True)

    preparado        = models.TextField(null=True)
    pedido           = models.TextField(null=True)
    und_ped          = models.TextField(null=True)
    cajas_ped        = models.TextField(null=True)
    codigo_familia   = models.TextField(null=True)

    clicked          = models.IntegerField(null=True, default=0)
    cajas_real       = models.FloatField(null=True)
    kg_real          = models.FloatField(null=True)

    desglose         = models.TextField(null=True)
    desglose_ticado  = models.TextField(null=True)