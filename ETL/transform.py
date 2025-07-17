import pandas as pd

# Mapeo de códigos de región y provincia
region_provincia_map = {
    '01': ('Sierra', 'Azuay'), '02': ('Sierra', 'Bolívar'), '03': ('Sierra', 'Cañar'),
    '04': ('Sierra', 'Carchi'), '05': ('Sierra', 'Cotopaxi'), '06': ('Sierra', 'Chimborazo'),
    '07': ('Costa', 'El Oro'), '08': ('Costa', 'Esmeraldas'), '09': ('Costa', 'Guayas'),
    '10': ('Sierra', 'Imbabura'), '11': ('Sierra', 'Loja'), '12': ('Costa', 'Los Ríos'),
    '13': ('Costa', 'Manabí'), '14': ('Oriente', 'Morona Santiago'), '15': ('Oriente', 'Napo'),
    '16': ('Oriente', 'Pastaza'), '17': ('Sierra', 'Pichincha'), '18': ('Sierra', 'Tungurahua'),
    '19': ('Oriente', 'Zamora Chinchipe'), '20': ('Insular', 'Galápagos'), '21': ('Oriente', 'Sucumbíos'),
    '22': ('Oriente', 'Orellana'), '23': ('Costa', 'Santo Domingo de los Tsáchilas'),
    '24': ('Costa', 'Santa Elena')
}

def get_region_and_provincia(cod):
    """Devuelve (REGION, PROVINCIA) a partir del prefijo de 'ciudad'."""
    try:
        prefix = str(int(float(cod))).zfill(6)[:2]
        return region_provincia_map.get(prefix, ('Desconocida', 'Desconocida'))
    except Exception:
        return ('Desconocida', 'Desconocida')

def transform_persona_data(df):
    print("⏳Transformando datos de persona...")
    cols = ['area', 'ciudad', 'p02', 'p03', 'p06', 'p10a', 'p11', 'p72b',
            'fexp', 'ingrl', 'ingpc', 'pobreza', 'epobreza', 'empleo', 'periodo']
    
    df = df.loc[:, df.columns.intersection(cols)].dropna().drop_duplicates().copy()

    # Convertir 'periodo' a string 'YYYYMM' para varchar
    df['periodo'] = pd.to_datetime(df['periodo'], format='%Y%m', errors='coerce').dt.strftime('%Y')

    # Región / Provincia
    regiones = df['ciudad'].apply(lambda x: pd.Series(get_region_and_provincia(x)))
    df[['REGION', 'PROVINCIA']] = regiones

    # Renombrar columnas
    df.rename(columns={
        'p02': 'SEXO',
        'p03': 'EDAD',
        'p06': 'ESTADO_CIVIL',
        'p10a': 'NIVEL_INSTRUCCION',
        'p11': 'ANALFABETO',
        'p72b': 'INGRESO_PENSION',
        'ingrl': 'INGRESO_LABORAL',
        'ingpc': 'INGRESO_PER_CAPITA',
        'pobreza': 'POBREZA',
        'epobreza': 'EXTREMA_POBREZA'
    }, inplace=True)

    # Mapeos
    df['SEXO'] = df['SEXO'].map({1:'Hombre', 2:'Mujer'}).fillna('Desconocido')
    estado_civil_map = {'1':'Casado','2':'Separado','3':'Divorciado','4':'Viudo','5':'Union Libre','6':'Soltero'}
    df['ESTADO_CIVIL'] = df['ESTADO_CIVIL'].astype(str).str.strip().map(estado_civil_map).fillna('Desconocido')
    df['ANALFABETO'] = (df['ANALFABETO'].astype(str).str.strip().map({'1': 'No', '2': 'Si'}).fillna('No'))

    nivel_map = {
        '1':'Ninguno','2':'Alfabetización','3':'Jardin Infantes','4':'Primaria',
        '5':'Educación Básica','6':'Secundaria','7':'Bachillerato',
        '8':'Superior no Universitario','9':'Universitario','10':'Post grado'
    }
    df['NIVEL_INSTRUCCION'] = df['NIVEL_INSTRUCCION'].astype(str).str.strip().map(nivel_map).fillna('No especificado')
    df['POBREZA'] = df['POBREZA'].astype(str).str.strip().eq('1').map({True:'Si', False:'No'})
    df['EXTREMA_POBREZA'] = df['EXTREMA_POBREZA'].astype(str).str.strip().eq('1').map({True:'Si', False:'No'})
    df['empleo'] = df['empleo'].astype(str).str.strip().eq('1').map({True:'Si', False:'No'})

    numeric_cols = ['INGRESO_LABORAL', 'INGRESO_PENSION', 'INGRESO_PER_CAPITA']
    for col in numeric_cols:
        # Convertimos a str para poder aplicar str.replace
        df[col] = (
            df[col]
            .astype(str)
            .str.replace('.', '', regex=False)  # quita miles
            .str.replace(',', '.', regex=False) # coma a punto
        )
        # Convertimos a float
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)

        df[col] = df[col].replace(999999, 100)

        # Validar y ajustar negativos
        n_neg = (df[col] < 0).sum()
        df[col] = df[col].clip(lower=0)

    df.to_excel('transformado_personas.xlsx', index=False)
    print("✅ Transformación de datos de persona completada")
    return df

