import json
from froxa.models import Userfroxa
from powerbi.models import Powerbireports


def get_custom_report(request):
    user_name   = request.POST.get('user_name') or ''
    password    = request.POST.get('password') or ''
    report_name = request.POST.get('report_name') or ''

    userAccount = Userfroxa.objects.filter(name=user_name).first()
    if userAccount is None:
        return {'user_name': None, 'report_name': None, 'res': -1}

    firstLine   = Powerbireports.objects.filter(report_name=report_name).first()

    if firstLine is None or len(user_name) < 3:
        return {'user_name': None, 'report_name': None, 'res': 0}

    users = firstLine.user_names.split(';')
    for user in users:
        if user == user_name and userAccount.password == password:
            return {'user_name': user_name, 'report_name': report_name, 'res': firstLine.report_link}

    return {'user_name': user_name, 'report_name': report_name, 'res': 1}