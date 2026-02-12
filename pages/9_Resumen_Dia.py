import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import datetime as dt
from componentes import fetch_all_from_supabase, kpi_gauge, asignarTerminal, metric_coloreado, subheader_custom


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
# transacciones = get_table_cached("transacciones")
# energia = get_table_cached("energia")


frecuencias = frecuencias.rename(columns={
    "fecha": "Fecha",
    "demanda": "Demanda",
    "terminal": "Terminal",
    "servicio": "Servicio",
    "frecuencia": "Frecuencia"
})
frecuencias["Fecha"] = pd.to_datetime(frecuencias["Fecha"], dayfirst=True)
frecuencias["Terminal"] = frecuencias["Servicio"].apply(asignarTerminal)

regularidad = regularidad.rename(columns={    
    "fecha": "Fecha",
    "promedio": "Promedio",
    "servicio": "Servicio",
    "total": "Total",
    "sentido": "Sentido"
})
regularidad["Fecha"] = pd.to_datetime(regularidad["Fecha"], dayfirst=True)

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


# transacciones = transacciones.rename(columns={
#     "fecha": "Fecha",
#     "transacciones": "Transacciones",
#     "recaudación":"Recaudación",
#     "comisión":"Comisión",
# })
# transacciones["Fecha"] = pd.to_datetime(transacciones["Fecha"], dayfirst=True)

# energia = energia.rename(columns={
#     "fecha": "Fecha_1",
#     "inicio_carga": "Inicio_Carga",
#     "inicio_soc":"Inicio_Soc",
#     "fin_soc":"Fin_Soc",
#     "energía":"Energía",
#     "duración":"Duración",
# })

# energia["Fecha"] = (
#     pd.to_datetime(
#         energia["Inicio_Carga"],
#         format="%d-%m-%Y %H:%M:%S",
#         errors="coerce"
#     )
#     .dt.normalize()
# )


# energia["Fecha"] = pd.to_datetime(energia["Fecha"], dayfirst=True, errors="coerce")





# ---------------------------
# Filtro por fechas
# ---------------------------
st.sidebar.header("Filtros")

fecha_max = frecuencias["Fecha"].max()
fecha_inicio_default = fecha_max - dt.timedelta(days=14)

# fecha_inicio, fecha_fin = st.sidebar.date_input(
#     "Rango de fechas",
#     value=[frecuencias["Fecha"].min(), frecuencias["Fecha"].max()]
# )

rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=[fecha_inicio_default, fecha_max],
    min_value=frecuencias["Fecha"].min(),
    max_value=frecuencias["Fecha"].max()
)

if not (isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2):
    st.stop()

fecha_inicio, fecha_fin = rango_fechas



# fecha_inicio, fecha_fin = st.sidebar.date_input(
#     "Rango de fechas",
#     value=[fecha_inicio_default, fecha_max],
#     min_value=frecuencias["Fecha"].min(),
#     max_value=frecuencias["Fecha"].max()
# )


terminales = ["Todos"] + sorted(frecuencias["Terminal"].dropna().unique().tolist())
terminal_seleccionada = st.sidebar.selectbox(
    "Terminal",
    terminales
)


frecuencias_filtrado = frecuencias[
    (frecuencias["Fecha"] >= pd.to_datetime(fecha_inicio)) &
    (frecuencias["Fecha"] <= pd.to_datetime(fecha_fin))
]

if terminal_seleccionada != "Todos":
    frecuencias_filtrado = frecuencias_filtrado[
        frecuencias_filtrado["Terminal"] == terminal_seleccionada
    ]


regularidad_filtrado = regularidad[
    (regularidad["Fecha"] >= pd.to_datetime(fecha_inicio)) &
    (regularidad["Fecha"] <= pd.to_datetime(fecha_fin))
]

if terminal_seleccionada != "Todos":
    regularidad_filtrado = regularidad_filtrado[
        regularidad_filtrado["Terminal"] == terminal_seleccionada
    ]

puntualidad_filtrado = puntualidad[
    (puntualidad["Fecha"] >= pd.to_datetime(fecha_inicio)) &
    (puntualidad["Fecha"] <= pd.to_datetime(fecha_fin))
]

