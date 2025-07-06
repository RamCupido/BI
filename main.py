from Config.db_config import get_connection
from ETL.extract import extract_csv, extract_vivienda_csv
from ETL.transform import transform_persona_data, transform_vivienda_data
from ETL.load import load_persona_data, load_vivienda_data
from models.schema_creation import create_schema_persona
from models.schema_vivienda import create_vivienda_schema

def main():
    # --- Personas ---
    csv_path = 'Data/enemdu_persona_2024_06.csv'
    df = extract_csv(csv_path)
    df_transformed = transform_persona_data(df)

    conn = get_connection()
    cursor = conn.cursor()

    create_schema_persona(cursor, conn)
    load_persona_data(df_transformed, cursor, conn)

    # --- Viviendas ---
    df_vivienda = extract_vivienda_csv('Data/enemdu_vivienda_hogar_2024_06.csv')
    df_vivienda_transformed = transform_vivienda_data(df_vivienda)

    create_vivienda_schema(cursor, conn)
    load_vivienda_data(df_vivienda_transformed, cursor, conn)

    print("Proceso ETL y carga completado correctamente.")

if __name__ == '__main__':
    main()
