import pandas as pd

def extract_csv(path):
    return pd.read_csv(path, sep=';', encoding='utf-8', decimal=',', low_memory=False)
