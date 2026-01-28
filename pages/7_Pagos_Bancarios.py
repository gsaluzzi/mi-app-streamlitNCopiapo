
import streamlit as st
import plotly.express as px
import pandas as pd
from utilities import get_gsheet_df


st.set_page_config(
    page_title="Pagos Bancarios",
    layout="wide"
)

# ---------------------------
# Cargar datos
# ---------------------------
# df = pd.read_excel("data/Remuneraciones.xlsx")



SHEET_ID = "1N7glUY1cv2bO-H0MZeGtxL0VlNd7f47YohXQOH3TjCY"

df= get_gsheet_df(
    sheet_id=SHEET_ID,
    worksheet_name="Hoja 1"
)

def limpiar_a_numero(serie):
    return (
        serie.astype(str)
             .str.replace(".", "", regex=False)  # quita miles
             .str.replace(",", ".", regex=False) # por si hay decimales
             .pipe(pd.to_numeric, errors="coerce")
    )


cols_numericas = ["Cargo","Abono", "Saldo Diario"]

for col in cols_numericas:
    df[col] = limpiar_a_numero(df[col])



st.dataframe(df)

print(df.dtypes)