if terminal_seleccionada != "Todos":
    puntualidad_filtrado = puntualidad_filtrado[
        puntualidad_filtrado["Terminal"] == terminal_seleccionada
    ]

# transacciones_filtrado = transacciones[
#     (transacciones["Fecha"] >= pd.to_datetime(fecha_inicio)) &
#     (transacciones["Fecha"] <= pd.to_datetime(fecha_fin))
#     ]

# energia_filtrado = energia[
#     (energia["Fecha"] >= pd.to_datetime(fecha_inicio)) &
#     (energia["Fecha"] <= pd.to_datetime(fecha_fin))
#     ]



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
    porcentaje_regularidad = regularidad_filtrado["Promedio"].mean() * 100
else:
    porcentaje_regularidad = 0

#-------------------------------PUNTUALIDAD----------------------------------------

if len(puntualidad_filtrado) > 0:
    porcentaje_puntualidad = puntualidad_filtrado["Indicador"].mean() * 100
else:
    porcentaje_puntualidad = 0

#------------------------------Transacciones-----------------------------------------

# tabla_txn=pd.pivot_table(transacciones_filtrado, 
#                      values=["Transacciones", "Recaudación"],
#                      index="Fecha",
#                      aggfunc="sum")
# tabla_txn = tabla_txn.reset_index()


#-----------------------------Energia------------------------------------------------

# energia_filtrado["tipo_carga"] = (
#     pd.to_datetime(energia_filtrado["Inicio_Carga"], format="%d-%m-%Y %H:%M:%S")
#       .dt.hour
#       .between(8, 19)
#       .astype(int)
# )

#-----------------------------Tabla Finanzas----------------------------------------



st.title("📊 Indicadores de Cumplimiento")
st.markdown("---")
subheader_custom(f"{terminal_seleccionada}", size=20)
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
    kpi_gauge("Factor de Pago", list(promedios_tot.values())[0]*0.6 + porcentaje_regularidad*0.3 + porcentaje_puntualidad*0.1),
    use_container_width=True
    )







# st.markdown("---")
# st.dataframe(frecuencias)

# st.markdown("---")
# st.dataframe(puntualidad)

# st.markdown("---")
# st.dataframe(regularidad)



st.markdown("---")
# terminales_aux = ["Todos"] + sorted(frecuencias["Terminal"].dropna().unique().tolist())
# mes_sel = st.selectbox("Selecciona mes", terminales_aux)

# frecuencias_filtrado2=frecuencias_filtrado
# if mes_sel != "Todos":
#     frecuencias_filtrado2 = frecuencias[
#         frecuencias["Terminal"] == mes_sel
#     ]




tabla_fre=pd.pivot_table(frecuencias_filtrado, 
                     values=["Frecuencia"],
                     index=["Fecha","Demanda"],
                    #  columns="Terminal",
                     aggfunc="mean")

tabla_fre2=pd.pivot_table(tabla_fre, 
                     values=["Frecuencia"],
                     index=["Fecha"],
                    #  columns="Terminal",
                     aggfunc="mean")


# puntualidad_filtrado2=puntualidad
# if mes_sel != "Todos":
#     puntualidad_filtrado2 = puntualidad[
#         puntualidad["Terminal"] == mes_sel
#     ]

tabla_punt=pd.pivot_table(puntualidad_filtrado, 
                     values=["Indicador"],
                     index=["Fecha"],
                    #  columns="Terminal",
                     aggfunc="mean")


# regularidad_filtrado2=regularidad
# if mes_sel != "Todos":
#     regularidad_filtrado2 = regularidad[
#         regularidad["Terminal"] == mes_sel
#     ]

tabla_reg=pd.pivot_table(regularidad_filtrado, 
                     values=["Promedio"],
                     index=["Fecha"],
                    #  columns="Terminal",
                     aggfunc="mean")


tabla_aux=pd.merge(tabla_fre2, tabla_reg, on="Fecha", how="left")
tabla_aux2=pd.merge(tabla_aux, tabla_punt, on="Fecha", how="left")
tabla_aux2 = tabla_aux2.fillna(0)

