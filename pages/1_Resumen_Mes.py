import streamlit as st
import pandas as pd
from datetime import datetime
from utilities import get_gsheet_df


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


#------CGE------
SHEET_ID_CGE = "1n4Nv4IJes9cq9SqibBPWIFbqKYaRw7O1kERM2BYxHJM"
#------Presupuesto-------
SHEET_ID_PRE = "14wZ5eAjsynoohGqYP9H6ow38ieeShqqMJpyrfRMQxXg"


def estilo_variacion_ingreso(val):
    if pd.isna(val):
        return ""
    if val > 0:
        return "color: green; font-weight: bold"
    elif val < 0:
        return "color: red; font-weight: bold"
    else:
        return "color: gray"


def formato_con_flecha(val):
    if pd.isna(val):
        return ""
    if val > 0:
        return f"▲ {val:.2%}"
    elif val < 0:
        return f"▼ {abs(val):.2%}"
    else:
        return f"{val:.2%}"


def estilo_variacion_costo(val):
    if pd.isna(val):
        return ""
    if val < 0:
        return "color: green; font-weight: bold"
    elif val > 0:
        return "color: red; font-weight: bold"
    else:
        return "color: gray"




costo_cge= get_gsheet_df(
    sheet_id=SHEET_ID_CGE,
    worksheet_name="Hoja 1"
)

presupuesto= get_gsheet_df(
    sheet_id=SHEET_ID_PRE,
    worksheet_name="Hoja 1"
)


meses = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
meses_inv = {v: k for k, v in meses.items()}

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

clave_mes=meses_inv[mes_seleccionado]

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

presupuesto_filtrado =presupuesto[presupuesto['Mes']==mes_seleccionado]

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

if pd.isna(prom_sabados):
    prom_sabados=3000000
if pd.isna(prom_domingos):
    prom_domingos=2500000

factor_faltante = habiles*prom_habiles+sabados*prom_sabados+domingos*prom_domingos
# Factor_pago=(list(promedios_tot.values())[0]*0.6 + porcentaje_regularidad*0.3 + porcentaje_puntualidad*0.1)/100

recaudacion=recaudacion_actual+factor_faltante
subsidio_fijo=621637500
subsidio_variable=207212500
# subsidio_variable=207212500*0.85
total_ingresos=recaudacion+subsidio_fijo+subsidio_variable



# tabla_ingresos = pd.DataFrame({
#     "Ingresos": [
#         "Recaudación",
#         "Subsidio Fijo",
#         "Subsidio Variable",
#         "Total Ingresos"
#     ],
#     "Monto": [
#         recaudacion,
#         subsidio_fijo,
#         subsidio_variable,
#         total_ingresos
#     ]
# })


personal=280000000
costo_energia=45000000
tecnologia=21512134
mantenimiento=2000000
permisos=27000000
terreno=144000000*1.19/12 + 6000000
gastos=31000000
cuotabuses=354139725
cuotacarga=91503268
credkupos=15289752
total_costos=personal+costo_energia+tecnologia+mantenimiento+permisos+terreno+gastos+cuotabuses+cuotacarga+credkupos



