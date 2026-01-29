import streamlit as st
import pandas as pd
from datetime import datetime
from utilities import get_gsheet_df

from componentes import fetch_all_from_supabase, kpi_gauge, asignarTerminal, metric_coloreado, subheader_custom
from componentes import barra_carga_por_tipo, dias_restantes_mes_detalle, promedio_ingresos_por_tipo_dia, grafico_carga_3_meses

st.set_page_config(layout="wide")

# =====================
# CARGA DE DATOS
# =====================


@st.cache_data(ttl=3600)
def get_table_cached(table_name):
    return fetch_all_from_supabase(table_name)

# expediciones = get_table_cached("expediciones")
frecuencias = get_table_cached("frecuencias")
regularidad = get_table_cached("regularidad")
puntualidad = get_table_cached("puntualidad")
transacciones = get_table_cached("transacciones")
energia = get_table_cached("energia")

SHEET_ID = "1n4Nv4IJes9cq9SqibBPWIFbqKYaRw7O1kERM2BYxHJM"

costo_cge= get_gsheet_df(
    sheet_id=SHEET_ID,
    worksheet_name="Hoja 1"
)


meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


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


lineas={
    "1248":"L1",
    "1249":"L2",
    "1250":"L3",
    "1251":"L4",
    "1252":"L5",
    "1253":"L6",
    "1254":"L7",
    "1255":"L8",
    "1256":"L9",
    "1257":"L10",
    "1258":"L11",
    "1259":"L12"   
}

regularidad["Linea"] = regularidad["Servicio"].map(lineas)
regularidad["Terminal"] = regularidad["Linea"].apply(asignarTerminal)


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


transacciones = transacciones.rename(columns={
    "fecha": "Fecha",
    "transacciones": "Transacciones",
    "recaudación":"Recaudación",
    "comisión":"Comisión",
})
transacciones["Fecha"] = pd.to_datetime(transacciones["Fecha"], dayfirst=True)

transacciones["Mes"] = transacciones["Fecha"].dt.month.map(meses)
transacciones["Año"] = transacciones["Fecha"].dt.year


energia = energia.rename(columns={
    "fecha": "Fecha_1",
    "inicio_carga": "Inicio_Carga",
    "inicio_soc":"Inicio_Soc",
    "fin_soc":"Fin_Soc",
    "energía":"Energía",
    "duración":"Duración",
})

energia["Fecha"] = (
    pd.to_datetime(
        energia["Inicio_Carga"],
        format="%d-%m-%Y %H:%M:%S",
        errors="coerce"
    )
    .dt.normalize()
)

energia["Mes"] = energia["Fecha"].dt.month.map(meses)
energia["Año"] = energia["Fecha"].dt.year
energia["Costo"] = 10

energia["tipo_carga"] = (
    pd.to_datetime(energia["Inicio_Carga"], format="%d-%m-%Y %H:%M:%S")
      .dt.hour
      .between(8, 19)
      .astype(int)
)



# energia["Fecha"] = pd.to_datetime(energia["Fecha"], dayfirst=True, errors="coerce")





# ---------------------------
# Filtro por fechas
# ---------------------------
st.sidebar.header("Filtros")


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






meses_act = list(frecuencias["Mes"].unique())

if mes_actual in meses_act:
    index_default = meses_act.index(mes_actual)
else:
    index_default = 0  # fallback por si no existe

mes_seleccionado = st.sidebar.selectbox(
    "Elige Mes",
    meses_act,
    index=index_default
)


terminales = ["Todos"] + sorted(frecuencias["Terminal"].dropna().unique().tolist())
terminal_seleccionada = st.sidebar.selectbox(
    "Terminal",
    terminales
)


frecuencias_filtrado = frecuencias[frecuencias['Mes']==mes_seleccionado]

if terminal_seleccionada != "Todos":
    frecuencias_filtrado = frecuencias_filtrado[
        frecuencias_filtrado["Terminal"] == terminal_seleccionada
    ]


regularidad_filtrado =regularidad[regularidad['Mes']==mes_seleccionado]

if terminal_seleccionada != "Todos":
    regularidad_filtrado = regularidad_filtrado[
        regularidad_filtrado["Terminal"] == terminal_seleccionada
    ]

puntualidad_filtrado =puntualidad[puntualidad['Mes']==mes_seleccionado]

if terminal_seleccionada != "Todos":
    puntualidad_filtrado = puntualidad_filtrado[
        puntualidad_filtrado["Terminal"] == terminal_seleccionada
    ]

transacciones_filtrado = transacciones[transacciones['Mes']==mes_seleccionado]

energia_filtrado = energia[energia['Mes']==mes_seleccionado]



#-------------------------------FRECUENCIA----------------------------------------
if len(frecuencias_filtrado) > 0:
    porcentaje_frecuencias = frecuencias_filtrado["Frecuencia"].mean() * 100
