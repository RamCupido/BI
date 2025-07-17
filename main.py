from Config.db_config import get_connection
from ETL.extract import extract_csvs
from ETL.transform import transform_persona_data, transform_vivienda_data
from ETL.load import load_persona_data, load_vivienda_data
from models.schema_creation import create_schema_persona
from models.schema_vivienda import create_vivienda_schema

def run_etl():
    """Ejecuta el proceso completo de ETL para persona y vivienda."""
    conn = get_connection()
    cursor = conn.cursor()
    try:
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

        conn.commit()
        print("✅ Proceso ETL y carga completado correctamente.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Ocurrió un error durante el ETL: {e}")
    finally:
        cursor.close()
        conn.close()

def mostrar_menu():
    print("\n=== Menú ETL Índice de Pobreza ===")
    print("1. Ejecutar proceso ETL")
    print("2. Salir")

def ejecutar_menu():
    while True:
        mostrar_menu()
        opcion = input("Selecciona una opción [1-2]: ").strip()
        if opcion == "1":
            print("\n⏳ Iniciando proceso ETL...")
            run_etl()
        elif opcion == "2":
            print("👋 Saliendo. ¡Hasta luego!")
            break
        else:
            print("⚠️ Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    ejecutar_menu()
