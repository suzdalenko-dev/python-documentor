from django.db import connection


def exp_doc(request):
    user_id = int(request.GET.get('user_id', 0) or 0)
    exp_to  = str(request.GET.get('exp_to', '') or '').strip()

    cursor = connection.cursor()
        
    sql1 = f"""SELECT dd2.*, (SELECT GROUP_CONCAT(dt.tag_name, ', ') FROM documentor_document_tags dt WHERE dt.document_id = dd2.id) AS tags
               FROM documentor_documents dd2
               WHERE (dd2.department_id IN (SELECT mau.department_id FROM mainapp_users mau WHERE mau.id = %s)
                  OR dd2.department_id IN (SELECT ud.department_id FROM documentor_users_departments ud WHERE ud.user_id = %s))
                  AND dd2.expiration_date <= %s
               ORDER BY dd2.id DESC
    """
    cursor.execute(sql1, [user_id, user_id, exp_to,])
    rows    = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    docs    = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    connection.close()

    return {'docs': docs}