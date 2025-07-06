from os import path
import pandas as pd

def extract_csv(path):
    df = pd.read_csv(path, sep=';', encoding='utf-8', decimal=',', low_memory=False)
    print("Archivo CSV de persona cargado correctamente desde:", path)
    return df

def extract_vivienda_csv(path):
    df = pd.read_csv(path, sep=';', encoding='utf-8', decimal=',', low_memory=False)
    print("Archivo CSV de vivienda cargado correctamente desde:", path)
    return df
