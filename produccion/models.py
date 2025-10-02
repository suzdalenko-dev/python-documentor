from django.db import models

class ArticleCostsHead(models.Model):
    article_code = models.IntegerField(unique=True)
    article_name = models.TextField(null=True)
    created_at   = models.CharField(max_length=22, null=True)
    updated_at   = models.CharField(max_length=22, null=True)
    cost_date    = models.TextField(null=True)


class ArticleCostsLines(models.Model):
    parent_article = models.IntegerField(null=True)
    article_code   = models.IntegerField(null=True)
    article_name   = models.TextField(null=True)
    percentage     = models.FloatField(null=True)
    alternative    = models.TextField(null=True)
   

class ExcelLinesEditable(models.Model):
    article_code = models.IntegerField(unique=True)
    article_name = models.TextField(null=True)

    rendimiento          = models.FloatField(null=True)
    precio_materia_prima = models.FloatField(null=True)
    
    precio_aceite        = models.FloatField(null=True)
    precio_servicios     = models.FloatField(null=True)
    aditivos             = models.FloatField(null=True)
    mod                  = models.FloatField(null=True)
    embalajes            = models.FloatField(null=True)
    amort_maq            = models.FloatField(null=True)
    moi                  = models.FloatField(null=True)

    inicio_coste_act     = models.FloatField(null=True)
    inicio_coste_mas1    = models.FloatField(null=True)
    inicio_coste_mas2    = models.FloatField(null=True)
    inicio_coste_mas3    = models.FloatField(null=True)

    final_coste_act      = models.FloatField(null=True)
    final_coste_mas1     = models.FloatField(null=True)
    final_coste_mas2     = models.FloatField(null=True)
    final_coste_mas3     = models.FloatField(null=True)

    precio_padre_act           = models.FloatField(null=True)
    precio_padre_mas_gastos    = models.FloatField(null=True)
    precio_estandar            = models.FloatField(null=True)
    precio_estandar_con_gastos = models.FloatField(null=True)


class EquivalentsHead(models.Model):
    article_name = models.TextField(unique=True)
    alternative  = models.TextField(null=True)

    kg_act = models.FloatField(null=True)
    price_act = models.FloatField(null=True)

    kg0    = models.FloatField(null=True)
    price0 = models.FloatField(null=True)
    kg1    = models.FloatField(null=True)
    price1 = models.FloatField(null=True)
    kg2    = models.FloatField(null=True)
    price2 = models.FloatField(null=True)
    kg3    = models.FloatField(null=True)
    price3 = models.FloatField(null=True)
    precio_estandar_equival = models.FloatField(null=True)

    kg4    = models.FloatField(null=True)
    price4 = models.FloatField(null=True)
    kg5    = models.FloatField(null=True)
    price5 = models.FloatField(null=True)
    kg6    = models.FloatField(null=True)
    price6 = models.FloatField(null=True)



class DetalleEntradasEquivCC(models.Model):
    name         = models.TextField(null=True)
    entrada      = models.TextField(null=True)
    
    stock_actual = models.FloatField(null=True)
    pcm_actual   = models.FloatField(null=True)
    consumo_prod = models.FloatField(null=True)
    consumo_vent = models.FloatField(null=True)
    
    entrada_kg   = models.FloatField(null=True)
    entrada_eur  = models.FloatField(null=True)

    calc_kg      = models.FloatField(null=True)
    calc_eur     = models.FloatField(null=True)



class EmbarkedIndividualRatingDetail(models.Model):
    name         = models.TextField(null=True)
    code         = models.TextField(null=True)
    mercado      = models.TextField(null=True)
    familia      = models.TextField(null=True)
    subfamilia   = models.TextField(null=True)

    entrada      = models.TextField(null=True)
    
    stock_actual = models.FloatField(null=True)
    pcm_actual   = models.FloatField(null=True)
    consumo_prod = models.FloatField(null=True)
    consumo_vent = models.FloatField(null=True)
    
    entrada_kg   = models.FloatField(null=True)
    entrada_eur  = models.FloatField(null=True)

    calc_kg      = models.FloatField(null=True)
    calc_eur     = models.FloatField(null=True)


class EmbarkedIndividualRatingHorizontal(models.Model):
    name         = models.TextField(null=True)
    code         = models.TextField(null=True)
    mercado      = models.TextField(null=True)
    familia      = models.TextField(null=True)
    subfamilia   = models.TextField(null=True)
    
    fecha        = models.TextField(null=True)
    stock        = models.FloatField(null=True)
    precio       = models.FloatField(null=True)


class ProjectionCostsVPBI(models.Model):
    article_name = models.TextField(null=True)
    fecha        = models.TextField(null=True)
    price        = models.FloatField(null=True)
    y            = models.FloatField(null=True)
    title        = models.TextField(null=True)
 

class EquivalentItemsVPBI(models.Model):
    article_name = models.TextField(null=True)
    fecha        = models.TextField(null=True)
    kg_act       = models.FloatField(null=True)
    price_act    = models.FloatField(null=True)