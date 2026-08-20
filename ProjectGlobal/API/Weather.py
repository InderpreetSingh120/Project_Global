import os
import json
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("WEATHER_KEY") or st.secrets.get("WEATHER_KEY")
print("OpenWeather API key loaded." if API_KEY else "⚠️ WEATHER_KEY not found in environment.")

GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
CURRENT_WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
AQI_URL = "https://api.openweathermap.org/data/2.5/air_pollution"
AQI_FORECAST_URL = "https://api.openweathermap.org/data/2.5/air_pollution/forecast"
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache", "weather")


def _safe_filename(text: str) -> str:
    return text.strip().lower().replace(" ", "_").replace(",", "")


# ─── Geocoding (disk cache, permanent) ──────────────────

def geocode_location(query: str, limit: int = 5) -> list:
    """Resolve place name to coordinates. Cached to disk indefinitely."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CACHE_DIR, f"geo_{_safe_filename(query)}.json")

    if os.path.exists(cache_file):
        print(f"⚡ Cache hit: reading local geocoding data for '{query}'...")
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"🌐 Cache miss: requesting geocoding data for '{query}' from OpenWeather...")
    try:
        response = requests.get(GEOCODE_URL, params={"q": query, "limit": limit, "appid": API_KEY}, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as e:
        print(f"Geocoding request failed: {e}")
        return []

    if data:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"💾 Cached geocoding payload to: {cache_file}")

    return data


# ─── Live Weather (TTL cache) ──────────────────────────

@st.cache_data(ttl=600)   # 10 min
def get_current_weather(lat: float, lon: float, units: str = "metric") -> dict:
    try:
        response = requests.get(CURRENT_WEATHER_URL, params={"lat": lat, "lon": lon, "appid": API_KEY, "units": units}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Current weather request failed: {e}")
        return {}


@st.cache_data(ttl=1800)  # 30 min — 3-hour forecast buckets
def get_forecast(lat: float, lon: float, units: str = "metric") -> dict:
    try:
        response = requests.get(FORECAST_URL, params={"lat": lat, "lon": lon, "appid": API_KEY, "units": units}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Forecast request failed: {e}")
        return {}


@st.cache_data(ttl=600)   # 10 min
def get_air_quality(lat: float, lon: float) -> dict:
    try:
        response = requests.get(AQI_URL, params={"lat": lat, "lon": lon, "appid": API_KEY}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Air quality request failed: {e}")
        return {}


@st.cache_data(ttl=1800)  # 30 min
def get_air_quality_forecast(lat: float, lon: float) -> dict:
    try:
        response = requests.get(AQI_FORECAST_URL, params={"lat": lat, "lon": lon, "appid": API_KEY}, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Air quality forecast request failed: {e}")
        return {}


# ─── Visualization ──────────────────────────────────────

def create_forecast_chart(forecast: dict, hours: int = 48):
    """Temperature trend line chart for next N hours."""
    entries = forecast.get("list", [])[: hours // 3]
    if not entries:
        return None

    df = pd.DataFrame({
        "time": [e["dt_txt"] for e in entries],
        "Temperature": [e["main"]["temp"] for e in entries],
        "Feels Like": [e["main"]["feels_like"] for e in entries],
    })

    fig = px.line(df, x="time", y=["Temperature", "Feels Like"],
                  title=f"Temperature trend — next {hours} hours",
                  labels={"value": "°C", "time": "", "variable": ""},
                  markers=True)
    return fig


def create_aqi_forecast_chart(forecast: dict, hours: int = 48):
    """AQI + pollutants dual-axis chart for next N hours."""
    entries = forecast.get("list", [])[: hours // 3]
    if not entries:
        return None

    times = pd.to_datetime([e["dt"] for e in entries], unit="s")
    aqi_values = [e["main"]["aqi"] for e in entries]
    pm25 = [e["components"].get("pm2_5", 0) for e in entries]
    pm10 = [e["components"].get("pm10", 0) for e in entries]
    o3 = [e["components"].get("o3", 0) for e in entries]
    no2 = [e["components"].get("no2", 0) for e in entries]
    so2 = [e["components"].get("so2", 0) for e in entries]
    co = [e["components"].get("co", 0) for e in entries]

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Scatter(x=times, y=aqi_values, mode="lines+markers",
                             name="AQI", line=dict(color="black", width=3)), secondary_y=False)

    for name, vals in [("PM2.5 (µg/m³)", pm25), ("PM10 (µg/m³)", pm10),
                       ("O₃ (µg/m³)", o3), ("NO₂ (µg/m³)", no2),
                       ("SO₂ (µg/m³)", so2), ("CO (µg/m³)", co)]:
        fig.add_trace(go.Scatter(x=times, y=vals, mode="lines", name=name), secondary_y=True)

    fig.update_layout(title=f"Air Quality Forecast — next {hours} hours",
                      xaxis_title="Time", hovermode="x unified",
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig.update_yaxes(title_text="AQI (1-5)", secondary_y=False)
    fig.update_yaxes(title_text="Concentration (µg/m³)", secondary_y=True)
    return fig