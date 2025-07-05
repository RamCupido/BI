from utils.helper import get_or_insert_dim

def load_data(df, cursor, conn):
    for _, row in df.iterrows():
        id_tiempo = get_or_insert_dim(cursor, 'dim_tiempo', ['PERIODO'], [row['periodo']], 'ID_TIEMPO')
        id_ubicacion = get_or_insert_dim(cursor, 'dim_ubicacion', ['PROVINCIA', 'REGION'], [row['PROVINCIA'], row['REGION']], 'ID_UBICACION')
        id_persona = get_or_insert_dim(cursor, 'dim_persona', ['SEXO', 'EDAD', 'ESTADO_CIVIL', 'NIVEL_INSTRUCCION', 'ANALFABETO'],
                                       [row['SEXO'], row['EDAD'], row['ESTADO_CIVIL'], row['NIVEL_INSTRUCCION'], row['ANALFABETO']],
                                       'ID_PERSONA')
        
        cursor.execute("""
            INSERT INTO hechos_enemdu (
                ID_TIEMPO, ID_UBICACION, ID_PERSONA,
                INGRESO_LABORAL, INGRESO_PENSION, POBREZA,
                EXTREMA_POBREZA, EMPLEO, FEXP
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_tiempo, id_ubicacion, id_persona,
            row['ingrl'], row['INGRESO_PENSION'],
            row['POBREZA'], row['EXTREMA_POBREZA'],
            row['empleo'], row['fexp']
        ))
    conn.commit()
