import pandas as pd
import pyodbc

def clean_param(value):
    """
    Convierte numpy scalars u otros objetos con .item() a tipos nativos de Python.
    """
    try:
        return value.item()
    except Exception:
        return value

def bulk_load_dim(cursor, table, key_cols, keys, id_col):
    cols = ','.join(key_cols) + f", {id_col}"
    cursor.execute(f"SELECT {cols} FROM {table}")
    existing = {tuple(row[:-1]): row[-1] for row in cursor.fetchall()}

    # <-- Aseguramos que las claves sean del mismo tipo que en la tabla
    unique_keys = []
    for k in keys:
        casted = []
        for val in k:
            # si la tabla usa INT y val es digito, lo casteamos
            if isinstance(val, str) and val.isdigit():
                casted.append(int(val))
            else:
                casted.append(clean_param(val))
        unique_keys.append(tuple(casted))
    unique_keys = list(set(unique_keys))

    missing = [k for k in unique_keys if k not in existing]
    if missing:
        placeholders = ','.join('?' for _ in key_cols)
        sql = f"INSERT INTO {table} ({','.join(key_cols)}) VALUES ({placeholders})"
        try:
            cursor.executemany(sql, missing)
        except pyodbc.IntegrityError as e:
            if 'Violation of UNIQUE KEY' in str(e):
                pass
            else:
                raise

    cursor.execute(f"SELECT {cols} FROM {table}")
    return {tuple(row[:-1]): row[-1] for row in cursor.fetchall()}


