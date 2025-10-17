from documentor.models import Document_Tags, Tags, Users_Departments
from mainapp.models import Users


def create_tag(request, payload):
    tag_name = request.POST.get("name", "").strip().lower()

    if tag_name == "":
        return {"message": "El nombre de la etiqueta no puede estar vacío", "error": "yes"}

    tag_exist = Tags.objects.filter(name=tag_name).exists()
    if tag_exist:
        return {"message": "Eriqueta ya existe", "error": "yes"}
    
    if payload.get("user_id") > 0 and payload.get("department_id") > 0:
        pass
    else:
        return {"message": "Usuario o departamento inválido", "error": "yes"}
    
    new_tag                 = Tags(name=tag_name)
    new_tag.user_id         = payload.get("user_id")
    new_tag.user_name       = payload.get("username")
    new_tag.department_id   = payload.get("department_id")
    new_tag.department_name = payload.get("department_name")
    new_tag.save()

    return {"message": "Creacion de etiqueta exitosa", "error": "no", "id": new_tag.id, "name": new_tag.name}




def get_user_tags(request, payload):
    user_id = payload.get("user_id")
    tags    = Tags.objects.filter(user_id=user_id).values("id", "name").order_by("name")
    return {'tags': list(tags)}




def delete_tag(request, payload):
    tag_id = request.GET.get("tag_id", "").strip()
    if tag_id == "":
        return {"message": "El ID de la etiqueta no puede estar vacío", "error": "yes"}

    tag_in_use = Document_Tags.objects.filter(tag_id=tag_id).exists()
    if tag_in_use:
        return {"message": "No se puede eliminar la etiqueta porque está en uso por uno o más documentos", "error": "yes"}

    tag = Tags.objects.filter(id=tag_id, user_id=payload.get("user_id")).first()
    if not tag:
        return {"message": "Etiqueta no encontrada", "error": "yes"}

    tag.delete()
    return {"message": "Etiqueta eliminada exitosamente", "error": "no"}









def get_department_tags(request, payload):
    department_id = payload.get("department_id")
    tags          = Tags.objects.filter(department_id=department_id).values("id", "name").order_by("name") or []
    return list(tags)



def get_tags_dep(request):
    return 'ok'