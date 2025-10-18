from django.db import models
import uuid

# The user department is the one saved in the document
class Documents(models.Model):
    id                  = models.BigAutoField(primary_key=True)
    title               = models.TextField(null=True)
    descrption          = models.TextField(null=True)
    user_id             = models.BigIntegerField(null=True, db_index=True)
    user_name           = models.TextField(null=True)
    department_id       = models.IntegerField(null=True, db_index=True)
    department_name     = models.TextField(null=True)
    created_at          = models.TextField(null=True)
    updated_at          = models.TextField(null=True)
    expiration_date     = models.TextField(null=True)
    notification_emails = models.TextField(null=True)


class Documents_Lines(models.Model):
    id                  = models.BigAutoField(primary_key=True)
    document_id         = models.BigIntegerField(null=True, db_index=True)
    file_name           = models.TextField(null=True)
    file_path           = models.TextField(null=True)
    file_size_mb        = models.FloatField(null=True)
    department_id       = models.IntegerField(null=True, db_index=True)
    user_id             = models.BigIntegerField(null=True, db_index=True)
    

class Tags(models.Model):
    id              = models.BigAutoField(primary_key=True)
    name            = models.TextField(null=True)
    user_id         = models.IntegerField(null=True, db_index=True)
    user_name       = models.TextField(null=True)
    department_id   = models.IntegerField(null=True, db_index=True)
    department_name = models.TextField(null=True)


class Document_Tags(models.Model):
    id          = models.BigAutoField(primary_key=True)
    document_id = models.IntegerField(null=True, db_index=True)
    tag_id      = models.IntegerField(null=True, db_index=True)
    tag_name    = models.TextField(null=True)


# aqui guardo el usuario en el caso que pueda ver los documentos no solo de su departamiento
class Users_Departments(models.Model):
    id              = models.BigAutoField(primary_key=True)
    user_id         = models.IntegerField(null=True, db_index=True)
    user_name       = models.TextField(null=True)
    department_id   = models.IntegerField(null=True, db_index=True)
    department_name = models.TextField(null=True)
    