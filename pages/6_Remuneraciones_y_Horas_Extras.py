
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utilities import get_gsheet_df
from componentes import estilo_negrita, metric_coloreado, subheader_custom




def grafico_costo_vs_presupuesto(
    df,
    col_mes="Mes Ejercicio",
    col_monto="Monto",
    presupuesto=0,
    tolerancia_pct=0.05,   # ±5%
    color_bajo="#2ECC71",
    color_sobre="#E74C3C",
    color_linea="#2C3E50",
    color_tolerancia="rgba(241,196,15,0.25)"
):
    df = df.copy()

    # -----------------------------
    # Orden meses cronológicamente
    # -----------------------------
    orden_meses = [
        "Septiembre", "Octubre", "Noviembre", "Diciembre","Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto"
    ]

    df[col_mes] = pd.Categorical(df[col_mes], categories=orden_meses, ordered=True)

    resumen = (
        df.groupby(col_mes, observed=True)[col_monto]
        .sum()
        .reset_index()
        .sort_values(col_mes)
    )

    # -----------------------------
    # Variación % vs presupuesto
    # -----------------------------
    if presupuesto == 0:
        resumen["variacion_pct"] = None
    else:
        resumen["variacion_pct"] = (resumen[col_monto] / presupuesto - 1) * 100

    # Colores según presupuesto
    colores = [
        color_sobre if v > presupuesto else color_bajo
        for v in resumen[col_monto]
    ]

    # -----------------------------
    # Límites tolerancia
    # -----------------------------
    limite_inf = presupuesto * (1 - tolerancia_pct)
    limite_sup = presupuesto * (1 + tolerancia_pct)

    # -----------------------------
    # Gráfico
    # -----------------------------
    fig = go.Figure()

    fig.add_bar(
        x=resumen[col_mes],
        y=resumen[col_monto],
        marker_color=colores,
        customdata=resumen["variacion_pct"],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Monto: $%{y:,.0f}<br>"
            "Variación: %{customdata:.1f}% vs presupuesto"
            "<extra></extra>"
        ),
        text=[f"${v:,.0f}".replace(",", ".") for v in resumen[col_monto]],
        textfont=dict(size=12, color='black', family='Arial Black'),
        textposition="outside"
    )

    # -----------------------------
    # Banda de tolerancia
    # -----------------------------
    # fig.add_hrect(
    #     y0=limite_inf,
    #     y1=limite_sup,
    #     fillcolor=color_tolerancia,
    #     line_width=0,
    #     annotation_text=f"Tolerancia ±{int(tolerancia_pct*100)}%",
    #     annotation_position="top left"
    # )

    # Línea presupuesto
    fig.add_hline(
        y=presupuesto,
        line_dash="dash",
        line_color=color_linea,
        annotation_text="Presupuesto",
        annotation_position="top left"
    )

    # Ajuste eje Y
    max_val = max(resumen[col_monto].max(), limite_sup)
    fig.update_yaxes(range=[0, max_val * 1.2])

    fig.update_layout(
        # title="Costo Real vs Presupuesto",
        yaxis_title="Monto ($)",
        xaxis_title="Mes",
        showlegend=False,
        height=450,
        margin=dict(t=70, b=40)
    )

    return fig








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



df_HE_LH = df[df['DEPARTAMENTO']=="CONDUCTORES - LOS HEROES"]
fig_HE_LH = grafico_costo_vs_presupuesto(df_HE_LH, col_mes="MES", col_monto='HoraExtraTotal')
df_HE_PAIPO = df[df['DEPARTAMENTO']=="CONDUCTORES - PAIPOTE"]
fig_HE_PAIPO = grafico_costo_vs_presupuesto(df_HE_PAIPO, col_mes="MES", col_monto='HoraExtraTotal')
df_HE_TERRA = df[df['DEPARTAMENTO']=="CONDUCTORES - TERRAPUERTO"]
fig_HE_TERRA = grafico_costo_vs_presupuesto(df_HE_TERRA, col_mes="MES", col_monto='HoraExtraTotal')

print(df_HE_LH)

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


# fig = px.pie(
#     df_mes_seleccionado,
#     names="DEPARTAMENTO",
#     values='HoraExtraTotal',
#     hole=0.35,
# )

# fig.update_traces(
#     textinfo="percent",
#     textfont=dict(size=14, color='white', family='Arial Black'),
#     textposition="inside",
# )

# fig.update_layout(
#     title="Distribución de Categorías",
#     template="plotly_white"
# )

# tabla = pd.pivot_table(
#     df_mes_seleccionado,
#     index="DEPARTAMENTO",           # filas
#     values=['HoraExtraTotal'],
#     aggfunc={
#         'HoraExtraTotal': ["count", "sum", "mean"]
#     },
#     fill_value=0
# )
# tabla.columns=tabla.columns.droplevel(0)
# # tabla.columns = [f"{col}_{func}" for col, func in tabla.columns]
# tabla = tabla.rename(columns={
#     "count": "Cantidad",
#     "mean": "Promedio",
#     "sum": "Monto Total"
# })



colc1, colc2, colc3= st.columns(3)

with colc1:
    subheader_custom("HE Los Heroes", size=20)
    st.plotly_chart(fig_HE_LH, use_container_width=True)

with colc2:
    subheader_custom("H.E. Paipote", size=20)
    st.plotly_chart(fig_HE_PAIPO, use_container_width=True)

with colc3:
    subheader_custom("H.E. Terrapuerto", size=20)
    st.plotly_chart(fig_HE_TERRA, use_container_width=True)


# with colc1:
#     st.plotly_chart(fig, use_container_width=True)

# with colc2:
#     subheader_custom("Por Departamento:")
#     st.dataframe(tabla)


# st.dataframe(tabla1.style.apply(estilo_negrita, subset=['TOTAL']))

# st.dataframe(tabla)






