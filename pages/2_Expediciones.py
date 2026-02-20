import streamlit as st
import pandas as pd
from componentes import kpi_gauge, asignarTerminal, semana_relativa, sparkline, metric_coloreado, fetch_all_from_supabase
import plotly.graph_objects as go
import datetime as dt
from auth.permissions import require_auth, check_session_timeout
# from auth.auth import check_session_timeout
from ui import render_sidebar_user



check_session_timeout()
require_auth(["admin", "viewer"])
render_sidebar_user()

st.set_page_config(
    page_title="Expediciones Válidas",
    layout="wide"
)

# ---------------------------
# Cargar datos
# ---------------------------
# df = pd.read_excel("data/Expediciones_Maestro.xlsx")

@st.cache_data(ttl=3600)
def get_table_cached(table_name):
    return fetch_all_from_supabase(table_name)

df = get_table_cached("expediciones")


df = df.rename(columns={
    "fecha": "Fecha",
    "estado": "Estado",
    "terminal": "Terminal",
    "servicio": "Servicio"
})


df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True)
df["Estado"] = df["Estado"].str.lower().str.strip()
df["Terminal"] = df["Servicio"].apply(asignarTerminal)
df["Semana"]= semana_relativa(df["Fecha"], "2025-10-13")
df["es_valida"]= (df["Estado"].str.lower() == "valida").astype(int)

df = df[df['causa']!='Cortadas por inverso']

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
    porcentaje_validas = df_filtrado["Estado"].eq("valida").mean() * 100
else:
    porcentaje_validas = 0



df_filtrado_paipo=df_filtrado[df_filtrado['Terminal'] =='Paipote']
if len(df_filtrado_paipo) > 0:
    porcentaje_validas_paipo = df_filtrado_paipo["Estado"].eq("valida").mean() * 100
else:
    porcentaje_validas_paipo = 0


df_filtrado_terra=df_filtrado[df_filtrado['Terminal'] =='Terrapuerto']
if len(df_filtrado_terra) > 0:
    porcentaje_validas_terra = df_filtrado_terra["Estado"].eq("valida").mean() * 100
else:
    porcentaje_validas_terra = 0


df_filtrado_lh=df_filtrado[df_filtrado['Terminal'] =='Los Heroes']
if len(df_filtrado_lh) > 0:
    porcentaje_validas_lh = df_filtrado_lh["Estado"].eq("valida").mean() * 100
else:
    porcentaje_validas_lh = 0




# ---------------------------
# KPI: % de válidas SEMANA (TABLA)
# ---------------------------



tabla_evo=pd.pivot_table(df, 
                     values=["es_valida"],
                     index="Semana",
                     aggfunc="mean")

tabla_evo = tabla_evo.reset_index()


fig_evo=go.Figure()

fig_evo.add_trace(
    go.Scatter(
        x=tabla_evo["Semana"],
        y=tabla_evo["es_valida"],
        mode="lines+markers+text",
        text=tabla_evo["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=18, color='black', family='Arial Black'),
        textposition="top center",
        name="Mi Serie"
    )
)
meta=0.95
color_linea="#2C3E50"
fig_evo.add_hline(
        y=meta,
        line_dash="dash",
        line_color=color_linea,
        annotation_text="Meta",
        annotation_position="top left"
    )



fig_evo.update_layout(title="% Expediciones válidas por semana", template='ygridoff')
fig_evo.update_yaxes(range=[0.7,1])
fig_evo.update_yaxes(tickformat=".0%")



# ---------------------------
# KPI: % de válidas por Terminal y SEMANA (gráfico)
# ---------------------------



tabla_term=pd.pivot_table(df, 
                     values=["es_valida"],
                     index="Semana",
                     columns="Terminal",
                     aggfunc="mean")
tabla_term = tabla_term.reset_index()


fig_term = go.Figure()

fig_term.add_trace(
    go.Scatter(
        x=tabla_term["Semana"],
        y=tabla_term[("es_valida","Paipote")],
        mode="lines+markers+text",
        text=tabla_term[("es_valida","Paipote")].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=16, color='black', family='Arial Black'),
        textposition="top center",
        name="Paipote"
    )
)

fig_term.add_trace(
    go.Scatter(
        x=tabla_term["Semana"],
        y=tabla_term[("es_valida","Terrapuerto")],
        mode="lines+markers+text",
        text=tabla_term[("es_valida","Terrapuerto")].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=16, color='black', family='Arial Black'),
        textposition="top center",
        name="Terrapuerto"
    )
)

