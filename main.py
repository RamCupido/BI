from Config.db_config import get_connection
from ETL.extract import extract_csvs
from ETL.transform import transform_persona_data, transform_vivienda_data
from ETL.load import load_persona_data, load_vivienda_data
from models.schema_creation import create_schema_persona
from models.schema_vivienda import create_vivienda_schema

def main():

    conn = get_connection()
    cursor = conn.cursor()
    # --- Personas ---
    df_personas = extract_csvs('Data/Personas')
    df_personas_tr = transform_persona_data(df_personas)
    create_schema_persona(cursor, conn)
    load_persona_data(df_personas_tr, cursor, conn)

    # --- Viviendas ---
    df_viviendas = extract_csvs('Data/Viviendas')
    df_viviendas_tr = transform_vivienda_data(df_viviendas)
    create_vivienda_schema(cursor, conn)
    load_vivienda_data(df_viviendas_tr, cursor, conn)

    print("Proceso ETL y carga completado correctamente.")

if __name__ == '__main__':
    main()
