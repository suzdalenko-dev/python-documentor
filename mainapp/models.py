from django.db import models

class Users(models.Model):
    name        = models.TextField(null=True)
    password    = models.TextField(null=True)
    role        = models.TextField(null=True)
    permissions = models.TextField(null=True)

    first_visit = models.TextField(null=True)
    last_visit  = models.TextField(null=True)
    num_visit   = models.BigIntegerField(null=True)
    ip          = models.TextField(null=True)

    action_pass = models.TextField(null=True)



class Notify(models.Model):
    email      = models.TextField(null=True)
    sent       = models.TextField(null=True)
    message    = models.TextField(null=True)
    file       = models.TextField(null=True)
    time_log   = models.TextField(null=True)

    year       = models.TextField(null=True)
  