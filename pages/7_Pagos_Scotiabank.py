
import streamlit as st
import pandas as pd

from utilities import get_gsheet_df

meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

SHEET_ID_SCO = "1N7glUY1cv2bO-H0MZeGtxL0VlNd7f47YohXQOH3TjCY"
SHEET_ID_PRE = "14wZ5eAjsynoohGqYP9H6ow38ieeShqqMJpyrfRMQxXg"

df_pre= get_gsheet_df(
    sheet_id=SHEET_ID_PRE,
    worksheet_name="Hoja 1"
)


df_Scot= get_gsheet_df(
    sheet_id=SHEET_ID_SCO,
    worksheet_name="Hoja 1"
)

df_Scot["Fecha"] = pd.to_datetime(df_Scot["Fecha"], dayfirst=True)
df_Scot["Mes"] = df_Scot["Fecha"].dt.month.map(meses)


columnas_numericas = [
    "Cargo",
    "Abono",
    "Saldo Diario"
]

for col in columnas_numericas:
    df_Scot[col] = (
        df_Scot[col]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df_Scot[col] = pd.to_numeric(df_Scot[col], errors="coerce")
df_Scot = df_Scot.fillna(0)
df_Scot["Tipo"]= (df_Scot["Abono"] == 0).astype(int)  #----- 1 es Cargo 0 es Abono------

df_Scot_Cargo = df_Scot[df_Scot['Tipo']==1]
df_Scot_Cargo_Enero = df_Scot_Cargo[df_Scot_Cargo['Mes']=="Enero"]
tabla=pd.pivot_table(df_Scot_Cargo_Enero, 
                     values=["Cargo"],
                     index="Glosa 2",
                    #  columns="Semana",
                     aggfunc="sum")



df_pre2 = df_pre[df_pre['Mes']=='Diciembre']



st.dataframe(df_pre2)
st.dataframe(tabla, use_container_width=False)


# st.dataframe(df)
# print(df.dtypes)


