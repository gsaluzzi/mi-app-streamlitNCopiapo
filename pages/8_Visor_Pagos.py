
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from componentes import subheader_custom
from utilities import get_gsheet_df


def grafico_monto_por_mes_estado(
    df,
    col_mes="MES EJERCICIO",
    col_monto="MONTO",
    col_estado="ESTADO",
    color_pagada="#39BA1F",
    color_no_pagada="#F91F06"
):
    """
    Gráfico de barras por mes con color según estado de pago.
    """

    df = df.copy()

    # Asegurar monto numérico
    df[col_monto] = pd.to_numeric(df[col_monto], errors="coerce")

    # ORDEN CRONOLÓGICO DE MESES (AQUÍ)
    orden_meses = [
        "Septiembre", "Octubre", "Noviembre", "Diciembre","Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto"
    ]

    df[col_mes] = pd.Categorical(
        df[col_mes],
        categories=orden_meses,
        ordered=True
    )

    # Agrupar
    resumen = (
        df.groupby([col_mes, col_estado], observed=True)[col_monto]
        .sum()
        .reset_index()
    )

    meses = resumen[col_mes].unique()

    pagadas = resumen[resumen[col_estado] == "PAGADA"]
    no_pagadas = resumen[resumen[col_estado] == "NO PAGADA"]



    fig = go.Figure()

    # Barras pagadas
    fig.add_bar(
        x=pagadas[col_mes],
        y=pagadas[col_monto],
        name="Pagadas",
        marker_color=color_pagada,
        text=[f"${v:,.0f}".replace(",", ".") for v in pagadas[col_monto]],
        textposition="outside",
        textfont=dict(size=18, color="black")
    )

    # Barras no pagadas
    fig.add_bar(
        x=no_pagadas[col_mes],
        y=no_pagadas[col_monto],
        name="No pagadas",
        marker_color=color_no_pagada,
        text=[f"${v:,.0f}".replace(",", ".") for v in no_pagadas[col_monto]],
        textposition="outside",
        textfont=dict(size=18, color="black")
    )
    max_monto = resumen[col_monto].max()
    fig.update_yaxes(
        range=[0, max_monto * 1.15]
    )

    fig.update_layout(
        barmode="group",  # 👉 usa "stack" si las quieres apiladas
        yaxis_title="Monto",
        xaxis_title="Mes ejercicio",
        height=250,
        margin=dict(t=60, b=40),
        legend_title="Estado"
    )

    fig.update_traces(
        textposition="outside",
        cliponaxis=False
    )


    return fig


meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

SHEET_ID_FAC = "1N7glUY1cv2bO-H0MZeGtxL0VlNd7f47YohXQOH3TjCY"

df_fac= get_gsheet_df(
    sheet_id=SHEET_ID_FAC,
    worksheet_name="Facturas"
)

df = df_fac.copy()

# Fechas a datetime
df["FECHA EMISION"] = pd.to_datetime(df["FECHA EMISION"], dayfirst=True)
df["FECHA PAGO"] = pd.to_datetime(df["FECHA PAGO"], dayfirst=True, errors="coerce")

# Monto a número
df["MONTO"] = pd.to_numeric(df["MONTO"], errors="coerce")

df_VOLTEX = df[df['PROVEEDOR']=='COPEC VOLTEX']
fig_voltex = grafico_monto_por_mes_estado(df_VOLTEX)
df_CGE=df[df['PROVEEDOR']=='CGE']
fig_cge = grafico_monto_por_mes_estado(df_CGE)
df_COPEC=df[df['PROVEEDOR']=='COPEC LEASING']
fig_copec = grafico_monto_por_mes_estado(df_COPEC)
df_sbs=df[df['PROVEEDOR']=='SBS']
fig_sbs = grafico_monto_por_mes_estado(df_sbs)

df_seguros = df[df['PROVEEDOR']=='Seguros G Suramericana']
fig_seguros = grafico_monto_por_mes_estado(df_seguros)

st.title("📊 Visor de Pagos")
st.markdown("---")

col1, col2= st.columns(2)

with col1:
    subheader_custom("Pagos Mantención Centro de Carga(Copec Voltex)", size=20)
    st.plotly_chart(fig_voltex, use_container_width=True)

with col2:
    subheader_custom("Pagos Energía Flota(CGE/EMOAC)", size=20)
    st.plotly_chart(fig_cge, use_container_width=True)

st.markdown("---")

col3, col4= st.columns(2)

with col3:
    subheader_custom("Pagos Leasing Centro de Carga(Copec)", size=20)
    st.plotly_chart(fig_copec, use_container_width=True)

with col4:
    subheader_custom("Pagos SBS", size=20)
    st.plotly_chart(fig_sbs, use_container_width=True)


st.markdown("---")

col5, col6= st.columns(2)

with col5:
    subheader_custom("Pagos Seguros Generales", size=20)
    st.plotly_chart(fig_seguros, use_container_width=True)