else:
    porcentaje_frecuencias = 0


tabla_evo_tot=pd.pivot_table(frecuencias_filtrado, 
                     values=["Frecuencia"],
                     index="Demanda",
                    #  columns="Semana",
                     aggfunc="mean")
tabla_evo_tot=((tabla_evo_tot*100).round(0))

# tabla_evo.columns=tabla_evo.columns.droplevel(0)
tabla_evo_tot = tabla_evo_tot.reset_index()
tabla_evo_tot= tabla_evo_tot.drop("Demanda", axis=1)

promedios_tot = tabla_evo_tot.mean().round(0).to_dict()

#-------------------------------REGULARIDAD----------------------------------------

if len(regularidad_filtrado) > 0:
    porcentaje_regularidad = regularidad_filtrado["Promedio"].mean() * 100*1.05
else:
    porcentaje_regularidad = 0

#-------------------------------PUNTUALIDAD----------------------------------------

if len(puntualidad_filtrado) > 0:
    porcentaje_puntualidad = puntualidad_filtrado["Indicador"].mean() * 100
else:
    porcentaje_puntualidad = 0

#------------------------------Transacciones-----------------------------------------

tabla_txn=pd.pivot_table(transacciones_filtrado, 
                     values=["Transacciones", "Recaudación", "Comisión"],
                     index="Fecha",
                     aggfunc="sum")
tabla_txn = tabla_txn.reset_index()

recaudacion_actual=tabla_txn["Recaudación"].sum()
promedio_recaudacion=tabla_txn["Recaudación"].mean()
comision_kupos = tabla_txn["Comisión"].sum()

#-----------------------------Energia------------------------------------------------

# energia_filtrado["tipo_carga"] = (
#     pd.to_datetime(energia_filtrado["Inicio_Carga"], format="%d-%m-%Y %H:%M:%S")
#       .dt.hour
#       .between(8, 19)
#       .astype(int)
# )





#-----------------------------Tabla Finanzas----------------------------------------

habiles, sabados, domingos = dias_restantes_mes_detalle(transacciones_filtrado)
prom_habiles, prom_sabados, prom_domingos =promedio_ingresos_por_tipo_dia(tabla_txn, "Fecha", "Recaudación")

factor_faltante = habiles*prom_habiles+sabados*prom_sabados+domingos*prom_domingos
# Factor_pago=(list(promedios_tot.values())[0]*0.6 + porcentaje_regularidad*0.3 + porcentaje_puntualidad*0.1)/100

recaudacion=recaudacion_actual+factor_faltante
subsidio_fijo=621637500
subsidio_variable=207212500
# subsidio_variable=207212500*0.85
total_ingresos=recaudacion+subsidio_fijo+subsidio_variable



tabla_ingresos = pd.DataFrame({
    "Ingresos": [
        "Recaudación",
        "Subsidio Fijo",
        "Subsidio Variable",
        "Total Ingresos"
    ],
    "Monto": [
        recaudacion,
        subsidio_fijo,
        subsidio_variable,
        total_ingresos
    ]
})


personal=280000000
costo_energia=45000000
tecnologia=258145609/12
mantenimiento=2000000
permisos=27000000
terreno=144000000*1.19/12 + 6000000
gastos=31000000
cuotabuses=4249676702/12
cuotacarga=2219.35*40000
credkupos=15289752
total_costos=personal+costo_energia+tecnologia+mantenimiento+permisos+terreno+gastos+cuotabuses+cuotacarga+credkupos



tabla_costos = pd.DataFrame({
    "Costos": [
        "Personal",
        "Energía",
        "Tecnología",
        "Mantenimiento",
        "Permisos y Seguros",
        "Costo Terreno",
        "Gastos Administración",
        "Cuota Flota Buses",
        "Cuota Infraestructura Carga",
        "Credito Kupos",
        "Total Costos"
    ],
    "Monto": [
        personal,
        costo_energia,
        tecnologia,
        mantenimiento,
        permisos,
        terreno,
        gastos,
        cuotabuses,
        cuotacarga,
        credkupos,
        total_costos
    ]
})



def estilo_filas_ingreso(row):
    if row["Ingresos"] == "Total Ingresos":
        return [
            "font-weight: bold; background-color: #DFF0D8;" 
        ] * len(row)
    return [""] * len(row)



def estilo_filas_costo(row):
    if row["Costos"] == "Total Costos":
        return [
            "font-weight: bold; background-color: #F8D7DA;" 
        ] * len(row)
    return [""] * len(row)

styled_table_costos = (
    tabla_costos
    .style
    .apply(estilo_filas_costo, axis=1)
    .format({
        "Monto": lambda x: f"${x:,.0f}".replace(",", ".")
    })
)

