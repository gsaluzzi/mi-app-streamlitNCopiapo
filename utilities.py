import gspread
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from google.oauth2.service_account import Credentials


@st.cache_data(ttl=600)
def get_gsheet_df(sheet_id: str, worksheet_name: str) -> pd.DataFrame:
    """
    Lee una Google Sheet y retorna un DataFrame cacheado.
    """

    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )

        client = gspread.authorize(creds)
        worksheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
        data = worksheet.get_all_records()

        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"❌ Error leyendo Google Sheet: {e}")
        return pd.DataFrame()


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




