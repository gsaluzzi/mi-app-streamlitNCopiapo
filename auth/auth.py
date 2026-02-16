
import streamlit as st

def logout():
    st.session_state.authenticated = False
    st.session_state.user = None

    # Limpieza defensiva (opcional pero recomendado)
    for key in list(st.session_state.keys()):
        if key not in ["authenticated"]:
            del st.session_state[key]

    st.rerun()

