
import streamlit as st
from supabase import create_client
from security import hash_password, check_password
from auth.auth import logout
from datetime import datetime
from auth.auth import check_session_timeout
from ui import render_sidebar_user


check_session_timeout()
render_sidebar_user()

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)


def hide_pages_for_role():
    role = st.session_state.get("user", {}).get("role")

    if role != "admin":
        st.markdown(
            """
            <style>
            [data-testid="stSidebarNav"] li:has(a[href*="Admin"]) {
                display: none;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )




def crear_usuario(email, password, nombre, rol="usuario"):
    password_hash = hash_password(password)

    response = supabase.table("usuarios").insert({
        "email": email,
        "password_hash": password_hash,
        "nombre": nombre,
        "rol": rol,
        "activo": True
    }).execute()

    return response


def autenticar_usuario(email, password):
    response = supabase.table("usuarios") \
        .select("*") \
        .eq("email", email) \
        .eq("activo", True) \
        .execute()

    if not response.data:
        st.error("Usuario no existe o está inactivo")
        return

    user = response.data[0]

    if not check_password(password, user["password_hash"]):
        st.error("Contraseña incorrecta")
        return

    # 🔐 estado único y consistente
    st.session_state.authenticated = True
    st.session_state.user = {
        "id": user["id"],
        "email": user["email"],
        "nombre": user["nombre"],
        "role": user["rol"]
    }
    st.session_state.last_activity = datetime.now()

    supabase.table("usuarios") \
        .update({"ultimo_login": "now()"}) \
        .eq("id", user["id"]) \
        .execute()

    st.success("Login exitoso")
    st.rerun()



def login_form():
    st.title("🔐 Login")

    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")

    if st.button("Ingresar"):
        autenticar_usuario(email, password)


# -----------------------------
# FLUJO PRINCIPAL
# -----------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    login_form()
    st.stop()

hide_pages_for_role()

# if st.session_state.authenticated:
#     with st.sidebar:
#         st.markdown("---")
#         st.write(f"👤 {st.session_state.user['nombre']}")
#         st.write(f"🔐 Rol: {st.session_state.user['role']}")

#         if st.button("🚪 Cerrar sesión"):
#             logout()




st.set_page_config(
    page_title="Mi Aplicativo",
    page_icon="📊",
    layout="wide"
)

st.title("🏠 Página Principal")
st.write("Bienvenido al Dashboard de Nueva Copiapó")

st.markdown("---")


