
# import bcrypt
import streamlit as st
from supabase import create_client
from componentes import fetch_all_from_supabase


# password = "1234"
# password_hash = bcrypt.hashpw(
#     password.encode(),
#     bcrypt.gensalt()
# ).decode()

# print(password_hash)

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

response = supabase.table("usuarios")

df=fetch_all_from_supabase("usuarios")


print(df)
print(supabase)


