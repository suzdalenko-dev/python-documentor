from datetime import datetime, date, timedelta, timezone
from pathlib import Path
from dateutil.relativedelta import relativedelta
import json
import os
from django.forms import model_to_dict
import calendar
from urllib.parse import urljoin
from django.conf import settings
from openpyxl import Workbook

from froxa.models import Notify




def get_current_date():
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d %H:%M:%S")
    return formatted


def get_short_date():
    now = datetime.now()
    formatted = now.strftime("%Y-%m-%d")
    return formatted


def json_encode_one(oneObject):
    data = model_to_dict(oneObject)
    return data


def json_encode_all(listObject):
    data = [model_to_dict(article) for article in listObject]
    return data


def tCSV(x):
    return str(x).replace('.', ',')


def end_of_month_dates():
    todayD = date.today()
    dates  = [todayD.strftime("%Y-%m-%d")]
    year  = todayD.year
    month = todayD.month
    for i in range(22):
        month_i = month + i
        year_i = year + (month_i - 1) // 12
        month_i = ((month_i - 1) % 12) + 1
        LAST_DAY = calendar.monthrange(year_i, month_i)[1]
        fecha = date(year_i, month_i, LAST_DAY)
        dates.append(fecha.strftime("%Y-%m-%d"))
    return dates


def get_keys(file_key):
    try:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../froxa-keys/"+file_key))
        with open(base_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            return config_data[0]
    except Exception as e:
        print(f"❌ No se pudo cargar la configuración Oracle: {e}")
        return None
    

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]  # Si viene con proxy
    else:
        ip = request.META.get('REMOTE_ADDR')
    return str(ip)




def invoices_list_of_current_month():
    today = date.today()
    start_date = today.replace(day=1) - relativedelta(months=22)

    month_ranges = []
    year = start_date.year
    month = start_date.month

    while date(year, month, 1) <= today:
        first_day = date(year, month, 1)

        # calculate last day of the month
        if month == 12:
            last_day = date(year, month, 31)
        else:
            next_month = date(year, month + 1, 1)
            last_day = next_month - timedelta(days=1)

        month_ranges.append((first_day.strftime('%Y-%m-%d'), last_day.strftime('%Y-%m-%d')))

        # move to next month
        if month == 12:
            month = 1
            year += 1
        else:
            month += 1

    return month_ranges





def crear_excel_sin_pandas(datos, folder_name, file_name):
    """
    Crea un Excel en MEDIA_ROOT/reports/0/ y devuelve ruta + URL.
    :param datos: lista de diccionarios o lista de listas
    :param nombre_archivo: nombre del archivo final (opcional)
    :return: (ruta absoluta, url pública)
    """

    # 📂 Carpeta destino
    carpeta = os.path.join(settings.MEDIA_ROOT, "reports", folder_name)
    os.makedirs(carpeta, exist_ok=True)

    # nombre de archivo por defecto con timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    file_name = f"{file_name}_{timestamp}.xlsx"
    ruta = os.path.join(carpeta, file_name)

    # 📊 Crear Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Datos"

    if not datos:
        ws.append(["Sin datos"])
    elif isinstance(datos, list) and isinstance(datos[0], dict):
        # cabecera
        ws.append(list(datos[0].keys()))
        # filas
        for fila in datos:
            ws.append([fila.get(k, "") for k in datos[0].keys()])
    else:
        # lista de listas
        for fila in datos:
            ws.append(list(fila))

    # 💾 Guardar archivo
    wb.save(ruta)

    # Construir URL pública a partir de MEDIA_URL
    rel_path = os.path.relpath(ruta, settings.MEDIA_ROOT).replace(os.sep, "/")
    file_url = urljoin(settings.MEDIA_URL, rel_path)

    return ruta, file_url



def delete_excel_reports(folder_name: str, pattern: str = "*"):
    """
    Borra archivos en MEDIA_ROOT/reports/<folder_name>/ que cumplan el patrón.
    Ej.: pattern="*.xlsx" para solo excel.
    """
    base = Path(settings.MEDIA_ROOT) / "reports" / folder_name
    base.mkdir(parents=True, exist_ok=True)  # por si no existe

 
    today_day = datetime.now().day
    if today_day != 9:
        return {'deleted': 'is not 11 day'}

    # Seguridad: no salirte de MEDIA_ROOT
    base_resolved = base.resolve()
    if settings.MEDIA_ROOT not in str(base_resolved):
        raise RuntimeError("Ruta fuera de MEDIA_ROOT")

    count = 0
    for p in base.glob(pattern):
        if p.is_file():
            try:
                p.unlink()
                count += 1
            except Exception as e:
                return {'deleted': f"⚠️ No se pudo borrar {p}: {e}"}
    return {'deleted': count}




def notify_logger(data): # {'email': email_name, 'sent': 0, 'message': subject, 'file': str(file_path)}
    for d in data:
        n = Notify()
        n.email    = d['email']
        n.sent     = str(d['sent'])
        n.message  = str(d['message'])
        n.file     = str(d['file'])
        n.time_log = get_current_date()
        n.save()
