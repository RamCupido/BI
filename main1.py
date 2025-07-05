import pandas as pd

# Ruta al archivo CSV original
csv_path = "Data/enemdu_persona_2024_06.csv"

# Columnas objetivo (usamos 'pobre' y 'epobreza' como nombres tentativos)
columns_needed = ['area', 'ciudad', 'p02', 'p03', 'p06', 'p10a', 'p11', 'p72b','fexp', 'ingrl', 'ingpc', 'pobreza', 'epobreza', 'empleo', 'periodo']

# Leer el archivo con delimitador ; y decimal ,
df = pd.read_csv(csv_path, sep=';', encoding='utf-8', decimal=',', low_memory=False)

# Imprimir las columnas reales del archivo
print("Columnas disponibles en el CSV:")
print(df.columns.tolist())

# Confirmar columnas que existen de las que necesitamos
available_columns = [col for col in columns_needed if col in df.columns]
print("\n Columnas que se usarán:")
print(available_columns)

# Filtrar y copiar
df_filtered = df[available_columns].dropna(subset=available_columns).copy()
df_filtered.dropna(subset=available_columns, inplace=True)

# Crear diccionario de mapeo: primeros 2 dígitos código postal → provincia
region_provincia_map = {
    '01': ('Sierra', 'Azuay'), '02': ('Sierra', 'Bolívar'), '03': ('Sierra', 'Cañar'), '04': ('Sierra', 'Carchi'),
    '05': ('Sierra', 'Cotopaxi'), '06': ('Sierra', 'Chimborazo'), '07': ('Costa', 'El Oro'), '08': ('Costa', 'Esmeraldas'),
    '09': ('Costa', 'Guayas'), '10': ('Sierra', 'Imbabura'), '11': ('Sierra', 'Loja'), '12': ('Costa', 'Los Ríos'),
    '13': ('Costa', 'Manabí'), '14': ('Oriente', 'Morona Santiago'), '15': ('Oriente', 'Napo'),
    '16': ('Oriente', 'Pastaza'), '17': ('Sierra', 'Pichincha'), '18': ('Sierra', 'Tungurahua'),
    '19': ('Oriente', 'Zamora Chinchipe'), '20': ('Insular', 'Galápagos'), '21': ('Oriente', 'Sucumbíos'),
    '22': ('Oriente', 'Orellana'), '23': ('Costa', 'Santo Domingo de los Tsáchilas'), '24': ('Costa', 'Santa Elena')
}

# Aplicar mapeo para crear columna PROVINCIA
def get_region_and_provincia(cod):
    try:
        cod_str = str(int(float(cod))).zfill(6)  # asegura que tenga 6 dígitos
        prefix = cod_str[:2]  # extrae los dos primeros
        return region_provincia_map.get(prefix, ('Desconocida', 'Desconocida'))
    except:
        return 'Desconocida'

# Aplicar al DataFrame
df_filtered[['REGION', 'PROVINCIA']] = df_filtered['ciudad'].apply(
    lambda cod: pd.Series(get_region_and_provincia(cod))
)

# Renombrar columnas si están presentes
rename_dict = {}
if 'p02' in df_filtered.columns:
    rename_dict['p02'] = 'SEXO'
if 'p03' in df_filtered.columns:
    rename_dict['p03'] = 'EDAD'
if 'p06' in df_filtered.columns:
    rename_dict['p06'] = 'ESTADO_CIVIL'
if 'p10a' in df_filtered.columns:
    rename_dict['p10a'] = 'NIVEL_INSTRUCCION'
if 'p11' in df_filtered.columns:
    rename_dict['p11'] = 'ANALFABETO'
if 'p72b' in df_filtered.columns:
    rename_dict['p72b'] = 'INGRESO_PENSION'
if 'pobreza' in df_filtered.columns:
    rename_dict['pobreza'] = 'POBREZA'
if 'epobreza' in df_filtered.columns:
    rename_dict['epobreza'] = 'EXTREMA_POBREZA'

df_filtered.rename(columns=rename_dict, inplace=True)

# Mapear valores
if 'SEXO' in df_filtered.columns:
    df_filtered['SEXO'] = df_filtered['SEXO'].replace({1: 'Hombre', 2: 'Mujer'})

if 'ESTADO_CIVIL' in df_filtered.columns:
    df_filtered['ESTADO_CIVIL'] = df_filtered['ESTADO_CIVIL'].replace({
        '1': 'Casado', '2': 'Separado', '3': 'Divorciado', '4': 'Viudo', '5': 'Union Libre', '6': 'Soltero'
    }).fillna('no especificado').apply(lambda x: 'No especificado' if str(x).strip() == '' else x)

if 'ANALFABETO' in df_filtered.columns:
    df_filtered['ANALFABETO'] = df_filtered['ANALFABETO'].apply(lambda x: 'No' if str(x).strip() in ['1', '', 'nan'] else ('Si' if str(x).strip() == '2' else x))

if 'ingrl' in df_filtered.columns:
    df_filtered['ingrl'] = df_filtered['ingrl'].apply(lambda x: 0 if str(x).strip() in ['', 'nan'] else x).fillna(0).astype(float)

if 'empleo' in df_filtered.columns:
    df_filtered['empleo'] = df_filtered['empleo'].apply(lambda x: 'No' if str(x).strip() in ['', 'nan'] else ('Si' if str(x).strip() == '1' else x))

if 'NIVEL_INSTRUCCION' in df_filtered.columns:
    df_filtered['NIVEL_INSTRUCCION'] = df_filtered['NIVEL_INSTRUCCION'].replace({
        '1': 'Ninguno', '2': 'Alfabetización', '3': 'Jardin Infantes', '4': 'Primaria', '5': 'Educación Básica', '6': 'Secuandaria', '7': 'Media/Bachillerato', '8': 'Superior no Universitario', '9': 'Universitario', '10': 'Post grado'
        }).fillna('no especificado').apply(lambda x: 'No especificado' if str(x).strip() == '' else x)

if 'INGRESO_PENSION' in df_filtered.columns:
    df_filtered['INGRESO_PENSION'] = df_filtered['INGRESO_PENSION'].apply(lambda x: 0 if str(x).strip() in ['', 'nan'] else x).fillna(0).astype(float)

# Transformar pobreza y pobreza extrema de forma robusta
def map_pobreza(value):
    try:
        return 'Si' if int(float(str(value).strip())) == 1 else 'No'
    except:
        return 'No'

for col in ['POBREZA', 'EXTREMA_POBREZA']:
    if col in df_filtered.columns:
        df_filtered[col] = df_filtered[col].apply(map_pobreza)


# Guardar archivo Excel
output_excel_path = "datos_depurados_enemdu.xlsx"
df_filtered.to_excel(output_excel_path, index=False)

print(f"\n Archivo generado correctamente en: {output_excel_path}")





