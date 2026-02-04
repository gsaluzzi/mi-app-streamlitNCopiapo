
import streamlit as st
import pandas as pd
from componentes import subheader_custom
from utilities import get_gsheet_df, grafico_monto_por_mes_estado

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




