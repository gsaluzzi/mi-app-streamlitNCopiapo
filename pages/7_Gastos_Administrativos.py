
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from utilities import get_gsheet_df
from componentes import subheader_custom
from auth.permissions import require_auth
from auth.auth import check_session_timeout
from ui import render_sidebar_user


check_session_timeout()
require_auth(["admin"])
render_sidebar_user()

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
    fig.add_hrect(
        y0=limite_inf,
        y1=limite_sup,
        fillcolor=color_tolerancia,
        line_width=0,
        annotation_text=f"Tolerancia ±{int(tolerancia_pct*100)}%",
        annotation_position="top left"
    )

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
    fig.update_yaxes(range=[0, max_val * 1.15])

    fig.update_layout(
        title="Costo Real vs Presupuesto",
        yaxis_title="Monto ($)",
        xaxis_title="Mes",
        showlegend=False,
        height=450,
        margin=dict(t=70, b=40)
    )

    return fig


def tabla_glosas_resumen(
    df,
    col_glosa,
    col_monto,
    nombre_total="Total"
):
    """
    Retorna un DataFrame con:
    - Glosa
    - Monto total por glosa
    - % de participación
    - Fila total al final
    """

    df = df.copy()

    # Agrupar y sumar
    resumen = (
        df.groupby(col_glosa, as_index=False)[col_monto]
        .sum()
        .rename(columns={
            col_glosa: "Glosa",
            col_monto: "Monto"
        })
    )

    # Total general
    total_monto = resumen["Monto"].sum()

    # % participación
    resumen["% Participación"] = resumen["Monto"] / total_monto

    # Ordenar de mayor a menor monto
    resumen = resumen.sort_values("Monto", ascending=False)

    # Fila TOTAL
    fila_total = pd.DataFrame({
        "Glosa": [nombre_total],
        "Monto": [total_monto],
        "% Participación": [1.0]
    })

    resumen = pd.concat([resumen, fila_total], ignore_index=True)

    return resumen

def resaltar_total(row, nombre_total="Total"):
    if row["Glosa"] == nombre_total:
        return [
            "font-weight: bold; background-color: #F5F5F5"
        ] * len(row)
    return [""] * len(row)


def formato_moneda_cl(val):
    if pd.isna(val):
        return ""
    return f"${val:,.0f}".replace(",", ".")


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
df_Scot["Monto"] = df_Scot["Cargo"]*-1


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
df_Scot_Cargo_1 = df_Scot_Cargo[~df_Scot_Cargo["Mes Ejercicio"].isin(["Octubre", "Noviembre"])]
# df_Scot_Cargo_Enero = df_Scot_Cargo[df_Scot_Cargo['Mes']=="Enero"]
# tabla=pd.pivot_table(df_Scot_Cargo, 
#                      values=["Cargo"],
#                      index="Glosa 2",
#                      columns="Mes Ejercicio",
#                      aggfunc="sum")


tabla2=pd.pivot_table(df_Scot_Cargo, 
                     values=["Cargo"],
                     index="CCosto",
                     columns="Mes Ejercicio",
                     aggfunc="sum")

tabla2 = tabla2.fillna(0)

df_Scot_admin = df_Scot_Cargo_1[df_Scot_Cargo_1['Glosa 2']=="Gastos Administración"]
presupuesto_admin=20000000
fig_admin=grafico_costo_vs_presupuesto(df_Scot_admin, presupuesto=presupuesto_admin)


df_Scot_Nopre=df_Scot_Cargo_1[df_Scot_Cargo_1['Glosa 2']=="Gastos No Presupuestados"]
presupuesto_Nopre=20000000
fig_Nopre=grafico_costo_vs_presupuesto(df_Scot_Nopre)

# df_Scot_mant = df_Scot_Cargo_1[df_Scot_Cargo_1['Glosa 2']=="Mantención"]
# presupuesto_mant=2000000
# fig_mant=grafico_costo_vs_presupuesto(df_Scot_mant, presupuesto=presupuesto_mant)



meses2 = sorted(df_Scot_admin["Mes Ejercicio"].unique())
opciones = ["TODOS"] + meses2

meses2N = sorted(df_Scot_Nopre["Mes Ejercicio"].unique())
opciones2 = ["TODOS"] + meses2N

# figpie_admin = px.pie(
#     df_Scot_admin,
#     names="CCosto",
#     values='Monto',
#     hole=0.35,
# )

# figpie_admin.update_traces(
#     textinfo="percent",
#     textfont=dict(size=14, color='white', family='Arial Black'),
#     textposition="inside",
# )

# figpie_admin.update_layout(
#     title="Distribución de Gastos Administrativos",
#     template="plotly_white"
# )




st.title("📊 Gastos v/s Presupuesto")
st.markdown("---")

col1, col2= st.columns(2)

with col1:
    subheader_custom("Gastos Administración", size=20)
    st.plotly_chart(fig_admin, use_container_width=True)

with col2:
    subheader_custom("Desglose Gastos", size=20)
    mes_sel = st.selectbox("Selecciona mes", opciones)
    if mes_sel == "TODOS":
        df_filtrado= df_Scot_admin.copy()
    else:
        df_filtrado = df_Scot_admin[df_Scot_admin["Mes Ejercicio"] == mes_sel]
   
    tabla = tabla_glosas_resumen(
    df=df_filtrado,
    col_glosa="CCosto",
    col_monto="Monto"
)
    st.dataframe(
        tabla.style
            .apply(resaltar_total, axis=1)
            .format({
                "Monto": formato_moneda_cl,
                "% Participación": "{:.1%}"
            }),
        hide_index=True
)



st.markdown("---")

col3, col4= st.columns(2)

with col3:
    subheader_custom("Gastos No Presupuestados", size=20)
    st.plotly_chart(fig_Nopre, use_container_width=True)


with col4:
    subheader_custom("Desglose Gastos No Presupuestados", size=20)
    mes_sel2 = st.selectbox("Selecciona Periodo", opciones2)
    if mes_sel2 == "TODOS":
        df_filtrado_Nopre = df_Scot_Nopre.copy()
    else:
        df_filtrado_Nopre = df_Scot_Nopre[df_Scot_Nopre["Mes Ejercicio"] == mes_sel2]
   
    tabla_Nopre = tabla_glosas_resumen(
    df=df_filtrado_Nopre,
    col_glosa="Glosa",
    col_monto="Monto"
)
    st.dataframe(
        tabla_Nopre.style
            .apply(resaltar_total, axis=1)
            .format({
                "Monto": formato_moneda_cl,
                "% Participación": "{:.1%}"
            }),
        hide_index=True
)


# col3, col4= st.columns(2)

# with col3:
#     subheader_custom("Gastos Mantención", size=20)
#     st.plotly_chart(fig_mant, use_container_width=True)


# st.dataframe(df)
# print(df.dtypes)


