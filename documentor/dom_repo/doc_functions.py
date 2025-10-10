from datetime import timezone
import os

from documentor.models import Document_Tags, Documents, Tag
from mainapp.utils.utilities.funcions_file import get_current_date, get_current_month, get_current_year, get_short_date, sanitize_filename


def create_new_doc(request, payload):
    if request.method != 'POST':
        return {'error': 'yes', 'message': 'Método no permitido'}

    try:
        # Si el archivo viene por formData:
        title           = request.POST.get('title')
        description     = request.POST.get('description')
        expiration_date = request.POST.get('expiration_date')
        email_aviso     = request.POST.get('email_aviso')
        tags            = request.POST.get('tags')  

        uploaded_file = request.FILES.get('file')

        if not all([title, expiration_date, email_aviso, uploaded_file]):
            return {'error': 'yes', 'message': 'Faltan datos obligatorios'}

        # Guardar archivo en sistema de archivos
        user_name_value = payload.get('username', 'unknown')
        folder = 'media/docs/'+user_name_value+'/'+get_current_year()+'/'+get_current_month()
        os.makedirs(folder, exist_ok=True)
        cleaned_name = sanitize_filename(uploaded_file.name)
        file_path = folder+'/'+cleaned_name

        with open(file_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)

        # Crear registro en BD
        doc = Documents()
        doc.title               = title
        doc.descrption          = description
        doc.expiration_date     = expiration_date
        doc.notification_emails = email_aviso
        doc.file_name           = cleaned_name
        doc.file_path           = file_path
        doc.created_at          = get_short_date()
        doc.updated_at          = get_current_date()
        doc.user_id             = payload.get('user_id')
        doc.user_name           = payload.get('username')
        doc.department_id       = payload.get('department_id')
        doc.department_name     = payload.get('department_name')

        if os.path.exists(file_path):  
            file_size_mb = round(uploaded_file.size / (1024 * 1024), 1)
            doc.file_size_mb = file_size_mb
            doc.save()

            tag_ids = [int(t.strip()) for t in tags.split(',') if t.strip().isdigit()]
            for tag_id in tag_ids:
                tag = Tag.objects.filter(id=tag_id).first()
                if tag:
                    doc_tag             = Document_Tags()
                    doc_tag.document_id = doc.id
                    doc_tag.tag_id      = tag.id
                    doc_tag.tag_name    = tag.name
                    doc_tag.save()

        else:
            return {'error': 'yes', 'message': 'Error al guardar archivo físico.'}

        return {'error': 'no', 'message': 'Documento guardado correctamente', 'id': doc.id}

    except Exception as e:
        return {'error': 'yes', 'message': str(e)}