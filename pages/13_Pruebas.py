
import streamlit as st
import pandas as pd
from datetime import datetime
from utilities import get_gsheet_df
from auth.permissions import require_auth, check_session_timeout
# from auth.auth import check_session_timeout
from ui import render_sidebar_user




from componentes import (
    fetch_all_from_supabase,
    kpi_gauge,
    asignarTerminal,
    metric_coloreado,
    subheader_custom,
    barra_carga_por_tipo,
    dias_restantes_mes_detalle,
    promedio_ingresos_por_tipo_dia,
    grafico_carga_3_meses
)

check_session_timeout()
require_auth(["admin"])
render_sidebar_user()

# st.title("Panel de Administración")
# st.write("Solo admins pueden ver esto")



st.set_page_config(layout="wide")

# =====================
# CARGA DE DATOS
# =====================


@st.cache_data(ttl=3600)
def get_table_cached(table_name):
    return fetch_all_from_supabase(table_name)




#------CGE------
SHEET_ID_CGE = "1n4Nv4IJes9cq9SqibBPWIFbqKYaRw7O1kERM2BYxHJM"
#------Presupuesto-------
SHEET_ID_PRE = "14wZ5eAjsynoohGqYP9H6ow38ieeShqqMJpyrfRMQxXg"
#------PAGOS-------
SHEET_ID_PAG = "1N7glUY1cv2bO-H0MZeGtxL0VlNd7f47YohXQOH3TjCY"



costo_cge= get_gsheet_df(
    sheet_id=SHEET_ID_CGE,
    worksheet_name="Hoja 1"
)

# presupuesto= get_gsheet_df(
#     sheet_id=SHEET_ID_PRE,
#     worksheet_name="Hoja 1"
# )

pagos_sco= get_gsheet_df(
    sheet_id=SHEET_ID_PAG,
    worksheet_name="Hoja 2"
)


meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
meses_inv = {v: k for k, v in meses.items()}







# lineas={
#     "1248":"L1",
#     "1249":"L2",
#     "1250":"L3",
#     "1251":"L4",
#     "1252":"L5",
#     "1253":"L6",
#     "1254":"L7",
#     "1255":"L8",
#     "1256":"L9",
#     "1257":"L10",
#     "1258":"L11",
#     "1259":"L12"   
# }




# pagos_sco["Monto"] = pagos_sco["Cargo"]*-1
# pagos_sco = pagos_sco.fillna(0)
# # energia["Fecha"] = pd.to_datetime(energia["Fecha"], dayfirst=True, errors="coerce")

# columnas_numericas = [
#     "Cargo",
#     "Abono",
#     "Saldo Diario"
# ]

# for col in columnas_numericas:
#     pagos_sco[col] = (
#         pagos_sco[col]
#         .astype(str)
#         .str.replace(".", "", regex=False)
#         .str.replace(",", ".", regex=False)
#     )
#     pagos_sco[col] = pd.to_numeric(pagos_sco[col], errors="coerce")

# pagos_sco["Tipo"]= (pagos_sco["Abono"] == 0).astype(int)  #----- 1 es Cargo 0 es Abono------


# df_Scot_Cargo = pagos_sco[pagos_sco['Tipo']==0]
# df_Scot_Cargo_1 = df_Scot_Cargo[~df_Scot_Cargo["Mes Ejercicio"].isin(["Octubre"])]
# df_Scot_Nopre=df_Scot_Cargo_1[df_Scot_Cargo_1['Glosa 2']=="Gastos No Presupuestados"]

# df_Scot_safu=df_Scot_Cargo_1[df_Scot_Cargo_1['Glosa 2']=="Costo Terreno"]
# df_Scot_rrhh=df_Scot_Cargo_1[df_Scot_Cargo_1['Glosa 2']=="Costo Personal"]
# df_Scot_mant=df_Scot_Cargo_1[df_Scot_Cargo_1['Glosa 2']=="Mantencion"]


st.dataframe(pagos_sco)

