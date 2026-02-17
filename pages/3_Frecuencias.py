import streamlit as st
import plotly.express as px
import pandas as pd
import datetime as dt
from componentes import kpi_gauge, asignarTerminal, semana_relativa, fetch_all_from_supabase
from auth.permissions import require_auth, check_session_timeout
# from auth.auth import check_session_timeout
from ui import render_sidebar_user


check_session_timeout()
require_auth(["admin", "viewer"])
render_sidebar_user()

st.set_page_config(
    page_title="Indicador de Frecuencia",
    layout="wide"
)


@st.cache_data(ttl=3600)
def get_table_cached(table_name):
    return fetch_all_from_supabase(table_name)

df = get_table_cached("frecuencias")

df = df.rename(columns={
    "fecha": "Fecha",
    "demanda": "Demanda",
    "terminal": "Terminal",
    "servicio": "Servicio",
    "frecuencia": "Frecuencia"
})



# ---------------------------
# Cargar datos
# ---------------------------
# df = pd.read_excel("data/Frecuencia.xlsx")
df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True)
df["Terminal"] = df["Servicio"].apply(asignarTerminal)
df["Semana"]= semana_relativa(df["Fecha"], "2025-10-13")



# ---------------------------
# Filtro por fechas
# ---------------------------
st.sidebar.header("Filtros")

# fecha_inicio, fecha_fin = st.sidebar.date_input(
#     "Rango de fechas",
#     value=[df["Fecha"].min(), df["Fecha"].max()]
# )

fecha_max = df["Fecha"].max()
fecha_inicio_default = fecha_max - dt.timedelta(days=14)


rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=[fecha_inicio_default, fecha_max],
    min_value=df["Fecha"].min(),
    max_value=df["Fecha"].max()
)

if not (isinstance(rango_fechas, (list, tuple)) and len(rango_fechas) == 2):
    st.stop()

fecha_inicio, fecha_fin = rango_fechas


df_filtrado = df[
    (df["Fecha"] >= pd.to_datetime(fecha_inicio)) &
    (df["Fecha"] <= pd.to_datetime(fecha_fin))
]

# ---------------------------
# KPI: % de válidas
# ---------------------------
if len(df_filtrado) > 0:
    porcentaje_validas = df_filtrado["Frecuencia"].mean() * 100
else:
    porcentaje_validas = 0



df_filtrado_paipo=df_filtrado[df_filtrado['Terminal'] =='Paipote']
if len(df_filtrado_paipo) > 0:
    porcentaje_validas_paipo = df_filtrado_paipo["Frecuencia"].mean() * 100
else:
    porcentaje_validas_paipo = 0


df_filtrado_terra=df_filtrado[df_filtrado['Terminal'] =='Terrapuerto']
if len(df_filtrado_terra) > 0:
    porcentaje_validas_terra = df_filtrado_terra["Frecuencia"].mean() * 100
else:
    porcentaje_validas_terra = 0


df_filtrado_lh=df_filtrado[df_filtrado['Terminal'] =='Los Heroes']
if len(df_filtrado_lh) > 0:
    porcentaje_validas_lh = df_filtrado_lh["Frecuencia"].mean() * 100
else:
    porcentaje_validas_lh = 0




# ---------------------------
# KPI: % de válidas SEMANA (TABLA)
# ---------------------------




tabla_evo=pd.pivot_table(df, 
                     values=["Frecuencia"],
                     index="Demanda",
                     columns="Semana",
                     aggfunc="mean")
tabla_evo=((tabla_evo*100).round(0))

tabla_evo.columns=tabla_evo.columns.droplevel(0)
tabla_evo = tabla_evo.reset_index()
tabla_evo= tabla_evo.drop("Demanda", axis=1)

promedios = tabla_evo.mean().round(0).to_dict()


tabla_evo2=pd.DataFrame([promedios])


fig = px.line(x=list(promedios.keys()), y=list(promedios.values()))

fig.update_traces(
    mode="lines+markers+text",
    marker = dict(size=12),
    text = list(promedios.values()),
    textfont=dict(size=12, color='black', family='Arial Black'),
    textposition="top center",
    line=dict(width=3)    
)

meta=90
color_linea="#2C3E50"
fig.add_hline(
        y=meta,
        line_dash="dash",
        line_color=color_linea,
        annotation_text="Meta",
        annotation_position="top left"
    )



fig.update_layout(title="% Frecuencia por semana", template='ygridoff')
fig.update_yaxes(range=[0, 100])




tabla_evo_lh=pd.pivot_table(df_filtrado_lh, 
                     values=["Frecuencia"],
                     index="Demanda",
                    #  columns="Semana",
                     aggfunc="mean")
tabla_evo_lh=((tabla_evo_lh*100).round(0))
# tabla_evo_lh.columns=tabla_evo_lh.columns.droplevel(0)
tabla_evo_lh = tabla_evo_lh.reset_index()
tabla_evo_lh= tabla_evo_lh.drop("Demanda", axis=1)

promedio_lh = tabla_evo_lh.mean().round(0).to_dict()


tabla_evo_paipo=pd.pivot_table(df_filtrado_paipo, 
                     values=["Frecuencia"],
                     index="Demanda",
                    #  columns="Semana",
                     aggfunc="mean")
