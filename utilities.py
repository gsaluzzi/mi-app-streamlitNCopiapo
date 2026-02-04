import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials


@st.cache_data(ttl=600)
def get_gsheet_df(sheet_id: str, worksheet_name: str) -> pd.DataFrame:
    """
    Lee una Google Sheet y retorna un DataFrame cacheado.
    """

    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=scopes
        )

        client = gspread.authorize(creds)
        worksheet = client.open_by_key(sheet_id).worksheet(worksheet_name)
        data = worksheet.get_all_records()

        return pd.DataFrame(data)

    except Exception as e:
        st.error(f"❌ Error leyendo Google Sheet: {e}")
        return pd.DataFrame()





