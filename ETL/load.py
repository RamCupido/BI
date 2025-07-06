from utils.helper import get_or_insert_dim

def load_persona_data(df, cursor, conn):
    for _, row in df.iterrows():
        id_tiempo = get_or_insert_dim(cursor, 'dim_tiempo', ['PERIODO'], [row['periodo']], 'ID_TIEMPO')
        id_ubicacion = get_or_insert_dim(cursor, 'dim_ubicacion', ['PROVINCIA', 'REGION'], [row['PROVINCIA'], row['REGION']], 'ID_UBICACION')
        id_persona = get_or_insert_dim(cursor, 'dim_persona', ['SEXO', 'EDAD', 'ANALFABETO'], [row['SEXO'], row['EDAD'], row['ANALFABETO']], 'ID_PERSONA')
        id_educacion = get_or_insert_dim(cursor, 'dim_educacion', ['NIVEL_INSTRUCCION'], [row['NIVEL_INSTRUCCION']], 'ID_EDUCACION')
        id_estado_civil = get_or_insert_dim(cursor, 'dim_estado_civil', ['ESTADO_CIVIL'], [row['ESTADO_CIVIL']], 'ID_ESTADO_CIVIL')

        cursor.execute("""
            INSERT INTO hechos_enemdu (
                ID_TIEMPO, ID_UBICACION, ID_PERSONA, ID_EDUCACION, ID_ESTADO_CIVIL,
                INGRESO_LABORAL, INGRESO_PENSION, POBREZA, EXTREMA_POBREZA, EMPLEO, FEXP
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            id_tiempo, id_ubicacion, id_persona, id_educacion, id_estado_civil,
            row['ingrl'], row['INGRESO_PENSION'], row['POBREZA'], row['EXTREMA_POBREZA'],
            row['empleo'], row['fexp']
        ))
    conn.commit()
    print("Datos de persona cargados correctamente en la base de datos")


def load_vivienda_data(df, cursor, conn):
    for _, row in df.iterrows():
        id_tiempo = get_or_insert_dim(cursor, 'dim_tiempo', ['PERIODO'], [row['periodo']], 'ID_TIEMPO')
        id_ubicacion = get_or_insert_dim(cursor, 'dim_ubicacion', ['PROVINCIA', 'REGION'], [row['PROVINCIA'], row['REGION']], 'ID_UBICACION')
        id_tipo = get_or_insert_dim(cursor, 'dim_tipo_vivienda', ['DESCRIPCION'], [row['TIPO_VIVIENDA']], 'ID_TIPO_VIVIENDA')
        id_material = get_or_insert_dim(cursor, 'dim_material_vivienda',
            ['MATERIAL_TECHO', 'MATERIAL_PARED', 'MATERIAL_PISO'],
            [row['MATERIAL_TECHO'], row['MATERIAL_PARED'], row['MATERIAL_PISO']],
            'ID_MATERIAL'
        )

        cursor.execute("""
            INSERT INTO hechos_vivienda (
                ID_TIEMPO, ID_UBICACION, ID_TIPO_VIVIENDA, ID_MATERIAL,
                ACCESO_AGUA, ACCESO_ELECTRICIDAD
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            id_tiempo, id_ubicacion, id_tipo, id_material,
            row['ACCESO_AGUA'], row['ACCESO_ELECTRICIDAD']
        ))
    conn.commit()
    print("Datos de vivienda cargados correctamente en la base de datos")