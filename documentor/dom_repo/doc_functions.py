from datetime import timezone
import os
from documentor.models import Document_Tags, Documents, Documents_Lines, Tags, Users_Departments
from mainapp.models import Users
from mainapp.utils.utilities.funcions_file import encode_id_secure, get_current_date, get_current_month, get_current_year, get_short_date, json_encode_one, sanitize_filename


def create_new_doc(request, payload):
    if request.method != 'POST':
        return {'error': 'yes', 'message': 'Método no permitido'}

    try:
        # Si el archivo viene por formData:
        title           = request.POST.get('title')
        description     = request.POST.get('description')
        expiration_date = request.POST.get('expiration_date')
        email_aviso     = request.POST.get('email_aviso')
        tags            = request.POST.get('tags', '')  
        files           = request.FILES.getlist('files')  # 🔹 varios archivos

        if not all([title, expiration_date, email_aviso]) or not files:
            return {'error': 'yes', 'message': 'Faltan datos obligatorios o archivos'}

        # Crear registro en BD
        doc = Documents()
        doc.title               = title
        doc.descrption          = description
        doc.expiration_date     = expiration_date
        doc.notification_emails = email_aviso
        doc.created_at          = get_short_date()
        doc.updated_at          = ''
        doc.user_id             = payload.get('user_id')
        doc.user_name           = payload.get('username')
        doc.department_id       = payload.get('department_id')
        doc.department_name     = payload.get('department_name')
        doc.save()

        # Guardar archivo en sistema de archivos
        user_name_value = payload.get('username', 'unknown')
        base_folder = 'media/docs/'+user_name_value+'/'+get_current_year()+'/'+get_current_month()
        os.makedirs(base_folder, exist_ok=True)

        for file in files:
            cleaned_name = sanitize_filename(file.name)
            file_path = base_folder+'/'+cleaned_name

            with open(file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)

            dc = Documents_Lines()
            dc.document_id = doc.id
            dc.file_name=cleaned_name
            dc.file_path=file_path

            if os.path.exists(file_path):  
                size_mb = round(file.size / (1024 * 1024), 1)
                dc.file_size_mb=size_mb
                dc.save()

        

        tag_ids = [int(t.strip()) for t in tags.split(',') if t.strip().isdigit()]
        for tag_id in tag_ids:
            tag = Tags.objects.filter(id=tag_id).first()
            if tag:
                doc_tag             = Document_Tags()
                doc_tag.document_id = doc.id
                doc_tag.tag_id      = tag.id
                doc_tag.tag_name    = tag.name
                doc_tag.save()


        return {'error': 'no', 'message': 'Documento guardado correctamente', 'id': doc.id}

    except Exception as e:
        return {'error': 'yes', 'message': str(e)}
    



def doc_by_id(request):
    # verify that the document belongs to the user's departamentes
    user_id = request.GET.get('user_id')
    doc_id  = request.GET.get('doc_id')
    
    USER_DEP_IN_USE = []
    user       = Users.objects.get(id=user_id)
    USER_DEP_IN_USE += [user.department_id]
    user_deps  = Users_Departments.objects.filter(user_id=user_id).values('department_id') or []
    user_deps  = list(user_deps)
    for ud in user_deps:
        USER_DEP_IN_USE += [ud['department_id']]

    print(USER_DEP_IN_USE)

    doc = Documents.objects.get(id=doc_id)
    doc = json_encode_one(doc)

    if doc['department_id'] in USER_DEP_IN_USE:
        pass
    else:
        return {'error': 'yes', 'message': f'El documento {doc_id} no esta a tu alcance'}

    doc_lines = Documents_Lines.objects.filter(document_id=doc_id).values('id', 'document_id', 'file_name', 'file_path', 'file_size_mb') or []
    doc_lines = list(doc_lines)
    for d in doc_lines:
        d['code'] = encode_id_secure(d['id'])

    tags      = Document_Tags.objects.filter(document_id=doc_id).values('id', 'document_id', 'tag_id', 'tag_name') or []

    return {'doc': doc, 'doc_lines': doc_lines, 'doc_tags': list(tags), 'error': 'no'}

