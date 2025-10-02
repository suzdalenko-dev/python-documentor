from froxa.utils.utilities.funcions_file import delete_excel_reports


def delete_excels_files(request):
    x = delete_excel_reports('0')
    delete_excel_reports('1')
    delete_excel_reports('2')

    return {'x': x}