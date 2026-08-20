import pandas as pd
def processar_dados(csv_usuario):
    return pd.read_csv(csv_usuario,chunksize=50000)