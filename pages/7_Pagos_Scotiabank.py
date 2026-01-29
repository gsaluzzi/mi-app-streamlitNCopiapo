
import streamlit as st
import pandas as pd
from datetime import datetime
from componentes import fetch_all_from_supabase


st.set_page_config(
    page_title="Pagos Bancarios",
    layout="wide"
)

# ---------------------------
# Cargar datos
# ---------------------------
# df = pd.read_excel("data/Remuneraciones.xlsx")

@st.cache_data(ttl=3600)
def get_table_cached(table_name):
    return fetch_all_from_supabase(table_name)

df = get_table_cached("PagosScotiabank")


def limpiar_a_numero(serie):
    return (
        serie.astype(str)
             .str.replace(".", "", regex=False)  # quita miles
             .str.replace(",", ".", regex=False) # por si hay decimales
             .pipe(pd.to_numeric, errors="coerce")
    )

meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True)
df["Mes"] = df["Fecha"].dt.month.map(meses)


cols_numericas = ["Cargo","Abono", "Saldo Diario"]

for col in cols_numericas:
    df[col] = limpiar_a_numero(df[col])

df["Tipo"]= (df["Abono"] > 0).astype(int)





meses_es = {
    "january": "Enero",
    "february": "Febrero",
    "march": "Marzo",
    "april": "Abril",
    "may": "Mayo",
    "june": "Junio",
    "july": "Julio",
    "august": "Agosto",
    "september": "Septiembre",
    "october": "Octubre",
    "november": "Noviembre",
    "december": "Diciembre"
}

mes_actual = meses_es[datetime.now().strftime("%B").lower()]






meses_act = list(df["Mes"].unique())

if mes_actual in meses_act:
    index_default = meses_act.index(mes_actual)
else:
    index_default = 0  # fallback por si no existe



st.title("Pagos Bancarios")
cola1, cola2, cola3 = st.columns(3)
with cola1:
    mes_seleccionado = st.selectbox("Elige Mes", meses_act, index=index_default)

df_mes_seleccionado=df[df['Mes']==mes_seleccionado]


df_mes_seleccionado_cargos=df[df['Tipo']==0]
tabla=pd.pivot_table(df_mes_seleccionado_cargos, 
                     values=["Cargo"],
                     index="Glosa",
                     aggfunc="sum")







st.dataframe(tabla, use_container_width=False)


# st.dataframe(df)
# print(df.dtypes)


