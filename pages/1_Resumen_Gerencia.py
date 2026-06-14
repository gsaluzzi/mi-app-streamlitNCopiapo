import streamlit as st
import pandas as pd
from datetime import datetime
from utilities import get_gsheet_df
from auth.permissions import require_auth, check_session_timeout
from ui import render_sidebar_user
from dateutil.relativedelta import relativedelta

from componentes import (
    fetch_all_from_supabase,
    asignarTerminal,
    metric_coloreado,
    subheader_custom
)


check_session_timeout()
require_auth(["admin"])
render_sidebar_user()


@st.cache_data(ttl=3600)
def get_table_cached(table_name):
    return fetch_all_from_supabase(table_name)

# expediciones = get_table_cached("expediciones")
frecuencias = get_table_cached("frecuencias")
regularidad = get_table_cached("regularidad")
puntualidad = get_table_cached("puntualidad")
transacciones = get_table_cached("transacciones")


st.set_page_config(
    page_title="Resumen Gerencia",
    layout="wide")

st.title("📊 Resumen Gerencia")
st.markdown("---")

def indicador_mobile(
    nombre,
    actual,
    anterior,
    ayer
):

    delta_pct = (
        (actual - anterior) / anterior * 100
        if anterior != 0 else 0
    )

    with st.container(border=True):

        st.subheader(nombre)

        st.metric(
            label="Acumulado Mes",
            value=f"{actual:,.0f}",
            delta=f"{delta_pct:.1f}%"
        )

        c1, c2 = st.columns(2)

        with c1:
            st.caption("Mes anterior")
            st.write(f"**{anterior:,.0f}**")

        with c2:
            st.caption("Ayer")
            st.write(f"**{ayer:,.0f}**")


def indicador_compacto(
    nombre,
    actual,
    anterior,
    ayer
):

    delta_pct = (
        (actual - anterior) / anterior * 100
        if anterior != 0 else 0
    )

    with st.container(border=True):

        st.markdown(f"### {nombre}")

        st.metric(
            label="",
            value=f"{actual:,.0f}",
            delta=f"{delta_pct:.1f}%"
        )

        st.markdown(
            f"""
            **Mes Ant.:** {anterior:,.0f}  
            **Ayer:** {ayer:,.0f}
            """
        )


meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
meses_inv = {v: k for k, v in meses.items()}

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




frecuencias = frecuencias.rename(columns={
    "fecha": "Fecha",
    "demanda": "Demanda",
    "terminal": "Terminal",
    "servicio": "Servicio",
    "frecuencia": "Frecuencia"
})
frecuencias["Fecha"] = pd.to_datetime(frecuencias["Fecha"], dayfirst=True)
frecuencias["Terminal"] = frecuencias["Servicio"].apply(asignarTerminal)
frecuencias["Mes"] = frecuencias["Fecha"].dt.month.map(meses)
frecuencias["Año"] = frecuencias["Fecha"].dt.year
frecuencias["Dia"] = frecuencias["Fecha"].dt.day
frecuencias["Mes_numero"] = frecuencias["Fecha"].dt.month



fecha_ref = frecuencias["Fecha"].max()
anio_actual = fecha_ref.year
mes_actual = fecha_ref.month
dia_actual = fecha_ref.day
fecha_mes_ant = fecha_ref - relativedelta(months=1)
mes_ant = fecha_mes_ant.month


frecuencia_acum_actual=frecuencias[frecuencias["Mes_numero"] == mes_actual]
frecuencia_dia_actual=frecuencia_acum_actual[frecuencia_acum_actual["Dia"]==dia_actual]

tabla_evo_tot_actual=pd.pivot_table(frecuencia_acum_actual, 
                     values=["Frecuencia"],
                     index="Demanda",
                    #  columns="Semana",
                     aggfunc="mean")
tabla_evo_tot_actual=((tabla_evo_tot_actual*100).round(0))


tabla_evo_tot_actual = tabla_evo_tot_actual.reset_index()
tabla_evo_tot_actual= tabla_evo_tot_actual.drop("Demanda", axis=1)

promedios_tot = tabla_evo_tot_actual.mean().round(0).to_dict()
fre_final_mes_actual=list(promedios_tot.values())[0] 

frecuencia_acum_anterior=frecuencias[frecuencias["Mes_numero"] == mes_ant]
frecuencia_acum_anterior2=frecuencia_acum_anterior[frecuencia_acum_anterior["Dia"] <=dia_actual]

tabla_evo_tot_ant=pd.pivot_table(frecuencia_acum_anterior2, 
                     values=["Frecuencia"],
                     index="Demanda",
                    #  columns="Semana",
                     aggfunc="mean")
tabla_evo_tot_ant=((tabla_evo_tot_ant*100).round(0))


tabla_evo_tot_ant = tabla_evo_tot_ant.reset_index()
tabla_evo_tot_ant = tabla_evo_tot_ant.drop("Demanda", axis=1)

promedios_tot_ant = tabla_evo_tot_ant.mean().round(0).to_dict()
fre_final_mes_ant=list(promedios_tot_ant.values())[0] 


tabla_evo_tot_dia=pd.pivot_table(frecuencia_dia_actual, 
                     values=["Frecuencia"],
                     index="Demanda",
                    #  columns="Semana",
                     aggfunc="mean")
tabla_evo_tot_dia=((tabla_evo_tot_dia*100).round(0))


tabla_evo_tot_dia = tabla_evo_tot_dia.reset_index()
tabla_evo_tot_dia = tabla_evo_tot_dia.drop("Demanda", axis=1)

promedios_tot_dia = tabla_evo_tot_dia.mean().round(0).to_dict()
fre_final_dia=list(promedios_tot_dia.values())[0] 