def load_persona_data(df: pd.DataFrame, cursor, conn):
    print("🔄Cargando datos de persona a la Data Warehouse...")
    # 0. Normalizar nulos
    dims = ['periodo','PROVINCIA','REGION','SEXO','EDAD','ANALFABETO']
    df[dims] = df[dims].fillna('Desconocido')
    df[['NIVEL_INSTRUCCION','ESTADO_CIVIL']] = df[['NIVEL_INSTRUCCION','ESTADO_CIVIL']].fillna('Desconocido')
    df[['POBREZA','EXTREMA_POBREZA','empleo']] = df[['POBREZA','EXTREMA_POBREZA','empleo']].fillna('No')

    # 1. Preparar listas de claves
    periodo_keys   = [[clean_param(p)] for p in df['periodo'].dropna().unique()]
    ubic_keys      = df[['PROVINCIA','REGION']].drop_duplicates().values.tolist()
    persona_keys   = df[['SEXO','EDAD','ANALFABETO']].drop_duplicates().values.tolist()
    educa_keys     = [[clean_param(i)] for i in df['NIVEL_INSTRUCCION'].drop_duplicates()]
    estado_keys    = [[clean_param(e)] for e in df['ESTADO_CIVIL'].drop_duplicates()]

    # 2. Bulk-load dimensiones
    periodo_map      = bulk_load_dim(cursor, 'dim_tiempo',        ['PERIODO'],                periodo_keys, 'ID_TIEMPO')
    ubicacion_map    = bulk_load_dim(cursor, 'dim_ubicacion',     ['PROVINCIA','REGION'],     ubic_keys,    'ID_UBICACION')
    persona_map      = bulk_load_dim(cursor, 'dim_persona',       ['SEXO','EDAD','ANALFABETO'], persona_keys, 'ID_PERSONA')
    educa_map        = bulk_load_dim(cursor, 'dim_educacion',     ['NIVEL_INSTRUCCION'],      educa_keys,   'ID_EDUCACION')
    estado_map       = bulk_load_dim(cursor, 'dim_estado_civil',  ['ESTADO_CIVIL'],           estado_keys,  'ID_ESTADO_CIVIL')

    # 3. Mapear IDs en el DataFrame
    df['ID_TIEMPO']       = df['periodo'].map(lambda x: periodo_map.get((clean_param(x),)))
    df['ID_UBICACION']    = df.apply(lambda r: ubicacion_map.get((clean_param(r.PROVINCIA), clean_param(r.REGION))), axis=1)
    df['ID_PERSONA']      = df.apply(lambda r: persona_map.get((clean_param(r.SEXO), clean_param(r.EDAD), clean_param(r.ANALFABETO))), axis=1)
    df['ID_EDUCACION']    = df['NIVEL_INSTRUCCION'].map(lambda x: educa_map.get((clean_param(x),)))
    df['ID_ESTADO_CIVIL'] = df['ESTADO_CIVIL'].map(lambda x: estado_map.get((clean_param(x),)))

    # 4. Filtrar duplicados en la tabla de hechos
    cursor.execute(
        """
        SELECT ID_TIEMPO, ID_UBICACION, ID_PERSONA,
               ID_EDUCACION, ID_ESTADO_CIVIL, FEXP
        FROM hechos_enemdu
        """
    )
    rows = cursor.fetchall()
    existing_keys = set(tuple(row) for row in rows)
    df['__key__'] = list(zip(
        df.ID_TIEMPO, df.ID_UBICACION, df.ID_PERSONA,
        df.ID_EDUCACION, df.ID_ESTADO_CIVIL, df.fexp
    ))
    df_new = df[~df['__key__'].isin(existing_keys)].copy()
    if df_new.empty:
        print("⚠️ No hay registros nuevos para insertar en hechos_enemdu.")
        return

    # 5. Preparar batch de hechos y ejecutar
    cols = [
        'ID_TIEMPO','ID_UBICACION','ID_PERSONA',
        'ID_EDUCACION','ID_ESTADO_CIVIL',
        'INGRESO_LABORAL','INGRESO_PENSION','INGRESO_PER_CAPITA','POBREZA',
        'EXTREMA_POBREZA','empleo','fexp'
    ]
    records = list(df_new[cols].itertuples(index=False, name=None))
    cursor.fast_executemany = True
    cursor.executemany(
        """
        INSERT INTO hechos_enemdu
        (ID_TIEMPO, ID_UBICACION, ID_PERSONA, ID_EDUCACION,
         ID_ESTADO_CIVIL, INGRESO_LABORAL, INGRESO_PENSION, INGRESO_PER_CAPITA,
         POBREZA, EXTREMA_POBREZA, EMPLEO, FEXP)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        records
    )
    conn.commit()
    print(f"✅ {len(records)} filas nuevas insertadas en hechos_enemdu.")


def load_vivienda_data(df: pd.DataFrame, cursor, conn):
    print("🔄Cargando datos de vivienda a la Data Warehouse...")
    # 0. Normalizar nulos
    dims = ['periodo','PROVINCIA','REGION','TIPO_VIVIENDA',
            'MATERIAL_TECHO','MATERIAL_PARED','MATERIAL_PISO']
    df[dims] = df[dims].fillna('No')
    df[['ACCESO_AGUA','ACCESO_ELECTRICIDAD']] = df[['ACCESO_AGUA','ACCESO_ELECTRICIDAD']].fillna('No')

    # 1. Preparar listas de claves
    periodo_keys = [[clean_param(p)] for p in df['periodo'].dropna().unique()]
    ubic_keys    = df[['PROVINCIA','REGION']].drop_duplicates().values.tolist()
    tipo_keys    = [[clean_param(t)] for t in df['TIPO_VIVIENDA'].drop_duplicates()]
    mat_keys     = df[['MATERIAL_TECHO','MATERIAL_PARED','MATERIAL_PISO']].drop_duplicates().values.tolist()

    # 2. Bulk-load dimensiones
    periodo_map      = bulk_load_dim(cursor, 'dim_tiempo',            ['PERIODO'],            periodo_keys, 'ID_TIEMPO')
    ubicacion_map    = bulk_load_dim(cursor, 'dim_ubicacion',         ['PROVINCIA','REGION'], ubic_keys,    'ID_UBICACION')
    tipo_map         = bulk_load_dim(cursor, 'dim_tipo_vivienda',     ['DESCRIPCION'],        tipo_keys,    'ID_TIPO_VIVIENDA')
    mat_map          = bulk_load_dim(cursor, 'dim_material_vivienda', ['MATERIAL_TECHO','MATERIAL_PARED','MATERIAL_PISO'], mat_keys, 'ID_MATERIAL')

    # 3. Mapear IDs
    df['ID_TIEMPO']       = df['periodo'].map(lambda x: periodo_map.get((clean_param(x),)))
    df['ID_UBICACION']    = df.apply(lambda r: ubicacion_map.get((clean_param(r.PROVINCIA), clean_param(r.REGION))), axis=1)
    df['ID_TIPO_VIVIENDA']= df['TIPO_VIVIENDA'].map(lambda x: tipo_map.get((clean_param(x),)))
    df['ID_MATERIAL']     = df.apply(lambda r: mat_map.get((clean_param(r.MATERIAL_TECHO), clean_param(r.MATERIAL_PARED), clean_param(r.MATERIAL_PISO))), axis=1)

    # 4. Filtrar duplicados en hechos_vivienda
    cursor.execute(
        """
        SELECT ID_TIEMPO, ID_UBICACION, ID_TIPO_VIVIENDA, ID_MATERIAL
        FROM hechos_vivienda
        """
    )
    rows_v = cursor.fetchall()
    existing_keys_v = set(tuple(row) for row in rows_v)
    df['__key__'] = list(zip(df.ID_TIEMPO, df.ID_UBICACION, df.ID_TIPO_VIVIENDA, df.ID_MATERIAL))
    df_new_v = df[~df['__key__'].isin(existing_keys_v)].copy()
    if df_new_v.empty:
        print("⚠️ No hay registros nuevos para insertar en hechos_vivienda.")
        return

    # 5. Batch insert hechos_vivienda
    cols_v = ['ID_TIEMPO','ID_UBICACION','ID_TIPO_VIVIENDA','ID_MATERIAL','ACCESO_AGUA','ACCESO_ELECTRICIDAD']
    records_v = list(df_new_v[cols_v].itertuples(index=False, name=None))
    cursor.fast_executemany = True
    cursor.executemany(
        """
        INSERT INTO hechos_vivienda
        (ID_TIEMPO, ID_UBICACION, ID_TIPO_VIVIENDA, ID_MATERIAL,
         ACCESO_AGUA, ACCESO_ELECTRICIDAD)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        records_v
    )
    conn.commit()
    print(f"✅ {len(records_v)} filas nuevas insertadas en hechos_vivienda.")
