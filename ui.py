
import streamlit as st
from auth.auth import logout

def render_sidebar_user():
    if not st.session_state.get("authenticated"):
        return

    user = st.session_state.get("user", {})

    with st.sidebar:
        # st.markdown("---")

        st.markdown(
    f"""
    <div style="
        padding:10px;
        border-radius:8px;
        background-color:#f0f2f6;
        margin-bottom:10px;
    ">
        <b>👤 {user.get('nombre')}</b><br>
        <small>🛡️ {user.get('role').capitalize()}</small>
    </div>
    """,
    unsafe_allow_html=True
)

        if st.button("🚪 Cerrar sesión"):
            logout()
        st.markdown("---")
