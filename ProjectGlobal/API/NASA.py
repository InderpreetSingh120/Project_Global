import requests
from datetime import date, timedelta
from dotenv import load_dotenv
import json
import os
import streamlit as st

BASE_URL = "https://api.nasa.gov/planetary/apod"
SAVE_DIR = os.path.join(os.path.dirname(__file__), "cache", "nasa")

load_dotenv()
API_KEY = os.getenv("NASA_KEY") or st.secrets.get("NASA_KEY")


# ─── Fetch & Fallback ────────────────────────────────────

def download_apod():
    """Fetch APOD from NASA. Falls back to yesterday on 404 (publish gap)."""
    params = {"api_key": API_KEY}

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        if response.status_code == 404:
            print("⚠️ Today's APOD isn't published yet — falling back to yesterday's")
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            response = requests.get(BASE_URL, params={**params, "date": yesterday}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"⚠️ NASA APOD request failed: {e}")
        return None


# ─── Disk Cache ──────────────────────────────────────────

def save_apod(data: dict) -> None:
    """Save APOD to disk, keyed by NASA's reported date (not today)."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    file_date = data.get("date")
    if not file_date:
        raise ValueError("Data missing required 'date' key.")
    file_path = os.path.join(SAVE_DIR, f"{file_date}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Successfully saved: {file_path}")


def load_apod(file_date: str):
    file_path = os.path.join(SAVE_DIR, f"{file_date}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─── Public API ──────────────────────────────────────────

@st.cache_data(ttl=3600)  # 1h — publish gap means today may not be ready
def get_apod():
    today = date.today().isoformat()
    data = load_apod(today)
    if data:
        print("📂 Loaded APOD from cache")
        return data
    print("🌐 Downloading APOD from NASA")
    data = download_apod()
    if data:
        save_apod(data)
    return data