tabla_evo_paipo=((tabla_evo_paipo*100).round(0))
# tabla_evo_paipo.columns=tabla_evo_paipo.columns.droplevel(0)
tabla_evo_paipo = tabla_evo_paipo.reset_index()
tabla_evo_paipo= tabla_evo_paipo.drop("Demanda", axis=1)

promedio_paipo = tabla_evo_paipo.mean().round(0).to_dict()


tabla_evo_terra=pd.pivot_table(df_filtrado_terra, 
                     values=["Frecuencia"],
                     index="Demanda",
                    #  columns="Semana",
                     aggfunc="mean")
tabla_evo_terra=((tabla_evo_terra*100).round(0))
# tabla_evo_terra.columns=tabla_evo_terra.columns.droplevel(0)
tabla_evo_terra= tabla_evo_terra.reset_index()
tabla_evo_terra= tabla_evo_terra.drop("Demanda", axis=1)

promedio_terra = tabla_evo_terra.mean().round(0).to_dict()


tabla_evo_tot=pd.pivot_table(df_filtrado, 
                     values=["Frecuencia"],
                     index="Demanda",
                    #  columns="Semana",
                     aggfunc="mean")
tabla_evo_tot=((tabla_evo_tot*100).round(0))

# tabla_evo.columns=tabla_evo.columns.droplevel(0)
tabla_evo_tot = tabla_evo_tot.reset_index()
tabla_evo_tot= tabla_evo_tot.drop("Demanda", axis=1)

promedios_tot = tabla_evo_tot.mean().round(0).to_dict()

#-------------Paipote--------------

df_paipo=df[df['Terminal'] =='Paipote']
tabla_paipo=pd.pivot_table(df_paipo, 
                     values=["Frecuencia"],
                     index="Demanda",
                     columns="Semana",
                     aggfunc="mean")
tabla_paipo=((tabla_paipo*100).round(0))

tabla_paipo.columns=tabla_paipo.columns.droplevel(0)
tabla_paipo = tabla_paipo.reset_index()
tabla_paipo= tabla_paipo.drop("Demanda", axis=1)

promedios_paipo = tabla_paipo.mean().round(0).to_dict()


tabla_paipo2=pd.DataFrame([promedios_paipo])


#-------------Terrapuerto--------------

df_terra=df[df['Terminal'] =='Terrapuerto']
tabla_terra=pd.pivot_table(df_terra, 
                     values=["Frecuencia"],
                     index="Demanda",
                     columns="Semana",
                     aggfunc="mean")
tabla_terra=((tabla_terra*100).round(0))

tabla_terra.columns=tabla_terra.columns.droplevel(0)
tabla_terra = tabla_terra.reset_index()
tabla_terra= tabla_terra.drop("Demanda", axis=1)

promedios_terra = tabla_terra.mean().round(0).to_dict()


tabla_terra2=pd.DataFrame([promedios_terra])

#-------------Los Heroés--------------

df_lh=df[df['Terminal'] =='Los Heroes']
tabla_lh=pd.pivot_table(df_lh, 
                     values=["Frecuencia"],
                     index="Demanda",
                     columns="Semana",
                     aggfunc="mean")
tabla_lh=((tabla_lh*100).round(0))

tabla_lh.columns=tabla_lh.columns.droplevel(0)
tabla_lh = tabla_lh.reset_index()
tabla_lh= tabla_lh.drop("Demanda", axis=1)

promedios_lh = tabla_lh.mean().round(0).to_dict()


tabla_lh2=pd.DataFrame([promedios_lh])

#--------------------------------------------------

df_frecTerm= pd.DataFrame({
    "Paipote": promedios_paipo,
    "Terrapuerto": promedios_terra,
    "Los Heroes": promedios_lh
})

df_frecTerm = df_frecTerm.reset_index().rename(columns={"index":"Semana"})

fig_frecTerm = px.line(
    df_frecTerm,
    x="Semana",
    y=["Paipote", "Terrapuerto", "Los Heroes"],
    markers=True
)


fig_frecTerm.update_traces(
    mode="lines+markers+text",
    marker = dict(size=12),
    texttemplate="%{y}",
    textfont=dict(size=12, color='black', family='Arial Black'),
    textposition="top center",
    line=dict(width=3)    
)


fig_frecTerm.update_layout(title="% Frecuencia por terminal", template='ygridoff')
fig_frecTerm.update_yaxes(range=[0, 100])

# ---------------------------
# Mostrar KPI
# ---------------------------
st.title("📊 % Frecuencia")
st.markdown("---")
col1, col2, col3, col4= st.columns(4)

with col1:

    st.plotly_chart(
    kpi_gauge("Total", list(promedios_tot.values())[0]),
    use_container_width=True
    )

with col2:

    st.plotly_chart(
    kpi_gauge("Paipote", list(promedio_paipo.values())[0]),
    use_container_width=True
    )

with col3:

    st.plotly_chart(
    kpi_gauge("Terrapuerto", list(promedio_terra.values())[0]),
    use_container_width=True
    )

with col4:

    st.plotly_chart(
    kpi_gauge("Los Heroes", list(promedio_lh.values())[0]),
    use_container_width=True
    )


st.markdown("---")
st.subheader("Evolución Semanal")




st.plotly_chart(fig)
st.markdown("---")
st.plotly_chart(fig_frecTerm)






