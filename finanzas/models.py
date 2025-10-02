from django.db import models

class InvoicesSales(models.Model):
    codigo_cliente     = models.TextField(null=True)
    cliente            = models.TextField(null=True)
    org_comercial      = models.TextField(null=True)
    agente             = models.TextField(null=True)
    ejercicio          = models.TextField(null=True)
    updated            = models.TextField(null=True)
    forma_cobro        = models.TextField(null=True)

    documento          = models.TextField(null=True, unique=True)
    dag                = models.TextField(null=True)
    importe            = models.FloatField(null=True)
    importe_cobrado    = models.FloatField(null=True)
    
    fecha_factura      = models.TextField(null=True)
    fecha_vencimiento  = models.TextField(null=True)
    fecha_cobro        = models.TextField(null=True)

    status_vencimiento = models.TextField(null=True)
    status_cobro       = models.TextField(null=True)

    dias_real_pago     = models.FloatField(null=True)
    dias_exceso        = models.FloatField(null=True)