fig_term.add_trace(
    go.Scatter(
        x=tabla_term["Semana"],
        y=tabla_term[("es_valida","Los Heroes")],
        mode="lines+markers+text",
        text=tabla_term[("es_valida","Los Heroes")].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=16, color='black', family='Arial Black'),
        textposition="top center",
        name="Los Heroes"
    )
)

fig_term.update_layout(
    title="Porcentaje de Válidas por Semana y Terminal",
    xaxis_title="Semana",
    yaxis_title="%",
    template="ygridoff"
)
fig_term.update_yaxes(range=[0.6,1.1])
fig_term.update_yaxes(tickformat=".0%")


# ---------------------------
# KPI: % de válidas por línea y SEMANA (TABLA)
# ---------------------------


tabla_txn=pd.pivot_table(df, 
                     values=["es_valida"],
                     index="Servicio",
                     columns="Semana",
                     aggfunc="mean")
tabla_txn=((tabla_txn*100).round(0))
# tabla_txn=((tabla_txn*100).round(0)).astype(str) + '%'
# tabla_txn = tabla_txn.reset_index()






# ---------------------------
# Mostrar KPI
# ---------------------------
st.title("📊 % Expediciones Válidas")
st.markdown("---")



colA1, colB1, colC1 = st.columns(3)

with colA1:
    metric_coloreado("Expediciones Totales", df_filtrado["Estado"].count(), delta=None, color_texto='white', color_fondo="#697dd8", formato='numero' )

with colB1:
    metric_coloreado("Expediciones Válidas", df_filtrado["es_valida"].sum(), delta=None, color_texto='white', color_fondo="#73e89e", formato='numero' )

with colC1:
    metric_coloreado("Expediciones Inválidas", df_filtrado["Estado"].count()-df_filtrado["es_valida"].sum() , delta=None, color_texto='white', color_fondo="#f06868", formato='numero' )

st.markdown("---")
st.subheader("Global y por Terminal")
col1, col2, col3, col4= st.columns(4)

with col1:

    st.plotly_chart(
    kpi_gauge("EV Total", porcentaje_validas),
    use_container_width=True
    )

with col2:

    st.plotly_chart(
    kpi_gauge("EV Paipote", porcentaje_validas_paipo),
    use_container_width=True
    )

with col3:

    st.plotly_chart(
    kpi_gauge("EV Terrapuerto", porcentaje_validas_terra),
    use_container_width=True
    )

