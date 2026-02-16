import streamlit as st

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