personal_pre=presupuesto_filtrado["Costo Personal"][clave_mes-1]
energia_pre=presupuesto_filtrado["Energía"][clave_mes-1]
tecno_pre=presupuesto_filtrado["Tecnología"][clave_mes-1]
mante_pre =presupuesto_filtrado["Mantenimiento"][clave_mes-1]
segur_pre=presupuesto_filtrado["Permisos y Seguros"][clave_mes-1]
terre_pre=presupuesto_filtrado["Costo Terreno"][clave_mes-1]
gastos_pre=presupuesto_filtrado["Gastos Administración"][clave_mes-1]
cuotabu_pre=presupuesto_filtrado["Cuota Flota Buses"][clave_mes-1]
cuotacc_pre=presupuesto_filtrado["Cuota CCarga"][clave_mes-1]
credku_pre=presupuesto_filtrado["Credito Kupos"][clave_mes-1]
total_costos_pre = personal_pre+energia_pre+tecno_pre+mante_pre+segur_pre+terre_pre+gastos_pre+cuotabu_pre+cuotacc_pre+credku_pre





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
    "Monto Proyectado": [
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
    ],
    "Monto Presupuesto": [
        personal_pre,
        energia_pre,
        tecno_pre,
        mante_pre,
        segur_pre,
        terre_pre,
        gastos_pre,
        cuotabu_pre,
        cuotacc_pre,
        credku_pre,
        total_costos_pre
    ],
    "Gap": [
        personal/personal_pre - 1,
        costo_energia/energia_pre -1,
        tecnologia/tecno_pre-1,
        mantenimiento/mante_pre-1,
        permisos/segur_pre-1,
        terreno/terre_pre-1,
        gastos/gastos_pre-1,
        cuotabuses/cuotabu_pre-1,
        cuotacarga/cuotacc_pre-1,
        credkupos/credku_pre-1,
        total_costos/total_costos_pre-1
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
    .map(estilo_variacion_costo, subset=["Gap"])
    .format({
        "Monto Proyectado": lambda x: f"${x:,.0f}".replace(",", "."),
        "Monto Presupuesto": lambda x: f"${x:,.0f}".replace(",", "."),
        "Gap": formato_con_flecha
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
    width='stretch'
    )

with col2:

    st.plotly_chart(
    kpi_gauge("Regularidad", porcentaje_regularidad),
    width='stretch'
    )

with col3:

    st.plotly_chart(
    kpi_gauge("Puntualidad", porcentaje_puntualidad),
    width='stretch'
    )

with col4:

    st.plotly_chart(
    kpi_gauge("ICF", list(promedios_tot.values())[0]*0.6 + porcentaje_regularidad*0.3 + porcentaje_puntualidad*0.1),
    width='stretch'
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
    st.plotly_chart(barra_carga_por_tipo(energia_filtrado), width='stretch')

with col11:
    subheader_custom("Últimos 3 meses", size=16)
    st.plotly_chart(grafico_carga_3_meses(energia, costo_cge), width='stretch')



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
    "Monto Proyectado": [
        recaudacion,
        subsidio_fijo,
        subsidio_variable_ajustado,
        total_ingresos_ajustado
    ],
    "Monto Presupuesto": [
        presupuesto_filtrado["Recaudación"][clave_mes-1],
        presupuesto_filtrado["Subsidio Fijo"][clave_mes-1],
        presupuesto_filtrado["Subsidio Variable"][clave_mes-1],
        presupuesto_filtrado["Recaudación"][clave_mes-1]+presupuesto_filtrado["Subsidio Fijo"][clave_mes-1]+presupuesto_filtrado["Subsidio Variable"][clave_mes-1]
    ],
    "Gap": [
        recaudacion/presupuesto_filtrado["Recaudación"][clave_mes-1] - 1,
        subsidio_fijo/presupuesto_filtrado["Subsidio Fijo"][clave_mes-1] -1,
        subsidio_variable_ajustado/presupuesto_filtrado["Subsidio Variable"][clave_mes-1] -1,
        total_ingresos_ajustado/(presupuesto_filtrado["Recaudación"][clave_mes-1]+presupuesto_filtrado["Subsidio Fijo"][clave_mes-1]+presupuesto_filtrado["Subsidio Variable"][clave_mes-1]) -1
    ]
    
})   
    styled_table_ingresos = (
    tabla_ingresos
    .style
    .apply(estilo_filas_ingreso, axis=1)
    .map(estilo_variacion_ingreso, subset=["Gap"])
    .format({
        "Monto Proyectado": lambda x: f"${x:,.0f}".replace(",", "."),
        "Monto Presupuesto": lambda x: f"${x:,.0f}".replace(",", "."),
        "Gap": formato_con_flecha
    })
)

      
    st.dataframe(styled_table_ingresos, hide_index=True)
    
       
    
       

with col13:
    subheader_custom("Costos Proyectados", size=20)
    st.dataframe(styled_table_costos, hide_index=True, height=430)


col14 = st.columns(1)
metric_coloreado("Ebitda Proyectado Mes", total_ingresos_ajustado-total_costos, delta=None, color_texto='white', color_fondo="#0e7ccb", formato="moneda")

# st.dataframe(promedios_tot)

