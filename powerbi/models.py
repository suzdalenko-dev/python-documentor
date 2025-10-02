from django.db import models

class Powerbireports(models.Model):
    report_name = models.TextField(null=True)
    report_link = models.TextField(null=True)
    user_names  = models.TextField(null=True)