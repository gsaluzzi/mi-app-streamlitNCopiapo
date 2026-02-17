import streamlit as st
from datetime import datetime, timedelta
from auth.auth import logout

def require_auth(allowed_roles: list[str]):
    """
    Middleware de seguridad por rol
    """

    if not st.session_state.get("authenticated"):
        st.error("🔒 Debes iniciar sesión")
        st.stop()

    user_role = st.session_state["user"]["role"]

    if user_role not in allowed_roles:
        st.error("⛔ No tienes permisos para acceder a esta página")
        st.stop()


PAGE_ACCESS = {
    "admin": [
        "Resumen Mes",
        "Expediciones",
        "Frecuencias",
        "Regularidad",
        "Puntualidad",
        "Remuneraciones y Horas Extras",
        "Gastos Administrativos",
        "Visor Pagos",
        "Resumen Dia"
        "Ingresos Kupos",
    ],
    "viewer": [
        "Expediciones",
        "Frecuencias",
        "Regularidad",
        "Puntualidad",     
        "Resumen Dia",
    ],
}

SESSION_TIMEOUT_MINUTES = 20

def check_session_timeout():
    if not st.session_state.get("authenticated"):
        return

    last_activity = st.session_state.get("last_activity")

    if not last_activity:
        return

    if datetime.now() - last_activity > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        st.warning("⏳ Tu sesión expiró por inactividad")
        logout()
    else:
        # Renovar actividad
        st.session_state.last_activity = datetime.now()




