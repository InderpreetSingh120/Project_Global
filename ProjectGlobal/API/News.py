import requests
from datetime import date
from dotenv import load_dotenv
import json
import os
import streamlit as st

HEADLINES_URL = "https://newsapi.org/v2/top-headlines"
ALL_URL = "https://newsapi.org/v2/everything"
# Relative to this file's location, not a hardcoded machine path.
SAVE_DIR = os.path.join(os.path.dirname(__file__), "cache", "news")

load_dotenv()
API_KEY = os.getenv("NEWS_KEY")


def download_news() -> dict:
    """Contacts NewsAPI and returns the raw JSON headlines.
    Returns {} on any network/HTTP failure instead of raising."""
    print("🌐 Cache miss: Requesting fresh data from NewsAPI...")
    params = {
        "country": "us",
        "apiKey": API_KEY,
        "pageSize": 5
    }

    try:
        response = requests.get(HEADLINES_URL, params=params, timeout=10)
        response.raise_for_status()
        print(response.status_code)
        print(response.text)
        return response.json()
    except requests.RequestException as e:
        print(f"⚠️ NewsAPI headlines request failed: {e}")
        return {}


def save_news_cache(filename: str, data: dict) -> None:
    """Saves the news dictionary payload to your specific local path."""
    os.makedirs(SAVE_DIR, exist_ok=True)
    file_path = os.path.join(SAVE_DIR, filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print(f"💾 Successfully cached payload to: {file_path}")


def load_news_cache(filename: str) -> dict:
    """Reads and returns the local cached news JSON file."""
    file_path = os.path.join(SAVE_DIR, filename)
    print(f"⚡ Cache hit: Reading local file from disk ({filename})...")

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data(ttl=86400)  # 24h. Stops get_news() from re-firing on every
# unrelated rerun — same fix as NASA.py, same underlying bug.
def get_news() -> dict:
    """Orchestrates the caching pipeline using today's date as the reference key."""
    today_str = date.today().isoformat()
    cache_filename = f"{today_str}.json"
    file_path = os.path.join(SAVE_DIR, cache_filename)

    if os.path.exists(file_path):
        return load_news_cache(cache_filename)

    fresh_data = download_news()
    if fresh_data:  # don't cache a failed/empty fetch as if it were real data
        save_news_cache(cache_filename, fresh_data)
    return fresh_data


@st.cache_data(ttl=600)  # searches can refresh more often than daily headlines
def search_query(query: str) -> dict:
    """Searches for news articles based on a user-provided query.
    Returns {} on failure so callers can safely do result.get("articles", [])."""
    params = {
        "q": query,
        "sortBy": "publishedAt",
        "apiKey": API_KEY,
        "pageSize": 5
    }
    try:
        response = requests.get(ALL_URL, params=params, timeout=10)
        response.raise_for_status()
        print(response.status_code)
        print(response.text)
        return response.json()
    except requests.RequestException as e:
        print(f"⚠️ NewsAPI search request failed: {e}")
        return {}