def transform_vivienda_data(df):
    print("⏳Transformando datos de vivienda...")
    cols = ['periodo','ciudad','vi02','vi03a','vi04a','vi05a','vi10','vi12']
    df = df.loc[:, df.columns.intersection(cols)].dropna().drop_duplicates().copy()

    # Convertir 'periodo' a string 'YYYYMM' para varchar
    df['periodo'] = pd.to_datetime(df['periodo'], format='%Y%m', errors='coerce').dt.strftime('%Y')

    # Renombrar
    df.rename(columns={
        'vi02':'TIPO_VIVIENDA','vi03a':'MATERIAL_TECHO',
        'vi04a':'MATERIAL_PISO','vi05a':'MATERIAL_PARED',
        'vi10':'ACCESO_AGUA','vi12':'ACCESO_ELECTRICIDAD'
    }, inplace=True)

    # Región / Provincia
    regiones = df['ciudad'].apply(lambda x: pd.Series(get_region_and_provincia(x)))
    df[['REGION','PROVINCIA']] = regiones

    # Mapas de vivienda
    df['TIPO_VIVIENDA'] = df['TIPO_VIVIENDA'].astype(str).str.strip().map({
        '1':'Casa','2':'Departamento','3':'Inquilinato','4':'Mediagua',
        '5':'Rancho/covacha','6':'Choza','7':'Otro'
    }).fillna('No especificado')

    df['MATERIAL_TECHO'] = df['MATERIAL_TECHO'].astype(str).str.strip().map({
        '1':'Hormigón','2':'Fibrocemento','3':'Zinc/Aluminio',
        '4':'Teja','5':'Palma/paja','6':'Otro'
    }).fillna('No especificado')

    df['MATERIAL_PISO'] = df['MATERIAL_PISO'].astype(str).str.strip().map({
        '1':'Madera','2':'Ceramica','3':'Marmol','4':'Ladrillo',
        '5':'Tabla','6':'Caña','7':'Tierra','8':'Otro'
    }).fillna('No especificado')

    df['MATERIAL_PARED'] = df['MATERIAL_PARED'].astype(str).str.strip().map({
        '1':'Hormigo/Bloque/Ladrillo','2':'Asbesto/cemento',
        '3':'Adobe/tapia','4':'Madera','5':'Bahareque','6':'Cartón','7':'Otro'
    }).fillna('No especificado')

    # Binarios de acceso
    df['ACCESO_AGUA'] = df['ACCESO_AGUA'].astype(str).str.strip().isin([str(i) for i in range(1,6)]).map({True:'Si', False:'No'})
    df['ACCESO_ELECTRICIDAD'] = df['ACCESO_ELECTRICIDAD'].astype(str).str.strip().isin(['1','2']).map({True:'Si', False:'No'})

    df.to_excel('transformado_viviendas.xlsx', index=False)
    print("✅ Transformación de datos de vivienda completada")
    return df
