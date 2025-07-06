import pandas as pd

# Mapeo de códigos de región y provincia
region_provincia_map = {
        '01': ('Sierra', 'Azuay'), '02': ('Sierra', 'Bolívar'), '03': ('Sierra', 'Cañar'), '04': ('Sierra', 'Carchi'),
        '05': ('Sierra', 'Cotopaxi'), '06': ('Sierra', 'Chimborazo'), '07': ('Costa', 'El Oro'), '08': ('Costa', 'Esmeraldas'),
        '09': ('Costa', 'Guayas'), '10': ('Sierra', 'Imbabura'), '11': ('Sierra', 'Loja'), '12': ('Costa', 'Los Ríos'),
        '13': ('Costa', 'Manabí'), '14': ('Oriente', 'Morona Santiago'), '15': ('Oriente', 'Napo'),
        '16': ('Oriente', 'Pastaza'), '17': ('Sierra', 'Pichincha'), '18': ('Sierra', 'Tungurahua'),
        '19': ('Oriente', 'Zamora Chinchipe'), '20': ('Insular', 'Galápagos'), '21': ('Oriente', 'Sucumbíos'),
        '22': ('Oriente', 'Orellana'), '23': ('Costa', 'Santo Domingo de los Tsáchilas'), '24': ('Costa', 'Santa Elena')
    }

def transform_persona_data(df):
    columns_needed = ['area', 'ciudad', 'p02', 'p03', 'p06', 'p10a', 'p11', 'p72b', 'fexp', 'ingrl', 'ingpc', 'pobreza', 'epobreza', 'empleo', 'periodo']
    df_filtered = df[[col for col in columns_needed if col in df.columns]].dropna().copy()

    # Obtener región y provincia
    def get_region_and_provincia(cod):
        try:
            prefix = str(int(float(cod))).zfill(6)[:2]
            return region_provincia_map.get(prefix, ('Desconocida', 'Desconocida'))
        except:
            return ('Desconocida', 'Desconocida')

    df_filtered[['REGION', 'PROVINCIA']] = df_filtered['ciudad'].apply(lambda x: pd.Series(get_region_and_provincia(x)))

    df_filtered.rename(columns={
        'p02': 'SEXO',
        'p03': 'EDAD',
        'p06': 'ESTADO_CIVIL',
        'p10a': 'NIVEL_INSTRUCCION',
        'p11': 'ANALFABETO',
        'p72b': 'INGRESO_PENSION',
        'pobreza': 'POBREZA',
        'epobreza': 'EXTREMA_POBREZA'
    }, inplace=True)

    df_filtered['SEXO'] = df_filtered['SEXO'].replace({1: 'Hombre', 2: 'Mujer'})
    
    estado_civil_map = {
    '1': 'Casado', '2': 'Separado', '3': 'Divorciado',
    '4': 'Viudo', '5': 'Union Libre', '6': 'Soltero'
    }

    df_filtered['ESTADO_CIVIL'] = df_filtered['ESTADO_CIVIL'].apply(
        lambda x: estado_civil_map.get(str(x).strip(), 'Desconocido')
    )

    df_filtered['ANALFABETO'] = df_filtered['ANALFABETO'].apply(lambda x: 'No' if str(x).strip() in ['1', '', 'nan'] else 'Si')

    nivel_instruccion_map = {
        '1': 'Ninguno', '2': 'Alfabetización', '3': 'Jardin Infantes', '4': 'Primaria',
        '5': 'Educación Básica', '6': 'Secundaria', '7': 'Bachillerato', '8': 'Superior no Universitario',
        '9': 'Universitario', '10': 'Post grado'
    }

    df_filtered['NIVEL_INSTRUCCION'] = df_filtered['NIVEL_INSTRUCCION'].apply(
        lambda x: nivel_instruccion_map.get(str(x).strip(), 'No especificado')
    )

    df_filtered['POBREZA'] = df_filtered['POBREZA'].apply(lambda x: 'Si' if str(x).strip() == '1' else 'No')
    df_filtered['EXTREMA_POBREZA'] = df_filtered['EXTREMA_POBREZA'].apply(lambda x: 'Si' if str(x).strip() == '1' else 'No')
    df_filtered['empleo'] = df_filtered['empleo'].apply(lambda x: 'Si' if str(x).strip() == '1' else 'No')

    df_filtered['ingrl'] = pd.to_numeric(df_filtered['ingrl'], errors='coerce').fillna(0.0)
    df_filtered['INGRESO_PENSION'] = pd.to_numeric(df_filtered['INGRESO_PENSION'], errors='coerce').fillna(0.0)


    # Exportar a Excel
    df_filtered.to_excel("persona_transformada.xlsx", index=False)

    print("Transformación de datos de persona completada")
    return df_filtered

