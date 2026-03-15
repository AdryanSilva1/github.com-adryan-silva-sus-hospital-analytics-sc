import pandas as pd
import streamlit as st


@st.cache_data
def load_raw_data(path="data/raw/dados_sc.csv"):
    """Lê o arquivo CSV exportado do TabNet/DATASUS."""
    df = pd.read_csv(path, sep=";", encoding="latin-1", skiprows=3)
    return df