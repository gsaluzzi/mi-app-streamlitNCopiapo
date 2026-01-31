import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from supabase import create_client
from plotly.subplots import make_subplots



def kpi_gauge(title, value, height=180):
    """
    Crea una KPI circular tipo donut.
    value debe estar entre 0 y 100.
    """
    if value >= 70:
        color = "green"
    elif value >= 40:
        color = "gold"
    else:
        color = "red"

    fig = go.Figure(go.Pie(
        values=[value, 100 - value],
        hole=0.7,
        sort=False,
        direction="clockwise",
        marker=dict(colors=[color, "#E0E0E0"]),
        textinfo="none"
    ))

    fig.update_layout(
        height=height,
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        annotations=[
            dict(
                text=f"<b>{value:.0f}%</b><br><span style='font-size:14px'>{title}</span>",
                x=0.5, y=0.5,
                font=dict(size=24),
                showarrow=False
            )
        ]
    )

    return fig



def semana_relativa(fecha, fecha_inicio):
    fecha = pd.to_datetime(fecha)
    fecha_inicio = pd.to_datetime(fecha_inicio)
    
    # diferencia en días
    dias = (fecha - fecha_inicio).dt.days
    
    # semana número (1, 2, 3, …)
    semana = dias // 7 + 1
    return semana


def asignarTerminal(servicio):
    if servicio in {'L1','L9','L11','L12', '[1248] L1', '[1256] L9', '[1258] L11',
                    '[1259] L12', '[1248] L1 I', '[1248] L1 R', '[1256] L9 I', '[1256] L9 R',
                    '[1258] L11 I', '[1258] L11 R', '[1259] L12 I', '[1259] L12 R'}:
        return "Paipote"
    elif servicio in {'L6','L8','L10', '[1253] L6', '[1255] L8', '[1257] L10', '[1253] L6 I', '[1253] L6 R',
                      '[1255] L8 I', '[1255] L8 R', '[1257] L10 I', '[1257] L10 R'}:
        return "Terrapuerto"
    else:
        return "Los Heroes"
    



def sparkline_unicode(values):
    bloques = "▁▂▃▄▅▆▇█"
    valores = pd.Series(values).astype(float)

    minimo = valores.min()
    maximo = valores.max()

    # Evitar división por cero cuando todos los valores son iguales
    if maximo - minimo == 0:
        return bloques[0] * len(valores)

    # Normalizar los valores entre 0 y 1
    normalizados = (valores - minimo) / (maximo - minimo)

    # Convertir a índice de bloques
    indices = (normalizados * (len(bloques) - 1)).astype(int)

    # Construir sparkline
    return "".join(bloques[i] for i in indices)

 

def sparkline(valores):
    # Convertir a lista de floats por si vienen como strings
    valores = pd.to_numeric(valores, errors='coerce')

    # Si todos son NaN, devolver vacío
    if valores.isna().all():
        return ""

    primero = valores.iloc[0]
    ultimo = valores.iloc[-1]

    # Flecha según aumento o caída
    if ultimo > primero:
        flecha = "🟢↑"
    elif ultimo < primero:
        flecha = "🔴↓"
    else:
        flecha = "➡️"

    # Sparkline simple con caracteres Unicode (▁▂▃▄▅▆▇█)
    chars = "▁▂▃▄▅▆▇█"
    minimo = valores.min()
    maximo = valores.max()

    rango = maximo - minimo if maximo != minimo else 1

    idx = ((valores - minimo) / rango * (len(chars) - 1)).astype(int)

    spark = "".join(chars[i] for i in idx)

    return f"{spark} {flecha}"



def estilo_negrita(col):
    return ['font-weight: bold'] * len(col)




