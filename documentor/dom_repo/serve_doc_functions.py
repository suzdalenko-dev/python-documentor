import mimetypes
import os
from django.http import FileResponse, Http404
from documentor.models import Documents_Lines
from mainapp.utils.utilities.funcions_file import decode_id_secure


def serve_document(request):
    code = request.GET.get('code')

    try:
        id = decode_id_secure(code)
        doc = Documents_Lines.objects.get(id=id)
    except Exception as e:
        raise Http404("Documento no encontrado "+ str(e))

    file_path = doc.file_path

    # Verificar si el archivo existe en disco
    if not os.path.exists(file_path):
        raise Http404(f"Archivo no encontrado: {file_path}")

    # Detectar el tipo MIME automáticamente 
    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or 'application/octet-stream'

    # Usar FileResponse (eficiente con archivos grandes)
    response = FileResponse(open(file_path, 'rb'), content_type=mime_type)
    response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'

    # response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
    # response['X-Frame-Options'] = 'ALLOWALL'  # Permite que se cargue dentro del iframe

    return response