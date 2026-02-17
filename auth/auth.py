
import streamlit as st
# from datetime import datetime, timedelta

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None

    # Limpieza defensiva (opcional pero recomendado)
    for key in list(st.session_state.keys()):
        if key not in ["authenticated"]:
            del st.session_state[key]

    st.rerun()

# SESSION_TIMEOUT_MINUTES = 20

# def check_session_timeout():
#     if not st.session_state.get("authenticated"):
#         return

#     last_activity = st.session_state.get("last_activity")

#     if not last_activity:
#         return

#     if datetime.now() - last_activity > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
#         st.warning("⏳ Tu sesión expiró por inactividad")
#         logout()
#     else:
#         # Renovar actividad
#         st.session_state.last_activity = datetime.now()