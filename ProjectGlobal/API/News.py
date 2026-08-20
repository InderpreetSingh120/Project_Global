import requests
from datetime import date
from dotenv import load_dotenv
import json
import os
import streamlit as st

HEADLINES_URL = "https://newsapi.org/v2/top-headlines"
ALL_URL = "https://newsapi.org/v2/everything"
SAVE_DIR = os.path.join(os.path.dirname(__file__), "cache", "news")

load_dotenv()
API_KEY = os.getenv("NEWS_KEY") or st.secrets.get("NEWS_KEY")


# ─── Cache Helpers ────────────────────────────────────────

def download_news() -> dict:
    """Fetch fresh headlines from NewsAPI. Returns {} on failure."""
    print("🌐 Cache miss: Requesting fresh data from NewsAPI...")
    params = {"country": "us", "apiKey": API_KEY, "pageSize": 5}

    try:
        response = requests.get(HEADLINES_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"⚠️ NewsAPI headlines request failed: {e}")
        return {}


def save_news_cache(filename: str, data: dict) -> None:
    """Persist news payload to disk cache."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    file_path = os.path.join(SAVE_DIR, filename)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"💾 Successfully cached payload to: {file_path}")


def load_news_cache(filename: str) -> dict:
    """Load news payload from disk cache."""
    file_path = os.path.join(SAVE_DIR, filename)
    print(f"⚡ Cache hit: Reading local file from disk ({filename})...")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─── Public API ───────────────────────────────────────────

@st.cache_data(ttl=86400)  # 24h — daily headlines
def get_news() -> dict:
    """Return today's headlines, using disk cache when available."""
    today_str = date.today().isoformat()
    cache_filename = f"{today_str}.json"
    file_path = os.path.join(SAVE_DIR, cache_filename)

    if os.path.exists(file_path):
        return load_news_cache(cache_filename)

    fresh_data = download_news()
    if fresh_data:
        save_news_cache(cache_filename, fresh_data)
    return fresh_data


@st.cache_data(ttl=600)  # 10 min — search refreshes more often
def search_query(query: str) -> dict:
    """Search NewsAPI /everything endpoint. Returns {} on failure."""
    params = {"q": query, "sortBy": "publishedAt", "apiKey": API_KEY, "pageSize": 5}
    try:
        response = requests.get(ALL_URL, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"⚠️ NewsAPI search request failed: {e}")
        return {}