tipo_factor=["Real","90%","100%"]

fecha_max=(frecuencias["Fecha"].max()).strftime("%Y-%m-%d %H:%M")

resultado = datetime.strptime(fecha_max, "%Y-%m-%d %H:%M").strftime("%d-%m")

st.title("📊 Dashboard Nueva Copiapó")
subheader_custom(f"(Actualizado al {resultado})", size=20)
st.markdown("---")
subheader_custom("Indicadores de Cumplimiento", size=20)
col1, col2, col3, col4= st.columns(4)

with col1:

    st.plotly_chart(
    kpi_gauge("Frecuencia", list(promedios_tot.values())[0]),
    use_container_width=True
    )

with col2:

    st.plotly_chart(
    kpi_gauge("Regularidad", porcentaje_regularidad),
    use_container_width=True
    )

with col3:

    st.plotly_chart(
    kpi_gauge("Puntualidad", porcentaje_puntualidad),
    use_container_width=True
    )

with col4:

    st.plotly_chart(
    kpi_gauge("ICF", list(promedios_tot.values())[0]*0.6 + porcentaje_regularidad*0.3 + porcentaje_puntualidad*0.1),
    use_container_width=True
    )

st.markdown("---")
subheader_custom("Transacciones Kupos", size=20)
col5, col6, col7, col8= st.columns(4)

with col5:
    metric_coloreado("Transacciones", tabla_txn["Transacciones"].sum(), delta=None, color_texto='white', color_fondo="#697dd8", formato="numero")

with col6:
    # metric_coloreado("Promedio x día", tabla_txn["Transacciones"].mean(), delta=None, color_texto='white', color_fondo="#697dd8", formato="numero")
    metric_coloreado("Recaudación", recaudacion_actual, delta=None, color_texto='white', color_fondo="#09bb15", formato="moneda")

with col7:
    metric_coloreado("Ticket Promedio", recaudacion_actual/tabla_txn["Transacciones"].sum(), delta=None, color_texto='white', color_fondo="#028e8e", formato="moneda")

with col8:
    metric_coloreado("Comisión Kupos", comision_kupos, delta=None, color_texto='white', color_fondo="#d1178d", formato="moneda")

st.markdown("---")


col9, col10, col11= st.columns([1,2,2])

with col9:
    subheader_custom("Energia (MWh)", size=28)
    
    metric_coloreado("Consumo actual Mes", (energia_filtrado["Energía"].sum()/1000).round(2), delta=None, color_texto='white', color_fondo="#f3d218", formato="raw")

with col10:
    subheader_custom("", size=16)
    st.plotly_chart(barra_carga_por_tipo(energia_filtrado), use_container_width=True)

with col11:
    subheader_custom("Últimos 3 meses", size=16)
    st.plotly_chart(grafico_carga_3_meses(energia, costo_cge), use_container_width=True)



st.markdown("---")

subheader_custom("Análisis Financiero", size=22)

col12, col13= st.columns([1,1])

with col12:
    subheader_custom("Ingresos Proyectados", size=20)
    subheader_custom("Escenario del Subsidio", size=14)
    Factor_pago_1 = st.selectbox("Factor de Pago", tipo_factor, index=0)
    
    if Factor_pago_1 =="Real":
        Factor_pago=(list(promedios_tot.values())[0]*0.6 + porcentaje_regularidad*0.3 + porcentaje_puntualidad*0.1)/100
    elif Factor_pago_1=="90%":
        Factor_pago=0.9
    else: Factor_pago =1
    subsidio_variable_ajustado = subsidio_variable * Factor_pago
    
    total_ingresos_ajustado = (
    recaudacion +
    subsidio_fijo +
    subsidio_variable_ajustado
)
    
    tabla_ingresos = pd.DataFrame({
    "Ingresos": [
        "Recaudación",
        "Subsidio Fijo",
        "Subsidio Variable",
        "Total Ingresos"
    ],
    "Monto": [
        recaudacion,
        subsidio_fijo,
        subsidio_variable_ajustado,
        total_ingresos_ajustado
    ]
})   
    styled_table_ingresos = (
    tabla_ingresos
    .style
    .apply(estilo_filas_ingreso, axis=1)
    .format({
        "Monto": lambda x: f"${x:,.0f}".replace(",", ".")
    })
)
      
    st.dataframe(styled_table_ingresos, hide_index=True)
    
       
    
       

with col13:
    subheader_custom("Costos Proyectados", size=20)
    st.dataframe(styled_table_costos, hide_index=True, height=430)


col14 = st.columns(1)
metric_coloreado("Ebitda Proyectado Mes", total_ingresos_ajustado-total_costos, delta=None, color_texto='white', color_fondo="#0e7ccb", formato="moneda")

# st.dataframe(promedios_tot)

