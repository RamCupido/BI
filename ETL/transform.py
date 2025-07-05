import pandas as pd

def transform_data(df):
    columns_needed = ['area', 'ciudad', 'p02', 'p03', 'p06', 'p10a', 'p11', 'p72b', 'fexp', 'ingrl', 'ingpc', 'pobreza', 'epobreza', 'empleo', 'periodo']
    df_filtered = df[[col for col in columns_needed if col in df.columns]].dropna().copy()

    region_provincia_map = {
        '01': ('Sierra', 'Azuay'), '02': ('Sierra', 'Bolívar'), '03': ('Sierra', 'Cañar'), '04': ('Sierra', 'Carchi'),
        '05': ('Sierra', 'Cotopaxi'), '06': ('Sierra', 'Chimborazo'), '07': ('Costa', 'El Oro'), '08': ('Costa', 'Esmeraldas'),
        '09': ('Costa', 'Guayas'), '10': ('Sierra', 'Imbabura'), '11': ('Sierra', 'Loja'), '12': ('Costa', 'Los Ríos'),
        '13': ('Costa', 'Manabí'), '14': ('Oriente', 'Morona Santiago'), '15': ('Oriente', 'Napo'),
        '16': ('Oriente', 'Pastaza'), '17': ('Sierra', 'Pichincha'), '18': ('Sierra', 'Tungurahua'),
        '19': ('Oriente', 'Zamora Chinchipe'), '20': ('Insular', 'Galápagos'), '21': ('Oriente', 'Sucumbíos'),
        '22': ('Oriente', 'Orellana'), '23': ('Costa', 'Santo Domingo de los Tsáchilas'), '24': ('Costa', 'Santa Elena')
    }

    def get_region_and_provincia(cod):
        try:
            prefix = str(int(float(cod))).zfill(6)[:2]
            return region_provincia_map.get(prefix, ('Desconocida', 'Desconocida'))
        except:
            return ('Desconocida', 'Desconocida')

    df_filtered[['REGION', 'PROVINCIA']] = df_filtered['ciudad'].apply(lambda x: pd.Series(get_region_and_provincia(x)))

    df_filtered.rename(columns={
        'p02': 'SEXO', 'p03': 'EDAD', 'p06': 'ESTADO_CIVIL', 'p10a': 'NIVEL_INSTRUCCION',
        'p11': 'ANALFABETO', 'p72b': 'INGRESO_PENSION', 'pobreza': 'POBREZA', 'epobreza': 'EXTREMA_POBREZA'
    }, inplace=True)

    df_filtered['SEXO'] = df_filtered['SEXO'].replace({1: 'Hombre', 2: 'Mujer'})
    df_filtered['ESTADO_CIVIL'] = df_filtered['ESTADO_CIVIL'].replace({
        '1': 'Casado', '2': 'Separado', '3': 'Divorciado', '4': 'Viudo', '5': 'Union Libre', '6': 'Soltero'
    }).fillna('No especificado')
    df_filtered['ANALFABETO'] = df_filtered['ANALFABETO'].apply(lambda x: 'No' if str(x).strip() in ['1', '', 'nan'] else 'Si')
    df_filtered['NIVEL_INSTRUCCION'] = df_filtered['NIVEL_INSTRUCCION'].replace({
        '1': 'Ninguno', '2': 'Alfabetización', '3': 'Jardin Infantes', '4': 'Primaria',
        '5': 'Educación Básica', '6': 'Secundaria', '7': 'Bachillerato', '8': 'Superior no Universitario',
        '9': 'Universitario', '10': 'Post grado'
    }).fillna('No especificado')

    df_filtered['POBREZA'] = df_filtered['POBREZA'].apply(lambda x: 'Si' if str(x).strip() == '1' else 'No')
    df_filtered['EXTREMA_POBREZA'] = df_filtered['EXTREMA_POBREZA'].apply(lambda x: 'Si' if str(x).strip() == '1' else 'No')
    df_filtered['empleo'] = df_filtered['empleo'].apply(lambda x: 'Si' if str(x).strip() == '1' else 'No')

    df_filtered['ingrl'] = pd.to_numeric(df_filtered['ingrl'], errors='coerce').fillna(0.0)
    df_filtered['INGRESO_PENSION'] = pd.to_numeric(df_filtered['INGRESO_PENSION'], errors='coerce').fillna(0.0)

    return df_filtered
