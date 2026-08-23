import re
import requests
from datetime import date, timedelta
from dotenv import load_dotenv
import json
import os
import streamlit as st

BASE_URL = "https://api.nasa.gov/planetary/apod"
SAVE_DIR = os.path.join(os.path.dirname(__file__), "cache", "nasa")

YOUTUBE_ID_RE = re.compile(
    r'(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|youtu\.be/)([^&\s?/]+)'
)
# NASA's video days are commonly YouTube, but also frequently Vimeo — the
# NASA API's own repo notes this. player.vimeo.com/video/ID is the embed
# form; vimeo.com/ID (no "player.") is the watch page, not embeddable.
VIMEO_ID_RE = re.compile(r'(?:player\.)?vimeo\.com/(?:video/)?(\d+)')

# Extensions safe to hand straight to a <video>/<iframe> element as a raw
# file (no transcoding, just streamed bytes).
DIRECT_VIDEO_EXTENSIONS = (".mp4", ".webm", ".ogv", ".mov")

load_dotenv()
API_KEY = os.getenv("NASA_KEY") or st.secrets.get("NASA_KEY")


# ─── Fetch & Fallback ────────────────────────────────────

def download_apod():
    """Fetch APOD from NASA. Falls back to yesterday on 404 (publish gap).

    ``thumbs=True`` asks NASA to include a ``thumbnail_url`` whenever
    ``media_type`` is "video" (roughly 1 in 5-10 days APOD is a video, not
    a photo) — without it, video days have no image field at all, only a
    YouTube link, which is what makes the picture look "missing" if you
    render it with ``st.image``.
    """
    params = {"api_key": API_KEY, "thumbs": True}

    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        if response.status_code == 404:
            print("[WARN] Today's APOD isn't published yet — falling back to yesterday's")
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            response = requests.get(BASE_URL, params={**params, "date": yesterday}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"[WARN] NASA APOD request failed: {e}")
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
        print("[INFO] Loaded APOD from cache")
        return data
    print("[INFO] Downloading APOD from NASA")
    data = download_apod()
    if data:
        save_apod(data)
    return data


# ─── Media Resolution ────────────────────────────────────
# Decides HOW an APOD payload should be displayed. app.py should only call
# this and hand the result to st.image / st.video — it should not inspect
# media_type or build URLs itself.

def resolve_apod_media(data: dict | None) -> dict:
    """Work out what to render for a given APOD payload.

    Returns a dict with:
      kind        - "image", "video", "unsupported", or "missing"
      player      - only set when kind == "video": "native" (hand
                    display_url to st.video — covers YouTube and direct
                    file URLs, both of which st.video understands
                    natively) or "iframe" (needs a raw embed via
                    st.components.v1.iframe — covers Vimeo and anything
                    else with a known embeddable player URL)
      display_url - the URL to render; None if kind is "unsupported"/"missing"
      thumb_url   - optional preview image for video days (only populated
                    when NASA returned one, which requires download_apod's
                    thumbs=True param)
      external_url - a link that should always work, for a "view it on
                    NASA's site instead" fallback button

    NASA APOD is a video roughly 1 in 5-10 days, and those videos are
    commonly hosted on YouTube *or Vimeo* (NASA's own API repo notes
    both). st.video() only special-cases YouTube — Vimeo's watch-page URL
    isn't something it can embed, and would silently fail the same way
    st.image() silently failed on YouTube links. Vimeo (and anything else
    without a known player URL) needs an actual <iframe> embed, the same
    approach most websites use for third-party video players — Streamlit
    exposes that directly via st.components.v1.iframe(). This function is
    the one place that decides which path a given URL needs; app.py just
    dispatches on `player`.
    """
    if not data:
        return {"kind": "missing", "player": None, "display_url": None, "thumb_url": None, "external_url": None}

    media_type = data.get("media_type", "image")
    url = data.get("url")
    hdurl = data.get("hdurl")
    thumb_url = data.get("thumbnail_url")

    if media_type == "image" and url:
        return {
            "kind": "image",
            "player": None,
            "display_url": hdurl or url,
            "thumb_url": None,
            "external_url": url,
        }

    if media_type == "video" and url:
        player, embed_url = _resolve_video_url(url)
        if player:
            return {
                "kind": "video",
                "player": player,
                "display_url": embed_url,
                "thumb_url": thumb_url,
                "external_url": url,
            }
        # A video, but not YouTube, Vimeo, or a direct file — some other
        # host's watch page we don't have a known embed form for. Rather
        # than gamble on an iframe that a site's X-Frame-Options might
        # block anyway, hand back a link.
        return {"kind": "unsupported", "player": None, "display_url": None, "thumb_url": thumb_url, "external_url": url}

    if url:
        # Some future/unlisted media_type NASA might add — don't guess how
        # to render it, just hand back a link.
        return {"kind": "unsupported", "player": None, "display_url": None, "thumb_url": thumb_url, "external_url": url}

    return {"kind": "missing", "player": None, "display_url": None, "thumb_url": None, "external_url": None}


def _resolve_video_url(url: str) -> tuple[str, str] | tuple[None, None]:
    """Return (player, embed_url) for a video URL, or (None, None) if we
    don't have a known way to embed it.

    player is "native" for anything st.video() understands directly
    (YouTube, or a URL that's already a raw video file — no transcoding,
    just streamed bytes either way), or "iframe" for platforms that need
    a manual <iframe> embed (currently Vimeo). Video duration is
    irrelevant to either path: the browser streams straight from the
    source, Streamlit never re-serves the file itself.
    """
    youtube = _youtube_embed_url(url)
    if youtube:
        return "native", youtube

    vimeo = _vimeo_embed_url(url)
    if vimeo:
        return "iframe", vimeo

    if url.split("?")[0].lower().endswith(DIRECT_VIDEO_EXTENSIONS):
        return "native", url

    return None, None


def _youtube_embed_url(url: str) -> str | None:
    """Normalize any YouTube URL shape (watch/shorts/youtu.be/already-embed)
    to the /embed/ form Streamlit's video player reliably recognizes.
    Returns None if the URL isn't a YouTube link at all.
    """
    match = YOUTUBE_ID_RE.search(url)
    return f"https://www.youtube.com/embed/{match.group(1)}" if match else None


def _vimeo_embed_url(url: str) -> str | None:
    """Normalize a Vimeo watch-page or player URL to the player.vimeo.com
    embed form usable in an <iframe>. Returns None if not a Vimeo link.
    """
    match = VIMEO_ID_RE.search(url)
    return f"https://player.vimeo.com/video/{match.group(1)}" if match else None
