# API/GHI.py
"""
API.GHI – Global Happiness Index visualisation engine

Provides utilities to load, filter and render Plotly charts for the
World Happiness Report in a professional, theme‑consistent way.
"""
from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
# ────────────────────────────────────────────────────────────────────────
# THEME & CONSTANTS
# ────────────────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / "data" / "GlobalHappienessIndex.csv"
@st.cache_data
def load_ghi_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    if not DATA_PATH.exists():
        st.error(f"Data file missing at {DATA_PATH}")
        return pd.DataFrame()

    numeric_fields = [
        "Year", "Life Ladder", "Log GDP per capita",
        "Social support", "Healthy life expectancy at birth",
        "Freedom to make life choices", "Generosity",
        "Perceptions of corruption", "Positive affect", "Negative affect"
    ]

    for col in numeric_fields:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

