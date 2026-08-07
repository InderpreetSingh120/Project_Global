import requests
from datetime import date
from dotenv import load_dotenv
import json
import os
import streamlit as st

BASE_URL = "https://api.nasa.gov/planetary/apod"
# Relative to this file's location, not a hardcoded machine path — works
# regardless of where the project folder lives or what OS it runs on.
SAVE_DIR = os.path.join(os.path.dirname(__file__), "cache", "nasa")

load_dotenv()

API_KEY = os.getenv("NASA_KEY") or st.secrets.get("NASA_KEY")


def download_apod():
    """Contacts the NASA APOD API and returns the raw JSON data as a dictionary.
    Returns None on any network/HTTP failure instead of raising — a slow or
    down NASA API should never be able to crash the whole Streamlit app."""
    params = {"api_key": API_KEY}

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"⚠️ NASA APOD request failed: {e}")
        return None


def save_apod(data: dict) -> None:
    """Saves a Python dictionary to a JSON file named after the data's date string.

    Expects data to contain a 'date' key (e.g., '2026-08-01').
    """
    # 1. Ensure the destination directory exists
    os.makedirs(SAVE_DIR, exist_ok=True)

    # 2. Extract date to use as the filename
    file_date = data.get("date")
    if not file_date:
        raise ValueError("Provided data dictionary is missing the required 'date' key.")

    file_path = os.path.join(SAVE_DIR, f"{file_date}.json")

    # 3. Write data to the JSON file
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"Successfully saved: {file_path}")


def load_apod(file_date: str):
    file_path = os.path.join(SAVE_DIR, f"{file_date}.json")

    if not os.path.exists(file_path):
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=86400)  # 24h. This is what stops get_apod() from re-firing
# on every unrelated rerun (typing in Weather, clicking a button anywhere, etc.)
# — Streamlit short-circuits here before the function body runs again at all.
def get_apod():
    today = date.today().isoformat()

    data = load_apod(today)

    if data:
        print("📂 Loaded APOD from cache")
        return data

    print("🌐 Downloading APOD from NASA")

    data = download_apod()
    if data:  # don't cache a failed/empty fetch as if it were a real result
        save_apod(data)

    return data  # None here is expected on failure — app.py already checks for it