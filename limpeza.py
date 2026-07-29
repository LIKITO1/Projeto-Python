def limpar_dados(df):
    #Por enquanto só fiz a limpeza de strings
    df["Sale_Date"]=df["Sale_Date"].str.strip()
    df["Salesperson"]=df["Salesperson"].str.strip().str.title()
    df["Customer_Gender"]=df["Customer_Gender"].str.strip().str.title()
    df["Car_Make"]=df["Car_Make"].str.strip().str.title()
    df["Car_Model"]=df["Car_Model"].str.strip().str.title()
    df["Fuel_Type"]=df["Fuel_Type"].str.strip().str.title()
    df["Transmission"]=df["Transmission"].str.strip().str.title()
    df["Payment_Method"]=df["Payment_Method"].str.strip().str.title()
    df["State"]=df["State"].str.strip().str.upper()
    df["City"]=df["City"].str.strip().str.title()
    return df