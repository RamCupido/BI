import os
import glob
import pandas as pd

def extract_csvs(input_path, *, sep=';', encoding='utf-8', decimal=',', thousands='.', low_memory=False):
    
    # Comprobamos si es carpeta o archivo
    if os.path.isdir(input_path):
        pattern = os.path.join(input_path, '*.csv')
        archivos = glob.glob(pattern)
        if not archivos:
            raise FileNotFoundError(f"❌ No se encontraron CSV en {input_path}")
    elif os.path.isfile(input_path):
        archivos = [input_path]
    else:
        raise FileNotFoundError(f"❌ No existe el archivo o carpeta: {input_path}")

    # Leemos y almacenamos cada DataFrame
    dfs = []
    for ruta in archivos:
        df = pd.read_csv(ruta,
                         sep=sep,
                         encoding=encoding,
                         decimal=decimal,
                         thousands=thousands,
                         low_memory=low_memory)
        print(f"✅ CSV cargado correctamente desde: {ruta}")
        dfs.append(df)

    # Concatenamos y devolvemos
    df_all = pd.concat(dfs, ignore_index=True)
    print(f"🔃​  Total de archivos concatenados: {len(dfs)} → {df_all.shape[0]} filas")
    return df_all