with col4:

    st.plotly_chart(
    kpi_gauge("EV Los Heroes", porcentaje_validas_lh),
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

#---------------------------------------------------------------------
#------------------L1-------------------------------------------------

tabla_L1=pd.pivot_table(df[df["Servicio"]=="L1"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L1 = tabla_L1.reset_index()

#-----------------------------------------------------------------------
#------------------L2-------------------------------------------------

tabla_L2=pd.pivot_table(df[df["Servicio"]=="L2"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L2 = tabla_L2.reset_index()

#-----------------------------------------------------------------------
#------------------L3-------------------------------------------------

tabla_L3=pd.pivot_table(df[df["Servicio"]=="L3"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L3 = tabla_L3.reset_index()

#-----------------------------------------------------------------------
#------------------L4-------------------------------------------------

tabla_L4=pd.pivot_table(df[df["Servicio"]=="L4"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L4 = tabla_L4.reset_index()

#-----------------------------------------------------------------------
#------------------L5-------------------------------------------------

tabla_L5=pd.pivot_table(df[df["Servicio"]=="L5"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L5 = tabla_L5.reset_index()

#-----------------------------------------------------------------------
#------------------L6-------------------------------------------------

tabla_L6=pd.pivot_table(df[df["Servicio"]=="L6"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L6 = tabla_L6.reset_index()

#-----------------------------------------------------------------------
#------------------L7-------------------------------------------------

tabla_L7=pd.pivot_table(df[df["Servicio"]=="L7"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L7 = tabla_L7.reset_index()

#-----------------------------------------------------------------------
#------------------L8-------------------------------------------------

tabla_L8=pd.pivot_table(df[df["Servicio"]=="L8"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L8 = tabla_L8.reset_index()

#-----------------------------------------------------------------------
#------------------L9-------------------------------------------------

tabla_L9=pd.pivot_table(df[df["Servicio"]=="L9"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L9 = tabla_L9.reset_index()

#-----------------------------------------------------------------------
#------------------L10-------------------------------------------------

tabla_L10=pd.pivot_table(df[df["Servicio"]=="L10"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L10 = tabla_L10.reset_index()

#-----------------------------------------------------------------------
#------------------L11-------------------------------------------------

tabla_L11=pd.pivot_table(df[df["Servicio"]=="L11"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L11 = tabla_L11.reset_index()

#-----------------------------------------------------------------------
#------------------L12-------------------------------------------------

tabla_L12=pd.pivot_table(df[df["Servicio"]=="L12"], 
                     values=["es_valida"],
                     index="Semana",
                    #  columns="Terminal",
                     aggfunc="mean")
tabla_L12 = tabla_L12.reset_index()

#-----------------------------------------------------------------------





fig_paipo = go.Figure()

fig_paipo.add_trace(
    go.Scatter(
        x=tabla_L1["Semana"],
        y=tabla_L1["es_valida"],
        mode="lines+markers+text",
        text=tabla_L1["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L1"
    )
)
fig_paipo.add_trace(
    go.Scatter(
        x=tabla_L9["Semana"],
        y=tabla_L9["es_valida"],
        mode="lines+markers+text",
        text=tabla_L9["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L9"
    )
)
fig_paipo.add_trace(
    go.Scatter(
        x=tabla_L11["Semana"],
        y=tabla_L11["es_valida"],
        mode="lines+markers+text",
        text=tabla_L11["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L11"
    )
)
fig_paipo.add_trace(
    go.Scatter(
        x=tabla_L12["Semana"],
        y=tabla_L12["es_valida"],
        mode="lines+markers+text",
        text=tabla_L12["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L12"
    )
)

fig_paipo.update_layout(
    title="Exp válidas por líneas Paipote",
    xaxis_title="Semana",
    yaxis_title="%",
    template="ygridoff"
)
fig_paipo.update_yaxes(range=[0.3,1.1])
fig_paipo.update_yaxes(tickformat=".0%")

#--------------------------------------------------------------------------
fig_terra = go.Figure()

fig_terra.add_trace(
    go.Scatter(
        x=tabla_L6["Semana"],
        y=tabla_L6["es_valida"],
        mode="lines+markers+text",
        text=tabla_L6["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L6"
    )
)
fig_terra.add_trace(
    go.Scatter(
        x=tabla_L8["Semana"],
        y=tabla_L8["es_valida"],
        mode="lines+markers+text",
        text=tabla_L8["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L8"
    )
)
fig_terra.add_trace(
    go.Scatter(
        x=tabla_L10["Semana"],
        y=tabla_L10["es_valida"],
        mode="lines+markers+text",
        text=tabla_L10["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L10"
    )
)

fig_terra.update_layout(
    title="Exp válidas por líneas Terrapuerto",
    xaxis_title="Semana",
    yaxis_title="%",
    template="ygridoff"
)
fig_terra.update_yaxes(range=[0.3,1.1])
fig_terra.update_yaxes(tickformat=".0%")

#--------------------------------------------------------------------------------
fig_lh = go.Figure()

fig_lh.add_trace(
    go.Scatter(
        x=tabla_L2["Semana"],
        y=tabla_L2["es_valida"],
        mode="lines+markers+text",
        text=tabla_L2["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L2"
    )
)
fig_lh.add_trace(
    go.Scatter(
        x=tabla_L3["Semana"],
        y=tabla_L3["es_valida"],
        mode="lines+markers+text",
        text=tabla_L3["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L3"
    )
)
fig_lh.add_trace(
    go.Scatter(
        x=tabla_L4["Semana"],
        y=tabla_L4["es_valida"],
        mode="lines+markers+text",
        text=tabla_L4["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L4"
    )
)
fig_lh.add_trace(
    go.Scatter(
        x=tabla_L5["Semana"],
        y=tabla_L5["es_valida"],
        mode="lines+markers+text",
        text=tabla_L5["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L5"
    )
)
fig_lh.add_trace(
    go.Scatter(
        x=tabla_L7["Semana"],
        y=tabla_L7["es_valida"],
        mode="lines+markers+text",
        text=tabla_L7["es_valida"].apply(lambda x: f"{x:.0%}"),
        textfont=dict(size=14, color='black', family='Arial Black'),
        textposition="top center",
        name="L7"
    )
)
fig_lh.update_layout(
    title="Exp válidas por líneas Los Heroes",
    xaxis_title="Semana",
    yaxis_title="%",
    template="ygridoff"
)
fig_lh.update_yaxes(range=[0.3,1.1])
fig_lh.update_yaxes(tickformat=".0%")



st.markdown("---")
st.plotly_chart(fig_paipo)
st.markdown("---")
st.plotly_chart(fig_terra)
st.markdown("---")
st.plotly_chart(fig_lh)



