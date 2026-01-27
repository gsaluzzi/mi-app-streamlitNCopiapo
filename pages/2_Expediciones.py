import streamlit as st
import pandas as pd
from componentes import kpi_gauge, asignarTerminal, semana_relativa, sparkline, metric_coloreado, fetch_all_from_supabase
import plotly.graph_objects as go




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

fecha_inicio, fecha_fin = st.sidebar.date_input(
    "Rango de fechas",
    value=[df["Fecha"].min(), df["Fecha"].max()]
)

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


st.markdown("---")
st.subheader("Evolución Semanal por línea")
st.dataframe(tabla_txn2, height=480)