#---------------------------------------------------------------------------------------

regularidad = regularidad.rename(columns={    
    "fecha": "Fecha",
    "promedio": "Promedio",
    "servicio": "Servicio",
    "total": "Total",
    "sentido": "Sentido"
})
regularidad["Fecha"] = pd.to_datetime(regularidad["Fecha"], dayfirst=True)
regularidad["Mes"] = regularidad["Fecha"].dt.month.map(meses)
regularidad["Año"] = regularidad["Fecha"].dt.year
regularidad["Dia"] = regularidad["Fecha"].dt.day
regularidad["Mes_numero"] = regularidad["Fecha"].dt.month

regularidad_mes_actual =regularidad[regularidad['Mes_numero']==mes_actual]
reg_final_mes_actual = regularidad_mes_actual["Promedio"].mean() * 100*1.03

regularidad_acum_anterior=regularidad[regularidad["Mes_numero"] == mes_ant]
regularidad_acum_anterior2=regularidad_acum_anterior[regularidad_acum_anterior["Dia"] <=dia_actual]
reg_final_mes_ant=regularidad_acum_anterior2["Promedio"].mean() * 100*1.03

regularidad_dia_actual=regularidad_mes_actual[regularidad_mes_actual["Dia"]==dia_actual]
reg_final_dia=regularidad_dia_actual["Promedio"].mean() * 100

#-------------------------------------------------------------------------------------------------------

puntualidad = puntualidad.rename(columns={
    "fecha": "Fecha",
    "terminal": "Terminal",
    "servicio": "Servicio",
    "indicador": "Indicador"
})
puntualidad["Fecha"] = pd.to_datetime(puntualidad["Fecha"], dayfirst=True)
puntualidad["Terminal"] = puntualidad["Servicio"].apply(asignarTerminal)

puntualidad["Mes"] = puntualidad["Fecha"].dt.month.map(meses)
puntualidad["Año"] = puntualidad["Fecha"].dt.year
puntualidad["Dia"] = puntualidad["Fecha"].dt.day
puntualidad["Mes_numero"] = puntualidad["Fecha"].dt.month

puntualidad_mes_actual =puntualidad[puntualidad['Mes_numero']==mes_actual]
punt_final_mes_actual = puntualidad_mes_actual["Indicador"].mean() * 100

puntualidad_acum_anterior=puntualidad[puntualidad["Mes_numero"] == mes_ant]
puntualidad_acum_anterior2=puntualidad_acum_anterior[puntualidad_acum_anterior["Dia"] <=dia_actual]
punt_final_mes_ant=puntualidad_acum_anterior2["Indicador"].mean() * 100

puntualidad_dia_actual=puntualidad_mes_actual[puntualidad_mes_actual["Dia"]==dia_actual]
punt_final_dia=puntualidad_dia_actual["Indicador"].mean() * 100

#-----------------------------------------------------------------------------------------

transacciones = transacciones.rename(columns={
    "fecha": "Fecha",
    "transacciones": "Transacciones",
    "recaudación":"Recaudación",
    "comisión":"Comisión",
})
transacciones["Fecha"] = pd.to_datetime(transacciones["Fecha"], dayfirst=True)

transacciones["Mes"] = transacciones["Fecha"].dt.month.map(meses)
transacciones["Año"] = transacciones["Fecha"].dt.year
transacciones["Dia"] = transacciones["Fecha"].dt.day
transacciones["Mes_numero"] = transacciones["Fecha"].dt.month

transacciones_mes_actual =transacciones[transacciones['Mes_numero']==mes_actual]
rec_final_mes_actual = transacciones_mes_actual["Recaudación"].sum()
trans_final_mes_actual = transacciones_mes_actual["Transacciones"].sum()

transacciones_acum_anterior=transacciones[transacciones["Mes_numero"] == mes_ant]
transacciones_acum_anterior2=transacciones_acum_anterior[transacciones_acum_anterior["Dia"] <=dia_actual]
rec_final_mes_ant=transacciones_acum_anterior2["Recaudación"].sum()
trans_final_mes_ant=transacciones_acum_anterior2["Transacciones"].sum()

transacciones_dia_actual=transacciones_mes_actual[transacciones_mes_actual["Dia"]==dia_actual]
rec_final_dia=transacciones_dia_actual["Recaudación"].sum()
trans_final_dia=transacciones_dia_actual["Transacciones"].sum()


indicador_compacto(
    "Frecuencia Mes",
    fre_final_mes_actual,
    fre_final_mes_ant,
    fre_final_dia
)

indicador_compacto(
    "Regularidad Mes",
    reg_final_mes_actual,
    reg_final_mes_ant,
    reg_final_dia
)
indicador_compacto(
    "Puntualidad Mes",
    punt_final_mes_actual,
    punt_final_mes_ant,
    punt_final_dia
)
indicador_compacto(
    "Factor de Pago Mes",
    fre_final_mes_actual*0.6+reg_final_mes_actual*0.3+punt_final_mes_actual*0.1,
    fre_final_mes_ant*0.6+reg_final_mes_ant*0.3+punt_final_mes_ant*0.1,
    fre_final_dia*0.6+reg_final_dia*0.3+punt_final_dia*0.1
)
indicador_compacto(
    "Recaudación Mes",
    rec_final_mes_actual,
    rec_final_mes_ant,
    rec_final_dia
)
indicador_compacto(
    "Transacciones Mes",
    trans_final_mes_actual,
    trans_final_mes_ant,
    trans_final_dia
)

# st.dataframe(transacciones)
# print(mes_actual)
# print(fecha_ref)
# print(anio_actual)
# print(dia_actual)
# print(fecha_mes_ant)
# print(mes_ant)
# print(fre_final_mes_actual)

