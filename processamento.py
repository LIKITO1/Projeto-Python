import pandas as pd
def processar_dados():
    return pd.read_csv('./dados/car_sales_data.csv',chunksize=50000)