tabla_aux2["Factor Pago"]=tabla_aux2["Frecuencia"]*0.6+tabla_aux2["Promedio"]*0.3+tabla_aux2["Indicador"]*0.1
tabla_aux2= tabla_aux2.reset_index()


#--------------------------Frecuencia---------------------------------
fig_fre=go.Figure()

fig_fre.add_trace(
    go.Scatter(
        x=tabla_aux2["Fecha"],
        y=tabla_aux2["Frecuencia"],
        mode="lines+markers+text",
        text=tabla_aux2["Frecuencia"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="Mi Serie"
    )
)
meta=0.9
color_linea="#2C3E50"
fig_fre.add_hline(
        y=meta,
        line_dash="dash",
        line_color=color_linea,
        annotation_text="Meta",
        annotation_position="top left"
    )

fig_fre.update_layout(title=f"Evolutivo Frecuencias ({terminal_seleccionada})", template='ygridoff')
fig_fre.update_yaxes(range=[0.4,1.2])
fig_fre.update_yaxes(tickformat=".0%")

#-----------------------------------------------------------------------------------------------
#--------------------------Regularidad---------------------------------
fig_reg=go.Figure()

fig_reg.add_trace(
    go.Scatter(
        x=tabla_aux2["Fecha"],
        y=tabla_aux2["Promedio"],
        mode="lines+markers+text",
        text=tabla_aux2["Promedio"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="Mi Serie"
    )
)
meta=0.8
color_linea="#2C3E50"
fig_reg.add_hline(
        y=meta,
        line_dash="dash",
        line_color=color_linea,
        annotation_text="Meta",
        annotation_position="top left"
    )

fig_reg.update_layout(title=f"Evolutivo Regularidad ({terminal_seleccionada})", template='ygridoff')
fig_reg.update_yaxes(range=[0.1,1.1])
fig_reg.update_yaxes(tickformat=".0%")

#-----------------------------------------------------------------------------------------------
#--------------------------Puntualidad---------------------------------
fig_pun=go.Figure()

fig_pun.add_trace(
    go.Scatter(
        x=tabla_aux2["Fecha"],
        y=tabla_aux2["Indicador"],
        mode="lines+markers+text",
        text=tabla_aux2["Indicador"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="Mi Serie"
    )
)
meta=0.7
color_linea="#2C3E50"
fig_pun.add_hline(
        y=meta,
        line_dash="dash",
        line_color=color_linea,
        annotation_text="Meta",
        annotation_position="top left"
    )

fig_pun.update_layout(title=f"Evolutivo Puntualidad ({terminal_seleccionada})", template='ygridoff')
fig_pun.update_yaxes(range=[0,1.1])
fig_pun.update_yaxes(tickformat=".0%")

#-----------------------------------------------------------------------------------------------
#--------------------------Factor de Pago---------------------------------
fig_fac=go.Figure()

fig_fac.add_trace(
    go.Scatter(
        x=tabla_aux2["Fecha"],
        y=tabla_aux2["Factor Pago"],
        mode="lines+markers+text",
        text=tabla_aux2["Factor Pago"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="Mi Serie"
    )
)
meta=0.85
color_linea="#2C3E50"
fig_fac.add_hline(
        y=meta,
        line_dash="dash",
        line_color=color_linea,
        annotation_text="Meta",
        annotation_position="top left"
    )

fig_fac.update_layout(title=f"Evolutivo Factor de Pago ({terminal_seleccionada})", template='ygridoff')
fig_fac.update_yaxes(range=[0,1.1])
fig_fac.update_yaxes(tickformat=".0%")

#-----------------------------------------------------------------------------------------------




st.plotly_chart(fig_fre)
st.plotly_chart(fig_reg)
st.plotly_chart(fig_pun)
st.plotly_chart(fig_fac)


# st.dataframe(tabla_fre)
# st.dataframe(tabla_fre2)


# st.dataframe(tabla_punt)
# st.dataframe(tabla_reg)
st.markdown("---")
# st.dataframe(tabla_aux2)
