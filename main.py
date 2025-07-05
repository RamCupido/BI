from Config.db_config import get_connection
from ETL.extract import extract_csv
from ETL.transform import transform_data
from ETL.load import load_data
from models.schema_creation import create_schema

def main():
    csv_path = 'Data/enemdu_persona_2024_06.csv'
    df = extract_csv(csv_path)
    df_transformed = transform_data(df)

    conn = get_connection()
    cursor = conn.cursor()

    create_schema(cursor, conn)
    load_data(df_transformed, cursor, conn)

    print("✅ Proceso ETL y carga completado correctamente.")

if __name__ == '__main__':
    main()