def transform_vivienda_data(df):
    columns = ['periodo', 'ciudad', 'vi02', 'vi03a', 'vi04a', 'vi05a', 'vi10', 'vi12']
    df_viv = df[columns].dropna().copy()

    df_viv.rename(columns={
        'vi02': 'TIPO_VIVIENDA',
        'vi03a': 'MATERIAL_TECHO',
        'vi04a': 'MATERIAL_PISO',
        'vi05a': 'MATERIAL_PARED',
        'vi10': 'ACCESO_AGUA',
        'vi12': 'ACCESO_ELECTRICIDAD'
    }, inplace=True)

    # Obtener región y provincia
    def get_region_and_provincia(cod):
        try:
            prefix = str(int(float(cod))).zfill(6)[:2]
            return region_provincia_map.get(prefix, ('Desconocida', 'Desconocida'))
        except:
            return ('Desconocida', 'Desconocida')
        
    df_viv[['REGION', 'PROVINCIA']] = df_viv['ciudad'].apply(lambda x: pd.Series(get_region_and_provincia(x)))

    tipo_vivienda_map = {
        '1': 'Casa', '2': 'Departamento', '3': 'Inquilinato', '4': 'Mediagua',
        '5': 'Rancho/covacha', '6': 'Choza', '7': 'Otro'
    }
    material_techo_map = {
        '1': 'Hormigón', '2': 'Fibrocemento', '3': 'Zinc/Aluminio', '4': 'Teja', '5': 'Palma/paja',
        '6': 'Otro'
    }
    material_piso_map = {
        '1': 'Madera', '2': 'Ceramica', '3': 'Marmol', '4': 'Ladrillo', '5': 'Tabla',
        '6': 'Caña', '7': 'Tierra', '8': 'Otro'
    }
    material_pared_map = {
        '1': 'Hormigo/Bloque/Ladrillo', '2': 'Asbesto/cemento', '3': 'Adobe/tapia', '4': 'Madera', '5': 'Bahareque',
        '6': 'Cartón', '7': 'Otro'
    }

    df_viv['TIPO_VIVIENDA'] = df_viv['TIPO_VIVIENDA'].apply(
        lambda x: tipo_vivienda_map.get(str(x).strip(), 'No especificado')
    )

    df_viv['MATERIAL_TECHO'] = df_viv['MATERIAL_TECHO'].apply(
        lambda x: material_techo_map.get(str(x).strip(), 'No especificado')
    )

    df_viv['MATERIAL_PISO'] = df_viv['MATERIAL_PISO'].apply(
        lambda x: material_piso_map.get(str(x).strip(), 'No especificado')
    )

    df_viv['MATERIAL_PARED'] = df_viv['MATERIAL_PARED'].apply(
        lambda x: material_pared_map.get(str(x).strip(), 'No especificado')
    )

    # Normalizar los valores binarios
    df_viv['ACCESO_AGUA'] = df_viv['ACCESO_AGUA'].apply(
        lambda x: 'Si' if str(x).strip() in ['1', '2', '3', '4', '5', '6'] else 'No'
    )

    df_viv['ACCESO_ELECTRICIDAD'] = df_viv['ACCESO_ELECTRICIDAD'].apply(
        lambda x: 'Si' if str(x).strip() in ['1', '2'] else 'No'
    )

    # Exportar a Excel
    df_viv.to_excel("vivienda_transformada.xlsx", index=False)

    print("Transformación de datos de vivienda completada")
    return df_viv
