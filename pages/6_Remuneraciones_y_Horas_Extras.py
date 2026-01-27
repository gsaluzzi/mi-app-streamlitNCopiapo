
import streamlit as st
import plotly.express as px
import pandas as pd
from utilities import get_gsheet_df
from componentes import estilo_negrita, metric_coloreado, subheader_custom



st.set_page_config(
    page_title="Remuneraciones Nueva Copiapó",
    layout="wide"
)

# ---------------------------
# Cargar datos
# ---------------------------
# df = pd.read_excel("data/Remuneraciones.xlsx")



SHEET_ID = "1sMIZ5XWCjeMXvfoyiGgQIGBPw_7cNx6cgAnrcg2OhkM"

df= get_gsheet_df(
    sheet_id=SHEET_ID,
    worksheet_name="Hoja 1"
)


df['HoraExtraTotal'] = df['H. EXTRA'] + df['BONO PUESTA EN MARCHA'] + df['COMPENSACION FERIADOS']
df["Tuvo_HE"]= (df['HoraExtraTotal'] >0).astype(int)




# ---------------------------
# Hora Extra por Depto y MES
# ---------------------------

tabla1=pd.pivot_table(df, 
                     values=['HoraExtraTotal'],
                     index="DEPARTAMENTO",
                     columns="MES",
                     aggfunc="sum")
tabla1.columns=tabla1.columns.droplevel(0)
tabla1['TOTAL']=tabla1.sum(axis=1)

for c in list(tabla1.columns):
    tabla1[c] = tabla1[c].apply(lambda x: f"${x:,.0f}".replace(",", "."))


# ---------------------------
# % Dotacion con HE
# ---------------------------

tabla=pd.pivot_table(df, 
                     values=["Tuvo_HE"],
                     index="DEPARTAMENTO",
                     columns="MES",
                     aggfunc="mean")
tabla.columns=tabla.columns.droplevel(0)
tabla=((tabla*100).round(0))

for i in list(tabla.columns):
    tabla[i]=tabla[i].astype(str) + '%'



st.title("Horas Extras")


meses = df["MES"].unique()

cola1, cola2, cola3 = st.columns(3)
with cola1:
    mes_seleccionado = st.selectbox("Elige Mes", meses)

df_mes_seleccionado=df[df['MES']==mes_seleccionado]


colb1, colb2, colb3, colb4 = st.columns(4)

with colb1:
    metric_coloreado("Total Horas Extras", df_mes_seleccionado['HoraExtraTotal'].sum(), delta=None, color_texto='white', color_fondo="#697dd8", formato='moneda' )

with colb2:
    metric_coloreado("Horas Extras", df_mes_seleccionado['H. EXTRA'].sum(), delta=None, color_texto='white', color_fondo="#697dd8", formato='moneda' )

with colb3:
    metric_coloreado("Bono Puesta en Marcha", df_mes_seleccionado['BONO PUESTA EN MARCHA'].sum(), delta=None, color_texto='white', color_fondo="#697dd8", formato='moneda' )

with colb4:
    metric_coloreado("Compensacion feriados", df_mes_seleccionado['COMPENSACION FERIADOS'].sum(), delta=None, color_texto='white', color_fondo="#697dd8", formato='moneda' )

st.markdown("---")
st.subheader("Distribución Total H.Extras")


fig = px.pie(
    df_mes_seleccionado,
    names="DEPARTAMENTO",
    values='HoraExtraTotal',
    hole=0.35,
)

fig.update_traces(
    textinfo="percent",
    textfont=dict(size=14, color='white', family='Arial Black'),
    textposition="inside",
)

fig.update_layout(
    title="Distribución de Categorías",
    template="plotly_white"
)

tabla = pd.pivot_table(
    df_mes_seleccionado,
    index="DEPARTAMENTO",           # filas
    values=['HoraExtraTotal'],
    aggfunc={
        'HoraExtraTotal': ["count", "sum", "mean"]
    },
    fill_value=0
)
tabla.columns=tabla.columns.droplevel(0)
# tabla.columns = [f"{col}_{func}" for col, func in tabla.columns]
tabla = tabla.rename(columns={
    "count": "Cantidad",
    "mean": "Promedio",
    "sum": "Monto Total"
})



colc1, colc2 = st.columns(2)

with colc1:
    st.plotly_chart(fig, use_container_width=True)

with colc2:
    subheader_custom("Por Departamento:")
    st.dataframe(tabla)


st.dataframe(tabla1.style.apply(estilo_negrita, subset=['TOTAL']))

st.dataframe(tabla)



