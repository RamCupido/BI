import pyodbc

def get_connection():
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=localhost;'
        'DATABASE=OLAP01;'
        'UID=sa;'
        'PWD=TuPassword123!'
    )
