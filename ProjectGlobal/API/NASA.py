import os
import requests
import streamlit as st

NASA_APOD_URL = "https://api.nasa.gov/planetary/apod"


def _api_key():
    """Resolve key: Streamlit secrets -> env -> DEMO_KEY (rate-limited fallback)."""
    try:
        if "NASA_API_KEY" in st.secrets:
            return st.secrets["NASA_API_KEY"]
    except Exception:
        pass
    return os.getenv("NASA_API_KEY") or os.getenv("NASA_KEY") or "DEMO_KEY"


def get_apod(date=None, api_key=None):
    """Fetch APOD. Returns dict or raises RuntimeError with a friendly message."""
    key = api_key or _api_key()
    params = {"api_key": key}
    if date:
        params["date"] = date
    try:
        r = requests.get(NASA_APOD_URL, params=params, timeout=15)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Failed to retrieve NASA data. Please check your NASA API. ({e})")

    # NASA returns 200 with an error envelope for some failures
    try:
        data = r.json()
    except ValueError:
        raise RuntimeError(f"Failed to retrieve NASA data. Please check your NASA API. (non-JSON response, HTTP {r.status_code})")

    if not r.ok or (isinstance(data, dict) and data.get("code") not in (None, 200)):
        msg = data.get("msg") if isinstance(data, dict) else None
        raise RuntimeError(f"Failed to retrieve NASA data. Please check your NASA API. ({msg or r.status_code})")

    return data


def render_nasa():
    st.subheader("🚀 NASA Astronomy Picture of the Day")
    try:
        data = get_apod()
    except RuntimeError as e:
        st.error(str(e))
        st.info("Get a free key at https://api.nasa.gov/ and add `NASA_API_KEY` to your Streamlit secrets.")
        return

    media_type = data.get("media_type", "image")
    title = data.get("title", "Astronomy Picture of the Day")
    img_url = data.get("hdurl") or data.get("url")

    if media_type == "image" and img_url:
        st.image(img_url, caption=f"{title} — {data.get('date', '')}",
                 use_container_width=True)
    elif media_type == "video" and data.get("url"):
        st.video(data["url"])
        st.caption(title)
    else:
        st.warning("No media available for today.")

    if data.get("explanation"):
        with st.expander("Explanation"):
            st.write(data["explanation"])

    if data.get("copyright"):
        st.caption(f"© {data['copyright']}")
