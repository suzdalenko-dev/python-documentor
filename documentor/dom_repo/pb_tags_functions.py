from django.db import connection
from documentor.models import Tags, Users_Departments
from mainapp.models import Users


def get_my_tags(request):
    out    = []
    users_table =  Users.objects.values('department_id', 'department_name', 'id', 'name').order_by('department_id')
    dep_id = []

    for dep in users_table:
        if dep['department_id'] not in dep_id:
            dep_id += [dep['department_id']]
            out    += [{'department_id': dep['department_id'], 'name': dep['department_name'], 'users': [], 'tags': []}]

    users_departaments = Users_Departments.objects.values('user_id', 'user_name', 'department_id', 'department_name')
    tags               = Tags.objects.filter().values("department_id", "id", "name").order_by("name")

    for o in out:
        for dep in users_table:
            if o['department_id'] == dep['department_id']:
                o['users'] += [{'id': dep['id'], 'name': dep['name']}]
        for ud in users_departaments:
            if ud['department_id'] == o['department_id']:
                o['users'] += [{'id': ud['user_id'], 'name': ud['user_name']}]
        for t in tags:
            if o['department_id'] == t['department_id']:
                o['tags'] += [{'id': t['id'], 'name': t['name']}]

    return out




def get_tags_dep(request):
    user_id    = int(request.GET.get('user_id'), 0)
   
    cursor = connection.cursor()
    sql = """SELECT * 
             FROM documentor_tags dt
             WHERE 
                dt.department_id IN (SELECT u.department_id FROM mainapp_users u WHERE u.id = %s)
                OR
                dt.department_id IN (SELECT dud.department_id FROM documentor_users_departments dud WHERE dud.user_id = %s)
            ORDER BY dt.name ASC
        """
    
    cursor.execute(sql, [user_id, user_id])
    rows    = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    tags     = [dict(zip(columns, row)) for row in rows]
    
    return {'tags': tags}