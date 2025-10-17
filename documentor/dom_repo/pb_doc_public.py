from math import ceil
from django.db import connection

from mainapp.utils.utilities.funcions_file import encode_id_secure

def all_doc(request):
    # Parámetros
    number_page  = int(request.GET.get('number_page', 1) or 1)
    doc_per_page = 22
    user_id      = int(request.GET.get('user_id', 0) or 0)
    filter_text  = str(request.GET.get('filter_text', '') or '').strip().lower()

    creation_date_from   = str(request.GET.get('creation_date_from', '') or '').strip()
    creation_date_to     = str(request.GET.get('creation_date_to', '') or '').strip()
    expiration_date_from = str(request.GET.get('expiration_date_from', '') or '').strip()
    expiration_date_to   = str(request.GET.get('expiration_date_to', '') or '').strip()

    # 🔹 Etiquetas: ?tag_ids=1,2,3,4
    tag_ids_param = str(request.GET.get('tag_ids', '') or '').strip()
    tag_ids = [int(t) for t in tag_ids_param.split(',') if t.strip().isdigit()]

    offset = (number_page - 1) * doc_per_page

    # Filtros dinámicos
    text_filter_count = ""
    text_filter_docs  = ""
    params_count = [user_id, user_id]
    params_docs  = [user_id, user_id]

    # 🔹 Filtro por texto (title / descrption / notification_emails)
    if filter_text:
        text_filter_count += """ AND (
            LOWER(dd2.title) LIKE %s OR
            LOWER(dd2.descrption) LIKE %s OR
            LOWER(dd2.notification_emails) LIKE %s
        )"""
        text_filter_docs += """ AND (
            LOWER(dd.title) LIKE %s OR
            LOWER(dd.descrption) LIKE %s OR
            LOWER(dd.notification_emails) LIKE %s
        )"""
        like_value = f"%{filter_text}%"
        params_count += [like_value, like_value, like_value]
        params_docs  += [like_value, like_value, like_value]

    # 🔹 Filtro por fechas de creación
    if creation_date_from:
        text_filter_count += " AND dd2.created_at >= %s"
        text_filter_docs  += " AND dd.created_at >= %s"
        params_count.append(creation_date_from)
        params_docs.append(creation_date_from)

    if creation_date_to:
        text_filter_count += " AND dd2.created_at <= %s"
        text_filter_docs  += " AND dd.created_at <= %s"
        params_count.append(creation_date_to)
        params_docs.append(creation_date_to)

    # 🔹 Filtro por fechas de expiración
    if expiration_date_from:
        text_filter_count += " AND dd2.expiration_date >= %s"
        text_filter_docs  += " AND dd.expiration_date >= %s"
        params_count.append(expiration_date_from)
        params_docs.append(expiration_date_from)

    if expiration_date_to:
        text_filter_count += " AND dd2.expiration_date <= %s"
        text_filter_docs  += " AND dd.expiration_date <= %s"
        params_count.append(expiration_date_to)
        params_docs.append(expiration_date_to)

    # 🔹 Filtro por etiquetas (si hay tag_ids)
    if tag_ids:
        placeholders = ", ".join(["%s"] * len(tag_ids))
        tag_count = len(tag_ids)

        text_filter_count += f"""
            AND dd2.id IN (
                SELECT document_id
                FROM documentor_document_tags
                WHERE tag_id IN ({placeholders})
                GROUP BY document_id
                HAVING COUNT(DISTINCT tag_id) = {tag_count}
            )
        """

        text_filter_docs += f"""
            AND dd.id IN (
                SELECT document_id
                FROM documentor_document_tags
                WHERE tag_id IN ({placeholders})
                GROUP BY document_id
                HAVING COUNT(DISTINCT tag_id) = {tag_count}
            )
        """

    params_count += tag_ids
    params_docs  += tag_ids

    sql1 = ""
    sql2 = ""
    with connection.cursor() as cursor:
        # 🧮 1️⃣ Numero total de documentos filtrados
        sql1 = f"""
            SELECT COUNT(*)
            FROM documentor_documents dd2
            WHERE (dd2.department_id IN (
                        SELECT mau.department_id FROM mainapp_users mau WHERE mau.id = %s
                    )
                    OR dd2.department_id IN (
                        SELECT ud.department_id FROM documentor_users_departments ud WHERE ud.user_id = %s
                    ))
            {text_filter_count}
        """
        cursor.execute(sql1, params_count)
        total_count = cursor.fetchone()[0]

        # 📄 2️⃣ Documentos paginados con etiquetas
        sql2 = f"""SELECT
                (SELECT GROUP_CONCAT(dt.tag_name, ', ')
                 FROM documentor_document_tags dt
                 WHERE dt.document_id = dd.id
                ) AS tags,
                dd.id, dd.title, dd.descrption, dd.user_id, dd.user_name,
                dd.department_id, dd.department_name, dd.created_at, dd.updated_at,
                dd.expiration_date, dd.notification_emails
            FROM documentor_documents dd
            WHERE (dd.department_id IN (
                        SELECT mau.department_id FROM mainapp_users mau WHERE mau.id = %s
                    )
                    OR dd.department_id IN (
                        SELECT ud.department_id FROM documentor_users_departments ud WHERE ud.user_id = %s
                    ))
            {text_filter_docs}
            ORDER BY dd.id DESC
            LIMIT %s OFFSET %s
        """
        cursor.execute(sql2, params_docs + [doc_per_page, offset])

        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

    # 🔹 Convertir filas a lista de diccionarios
    docs = [dict(zip(columns, row)) for row in rows]
    # 🔹 Añadir campo 'code' con id codificado
    # for d in docs:
    #     d["code"] = encode_id_secure(d["id"])
    
    total_pages = ceil(total_count / doc_per_page) if total_count else 1

    # 🔹 Resultado final
    return {
        'page': number_page,
        'total_pages': total_pages,
        'total_docs': total_count,
        'has_prev': number_page > 1,
        'has_next': number_page < total_pages,
        'docs': docs,
        'sql1': sql1,
        'sql2': sql2,
    }