def metric_coloreado(label, value, delta=None, color_texto="black", color_fondo="white", formato="raw"):
    """
    Muestra un metric personalizado en Streamlit con colores y formato numérico.

    Parámetros:
    - value: número
    - delta: número opcional (si es positivo verde ▲, si es negativo rojo ▼)
    - color_texto: color del valor principal
    - color_fondo: color del cuadro
    - formato: "raw", "numero", "moneda", "porcentaje"
    """

    # ---- FORMATO DEL VALUE ----
    if formato == "numero":
        value_str = f"{value:,.0f}".replace(",", ".")
    elif formato == "moneda":
        value_str = "$" + f"{value:,.0f}".replace(",", ".")
    elif formato == "porcentaje":
        value_str = f"{value}%"
    else:  # raw
        value_str = str(value)

    # ---- DELTA ----
    delta_str = ""

    if delta is not None:
        if delta > 0:
            delta_str = f"<span style='color:green; font-weight:bold;'>▲ {delta}</span>"
        elif delta < 0:
            delta_str = f"<span style='color:red; font-weight:bold;'>▼ {abs(delta)}</span>"
        else:
            delta_str = f"<span style='color:gray; font-weight:bold;'>● {delta}</span>"

    # ---- HTML FINAL ----
    html = f"""
    <div style="
        background-color:{color_fondo};
        padding:12px;
        border-radius:10px;
    ">
        <div style="font-size:16px; color:white; font-weight:bold; opacity:0.7;">{label}</div>
        <div style="font-size:24px; color:{color_texto}; font-weight:bold;">{value_str}</div>
        <div style="font-size:16px; margin-top:2px;">{delta_str}</div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)


def subheader_custom(texto, size=20, color="black"):
    st.markdown(
        f"<h2 style='font-size:{size}px; color:{color}; margin-bottom:0px;'>{texto}</h2>",
        unsafe_allow_html=True,
    )
    



supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

def fetch_all_from_supabase(table_name, batch_size=1000):
    all_rows = []
    start = 0

    while True:
        end = start + batch_size - 1

        response = (
            supabase
            .table(table_name)
            .select("*")
            .range(start, end)
            .execute()
        )

        data = response.data

        if not data:
            break

        all_rows.extend(data)
        start += batch_size

    return pd.DataFrame(all_rows)


def insert_batch(table, rows, batch_size=500):
    for i in range(0, len(rows), batch_size):
        chunk = rows[i:i + batch_size]
        supabase.table(table).insert(chunk).execute()



def barra_carga_por_tipo(df):
    """
    Muestra una barra horizontal con porcentaje de carga día vs noche.
    tipo_carga: 1 = día, 0 = noche
    """

    total = len(df)
    pct_dia = round((df["tipo_carga"] == 1).sum() / total * 100, 1)
    pct_noche = 100 - pct_dia

    fig = go.Figure()

    # Día
    fig.add_bar(
        x=[pct_dia],
        y=["Carga"],
        orientation="h",
        name="Día",
        marker_color="#FDB813",
        text=[f"{pct_dia}%"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=18, color="white")
    )

    # Noche
    fig.add_bar(
        x=[pct_noche],
        y=["Carga"],
        orientation="h",
        name="Noche",
        marker_color="#2C3E50",
        text=[f"{pct_noche}%"],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(size=18, color="white")
    )

    fig.update_layout(
        barmode="stack",
        showlegend=True,
        height=120,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False)
    )

    return fig


def dias_restantes_mes_detalle(df, columna_fecha="Fecha"):
    """
    Retorna:
    - días hábiles restantes
    - sábados restantes
    - domingos restantes
    según la fecha máxima del dataframe
    """

    # Convertir a datetime
    fechas = pd.to_datetime(df[columna_fecha], dayfirst=True)
    fecha_max = fechas.max()

    # Último día del mes
    fin_mes = fecha_max + pd.offsets.MonthEnd(0)

    # Rango de fechas desde el día siguiente
    rango = pd.date_range(
        start=fecha_max + pd.Timedelta(days=1),
        end=fin_mes,
        freq="D"
    )

    # Contadores
    dias_habiles = sum(rango.weekday < 5)   # lunes(0) a viernes(4)
    sabados = sum(rango.weekday == 5)
    domingos = sum(rango.weekday == 6)

    return dias_habiles, sabados, domingos


def promedio_ingresos_por_tipo_dia(
    df,
    col_fecha="fecha",
    col_ingresos="ingresos"
):
    """
    Retorna:
    - promedio ingresos días hábiles
    - promedio ingresos sábados
    - promedio ingresos domingos
    """

    df = df.copy()

    # Asegurar datetime
    df[col_fecha] = pd.to_datetime(df[col_fecha], dayfirst=True, errors="coerce")

    # Eliminar filas inválidas
    df = df.dropna(subset=[col_fecha, col_ingresos])

    # Día de la semana (0=lunes ... 6=domingo)
    df["weekday"] = df[col_fecha].dt.weekday

    promedio_habil = df.loc[df["weekday"] < 5, col_ingresos].mean()
    promedio_sabado = df.loc[df["weekday"] == 5, col_ingresos].mean()
    promedio_domingo = df.loc[df["weekday"] == 6, col_ingresos].mean()

    return promedio_habil, promedio_sabado, promedio_domingo





def grafico_carga_3_meses(
    df,
    df_cge,
    color_dia="#FDB813",
    color_noche="#2C3E50",
    size_texto_pct=18
):
    # -----------------------------
    # Preparación de fechas
    # -----------------------------
    df = df.copy()
    df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True)
    df["mes"] = df["Fecha"].dt.to_period("M")

    mes_actual = df["mes"].max()
    meses_objetivo = sorted(df[df["mes"] < mes_actual]["mes"].unique())[-3:]

    df = df[df["mes"].isin(meses_objetivo)]

    # Etiquetas mes (ej: Enero 2026)
    etiquetas_mes = [
        m.to_timestamp().strftime("%B %Y").capitalize()
        for m in meses_objetivo
    ]

    # -----------------------------
    # Cálculo porcentajes día/noche
    # -----------------------------
    resumen = (
        df.groupby(["mes", "tipo_carga"])
        .size()
        .unstack(fill_value=0)
    )

    total = resumen.sum(axis=1)
    pct_dia = (resumen.get(1, 0) / total * 100).round(1)
    pct_noche = (resumen.get(0, 0) / total * 100).round(1)

    # -----------------------------
    # Energía y costo por mes
    # -----------------------------
    energia = (
        df.groupby("mes")["Energía"]
        .sum()
        .round(0)
        .astype(int)
        .tolist()
    )

    costo = (
        df_cge.groupby("mes")["Costo"]
        .sum()
        .tolist()
    )

    costo_fmt = [f"${v:,.0f}".replace(",", ".") for v in costo]
    energia_fmt = [f"{v/1000:,.0f} MWh".replace(",", ".") for v in energia]
    
    # -----------------------------
    # Figure con gráfico + tabla
    # -----------------------------
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.15,
        row_heights=[0.7, 0.3],
        specs=[[{"type": "bar"}], [{"type": "table"}]]
    )

    # Día
    fig.add_bar(
        x=etiquetas_mes,
        y=pct_dia,
        name="Día",
        marker_color=color_dia,
        text=[f"{v}%" for v in pct_dia],
        textposition="inside",
        textfont=dict(size=size_texto_pct),
        row=1,
        col=1
    )

    # Noche
    fig.add_bar(
        x=etiquetas_mes,
        y=pct_noche,
        name="Noche",
        marker_color=color_noche,
        text=[f"{v}%" for v in pct_noche],
        textposition="inside",
        textfont=dict(size=size_texto_pct),
        row=1,
        col=1
    )

    # -----------------------------
    # Tabla 2 filas x 3 columnas
    # -----------------------------
    fig.add_table(
        row=2,
        col=1,
        header=dict(values=["", "", ""], height=1),
        cells=dict(
            values=[
                [energia_fmt[0], costo_fmt[2]],
                [energia_fmt[1], costo_fmt[1]],
                [energia_fmt[2], costo_fmt[0]]
            ],
            align="center",
            font=dict(size=13),
            line_color="white"
        )
    )

    fig.update_layout(
        barmode="stack",
        showlegend=True,
        height=260,
        margin=dict(t=40, b=20)
    )

    return fig

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







