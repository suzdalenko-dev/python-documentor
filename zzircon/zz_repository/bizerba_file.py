import pyodbc
from froxa.utils.utilities.funcions_file import get_keys


def five_minutes():
    keys = get_keys('bizerba.json')
  
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={keys['host']};"
        f"DATABASE={keys['dbname']};"
        f"UID={keys['user']};"
        f"PWD={keys['password']};"
        "TrustServerCertificate=yes;"
    )

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    query = """SELECT
        (SELECT COUNT(*) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -5, GETDATE()) AND DeviceName = 'CWE' AND ErrorFlag = 0) AS numRows,
        (SELECT SUM(ActualNetWeightValue) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -5, GETDATE()) AND DeviceName = 'CWE' AND ErrorFlag = 0) AS kg5,
        (SELECT SUM(ActualNetWeightValue) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -25, GETDATE()) AND DeviceName = 'CWE') AS kg25,
        (SELECT SUM(ActualNetWeightValue) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -60, GETDATE()) AND DeviceName = 'CWE') AS kg60,
        (SELECT MIN(ArticleName) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -5, GETDATE()) AND DeviceName = 'CWE') AS ArticleName,
        (SELECT MIN(ArticleNumber) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -5, GETDATE()) AND DeviceName = 'CWE') AS ArticleNumber,
        '- - - - - - - - - - - - - -' AS SEPARATE,
        (SELECT COUNT(*) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -5, GETDATE()) AND DeviceName = 'CWE 01' AND ErrorFlag = 0) AS SEG_NumRows,
        (SELECT SUM(ActualNetWeightValue) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -5, GETDATE())  AND DeviceName = 'CWE 01' AND ErrorFlag = 0) AS SEG_Kg5,
        (SELECT SUM(ActualNetWeightValue) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -25, GETDATE()) AND DeviceName = 'CWE 01') AS SEG_kg25,
        (SELECT SUM(ActualNetWeightValue) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -60, GETDATE()) AND DeviceName = 'CWE 01') AS SEG_kg60,
        (SELECT MIN(ArticleName) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -5, GETDATE()) AND DeviceName = 'CWE 01') AS SEG_ArticleName,
        (SELECT MIN(ArticleNumber) FROM PackageRecord WHERE CreationDate >= DATEADD(MINUTE, -5, GETDATE()) AND DeviceName = 'CWE 01') AS SEG_ArticleNumber
    """

     # Ejecutar y obtener resultados
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]
    row = cursor.fetchone()
    materiales = [dict(zip(columns, row))] if row else []

    cursor.close()
    conn.close()

    # Respuesta JSON
    return materiales

    



def bizerba_recent_lines(seconds):
    seconds = int(seconds) 
    # Límite: 12 horas = 43200 segundos
    if seconds > 43200:
        seconds = 43200
    elif seconds < 1:
        seconds = 1  

    keys = get_keys('bizerba.json')
  
    conn_str = (
        "DRIVER={ODBC Driver 18 for SQL Server};"
        f"SERVER={keys['host']};"
        f"DATABASE={keys['dbname']};"
        f"UID={keys['user']};"
        f"PWD={keys['password']};"
        "TrustServerCertificate=yes;"
    )

    
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    query = f"""
        SELECT *
        FROM PackageRecord
        WHERE CreationDate >= DATEADD(SECOND, -{seconds}, GETDATE())
        ORDER BY CreationDate DESC
    """

    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    results = [dict(zip(columns, row)) for row in rows]

    cursor.close()
    conn.close()

    return results

  
