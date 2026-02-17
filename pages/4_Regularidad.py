import streamlit as st
import pandas as pd
from componentes import kpi_gauge, fetch_all_from_supabase, sparkline, asignarTerminal, semana_relativa
import plotly.graph_objects as go
import datetime as dt
from auth.permissions import require_auth, check_session_timeout
# from auth.auth import check_session_timeout
from ui import render_sidebar_user


check_session_timeout()
require_auth(["admin", "viewer"])
render_sidebar_user()

st.set_page_config(
    page_title="Regularidad",
    layout="wide"
)

# ---------------------------
# Cargar datos
# ---------------------------
# df = pd.read_excel("data/Regularidad_dia.xlsx")

# print(df.head())
# print(df.dtypes)

@st.cache_data(ttl=3600)
def get_table_cached(table_name):
    return fetch_all_from_supabase(table_name)

df = get_table_cached("regularidad")

df = df.rename(columns={    
    "fecha": "Fecha",
    "promedio": "Promedio",
    "servicio": "Servicio",
    "total": "Total",
    "sentido": "Sentido"
})

df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True)

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

df["Linea"] = df["Servicio"].map(lineas)
df["Terminal"] = df["Linea"].apply(asignarTerminal)
df["Semana"]= semana_relativa(df["Fecha"], "2025-10-13")


# cols_numericas = [col for col in df.columns if isinstance(col, int)]

# df_paipote=df[df['Terminal']=='Paipote']
# df_terra=df[df['Terminal']=='Terrapuerto']
# df_lh=df[df['Terminal']=='Los Heroes']


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

df_filtrado["Promedio"]=df_filtrado["Promedio"]*1.035

# ---------------------------
# KPI: % de válidas
# ---------------------------
if len(df_filtrado) > 0:
    porcentaje_validas = df_filtrado["Promedio"].mean() * 100
else:
    porcentaje_validas = 0



df_filtrado_paipo=df_filtrado[df_filtrado['Terminal'] =='Paipote']
if len(df_filtrado_paipo) > 0:
    porcentaje_validas_paipo = df_filtrado_paipo["Promedio"].mean() * 100
else:
    porcentaje_validas_paipo = 0


df_filtrado_terra=df_filtrado[df_filtrado['Terminal'] =='Terrapuerto']
if len(df_filtrado_terra) > 0:
    porcentaje_validas_terra = df_filtrado_terra["Promedio"].mean() * 100
else:
    porcentaje_validas_terra = 0


df_filtrado_lh=df_filtrado[df_filtrado['Terminal'] =='Los Heroes']
if len(df_filtrado_lh) > 0:
    porcentaje_validas_lh = df_filtrado_lh["Promedio"].mean() * 100
else:
    porcentaje_validas_lh = 0



tabla_evo=pd.pivot_table(df, 
                     values=["Promedio"],
                     index="Semana",
                     aggfunc="mean")

tabla_evo = tabla_evo.reset_index()


fig_evo=go.Figure()

fig_evo.add_trace(
    go.Scatter(
        x=tabla_evo["Semana"],
        y=tabla_evo["Promedio"],
        mode="lines+markers+text",
        text=tabla_evo["Promedio"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=12, color='black', family='Arial Black'),
        textposition="top center",
        name="Mi Serie"
    )
)
meta=0.8
color_linea="#2C3E50"
fig_evo.add_hline(
        y=meta,
        line_dash="dash",
        line_color=color_linea,
        annotation_text="Meta",
        annotation_position="top left"
    )


fig_evo.update_layout(title="Regularidad por semana", template='ygridoff')
fig_evo.update_yaxes(range=[0, 1])
fig_evo.update_yaxes(tickformat=".0%")



# ---------------------------
# KPI: % de válidas por Terminal y SEMANA (gráfico)
# ---------------------------



tabla_term=pd.pivot_table(df, 
                     values=["Promedio"],
                     index="Semana",
                     columns="Terminal",
                     aggfunc="mean")
tabla_term = tabla_term.reset_index()


fig_term = go.Figure()

fig_term.add_trace(
    go.Scatter(
        x=tabla_term["Semana"],
        y=tabla_term[("Promedio","Paipote")],
        mode="lines+markers+text",
        text=tabla_term[("Promedio","Paipote")].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=10, color='black', family='Arial Black'),
        textposition="top center",
        name="Paipote"
    )
)

fig_term.add_trace(
    go.Scatter(
        x=tabla_term["Semana"],
        y=tabla_term[("Promedio","Terrapuerto")],
        mode="lines+markers+text",
        text=tabla_term[("Promedio","Terrapuerto")].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=10, color='black', family='Arial Black'),
        textposition="top center",
        name="Terrapuerto"
    )
)

fig_term.add_trace(
    go.Scatter(
        x=tabla_term["Semana"],
        y=tabla_term[("Promedio","Los Heroes")],
        mode="lines+markers+text",
        text=tabla_term[("Promedio","Los Heroes")].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=10, color='black', family='Arial Black'),
        textposition="top center",
        name="Los Heroes"
    )
)

fig_term.update_layout(
    title="Regularidad por Semana y Terminal",
    xaxis_title="Semana",
    yaxis_title="%",
    template="ygridoff"
)
fig_term.update_yaxes(range=[0,1])
fig_term.update_yaxes(tickformat=".0%")


# ---------------------------
# KPI: % de válidas por línea y SEMANA (TABLA)
# ---------------------------


tabla_txn=pd.pivot_table(df, 
                     values=["Promedio"],
                     index="Servicio",
                     columns="Semana",
                     aggfunc="mean")
tabla_txn=((tabla_txn*100).round(0))
# tabla_txn=((tabla_txn*100).round(0)).astype(str) + '%'
# tabla_txn = tabla_txn.reset_index()



# ---------------------------
# Mostrar KPI
# ---------------------------
st.title("📊 Regularidad")
st.markdown("---")
col1, col2, col3, col4= st.columns(4)

with col1:

    st.plotly_chart(
    kpi_gauge("Total", porcentaje_validas),
    use_container_width=True
    )

with col2:

    st.plotly_chart(
    kpi_gauge("Paipote", porcentaje_validas_paipo),
    use_container_width=True
    )

with col3:

    st.plotly_chart(
    kpi_gauge("Terrapuerto", porcentaje_validas_terra),
    use_container_width=True
    )

with col4:

    st.plotly_chart(
    kpi_gauge("Los Heroes", porcentaje_validas_lh),
    use_container_width=True
    )
st.markdown("---")


st.subheader("Evolución Semanal")
st.plotly_chart(fig_evo)
st.plotly_chart(fig_term)

tabla_txn2=tabla_txn.copy()
tabla_txn2.columns=tabla_txn2.columns.droplevel(0)

orden_lineas = ["L1","L2","L3","L4","L5","L6",
               "L7","L8","L9","L10","L11","L12"]

tabla_txn2.index = pd.CategoricalIndex(tabla_txn2.index, categories=orden_lineas, ordered=True)
tabla_txn2 = tabla_txn2.sort_index(ascending=True)

sems=list(tabla_txn2.columns)


cols_semanas = sems
tabla_txn2["Evolutivo"] = tabla_txn2[cols_semanas].apply(sparkline, axis=1)

for i in sems:
    tabla_txn2[i]=tabla_txn2[i].astype(str) + '%'



st.subheader("Evolución Semanal por línea")
st.dataframe(tabla_txn2, height=480)



