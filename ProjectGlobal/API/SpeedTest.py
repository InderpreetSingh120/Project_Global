"""
Speed Test Module
Runs internet speed tests and generates Plotly visualizations for download/upload/ping
metrics, connection ratings, and download-time comparisons.
"""

import socket
import speedtest
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pandas as pd
from typing import Dict, List, Tuple
import time


def run_speedtest(timeout: int = 30) -> Dict:
    """
    Run an internet speed test using speedtest.net servers.

    Args:
        timeout: Maximum seconds to wait for the test.

    Returns:
        dict: download_mbps, upload_mbps, ping_ms, server, location, country,
              timestamp, datetime

    Raises:
        ConnectionError: If speedtest.net configuration cannot be retrieved.
        RuntimeError: If the speed test itself fails.
    """
    # speedtest-cli has no per-call timeout argument — it relies on the socket
    # module's global default, so that's the only way to actually bound it.
    # Restored afterward so this doesn't leak into unrelated requests elsewhere.
    previous_timeout = socket.getdefaulttimeout() 
    socket.setdefaulttimeout(timeout)
    try:
        st_speedtest = speedtest.Speedtest()
        st_speedtest.get_best_server()

        download = st_speedtest.download() / 1_000_000  # bits/s → Mbps
        upload = st_speedtest.upload() / 1_000_000
        ping = st_speedtest.results.ping

        server_info = st_speedtest.results.server

        return {
            "download_mbps": round(download, 2),
            "upload_mbps": round(upload, 2),
            "ping_ms": round(ping, 2),
            "server": server_info.get("name", "Unknown"),
            "location": server_info.get("location", "Unknown"),
            "country": server_info.get("country", "Unknown"),
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    except speedtest.ConfigRetrievalError:
        raise ConnectionError(
            "Unable to retrieve speedtest.net configuration. Check your internet connection."
        )
    except Exception as e:
        raise RuntimeError(f"Speed test failed: {e}")
    finally:
        socket.setdefaulttimeout(previous_timeout)


def get_connection_rating(download_mbps: float) -> Tuple[str, str]:
    """
    Return a rating label and color based on download speed.

    Args:
        download_mbps: Download speed in Mbps.

    Returns:
        tuple: (rating_text, rating_color_hex)
    """
    if download_mbps >= 200:
        return "🚀 Exceptional", "#00C853"
    elif download_mbps >= 100:
        return "⭐ Excellent", "#64DD17"
    elif download_mbps >= 50:
        return "👍 Very Good", "#29B6F6"
    elif download_mbps >= 20:
        return "✅ Good", "#FFD600"
    elif download_mbps >= 5:
        return "⚠️ Fair", "#FF9100"
    else:
        return "❌ Poor", "#FF1744"


def get_overall_score(results: Dict) -> int:
    """
    Calculate an overall connection quality score (0–100).

    Weights: Download 40%, Upload 30%, Latency 30%.
    """
    dl_score = min(results["download_mbps"] / 200 * 40, 40)
    ul_score = min(results["upload_mbps"] / 100 * 30, 30)
    ping_score = max(30 - results["ping_ms"] / 1.5, 0)
    return int(dl_score + ul_score + ping_score)


def create_speed_gauge_figure(results: Dict) -> go.Figure:
    """
    Create a Plotly figure with three gauge indicators: Download, Upload, Ping.

    Args:
        results: dict from run_speedtest()

    Returns:
        plotly.graph_objects.Figure
    """
    dl = results["download_mbps"]
    ul = results["upload_mbps"]
    ping = results["ping_ms"]

    dl_max = max(dl * 1.5, 50)
    ul_max = max(ul * 1.5, 50)
    ping_max = max(ping * 2, 50)

    fig = make_subplots(
        rows=1,
        cols=3,
        specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]],
        subplot_titles=(
            "⬇️ Download Speed (Mbps)",
            "⬆️ Upload Speed (Mbps)",
            "🏓 Ping (ms)",
        ),
    )

    # ── Download Gauge ──
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=dl,
            title={"text": "Download", "font": {"size": 14}},
            delta={
                "reference": 50,
                "increasing": {"color": "green"},
                "decreasing": {"color": "red"},
            },
            number={"suffix": " Mbps", "font": {"size": 20}},
            gauge={
                "axis": {"range": [0, dl_max], "tickwidth": 1},
                "bar": {"color": "#00BFA5", "thickness": 0.25},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": [0, 10], "color": "#FFEBEE"},
                    {"range": [10, 30], "color": "#FFF3E0"},
                    {"range": [30, 60], "color": "#E8F5E9"},
                    {"range": [60, 100], "color": "#C8E6C9"},
                    {"range": [100, dl_max], "color": "#A5D6A7"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 50,  # meaningful threshold, not the actual value
                },
            },
        ),
        row=1,
        col=1,
    )

    # ── Upload Gauge ──
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=ul,
            title={"text": "Upload", "font": {"size": 14}},
            number={"suffix": " Mbps", "font": {"size": 20}},
            gauge={
                "axis": {"range": [0, ul_max], "tickwidth": 1},
                "bar": {"color": "#42A5F5", "thickness": 0.25},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": [0, 5], "color": "#FFEBEE"},
                    {"range": [5, 20], "color": "#FFF3E0"},
                    {"range": [20, 50], "color": "#E3F2FD"},
                    {"range": [50, ul_max], "color": "#BBDEFB"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 25,
                },
            },
        ),
        row=1,
        col=2,
    )

    # ── Ping Gauge ──
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=ping,
            title={"text": "Ping", "font": {"size": 14}},
            number={"suffix": " ms", "font": {"size": 20}},
            gauge={
                "axis": {"range": [0, ping_max], "tickwidth": 1},
                "bar": {"color": "#FF7043", "thickness": 0.25},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": [0, 20], "color": "#C8E6C9"},
                    {"range": [20, 50], "color": "#FFF9C4"},
                    {"range": [50, 100], "color": "#FFE0B2"},
                    {"range": [100, ping_max], "color": "#FFCCBC"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 50,
                },
            },
        ),
        row=1,
        col=3,
    )

    fig.update_layout(
        height=420,
        margin=dict(t=60, b=20, l=20, r=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Segoe UI, sans-serif"),
    )

    return fig


def create_download_comparison_figure(download_mbps: float) -> go.Figure:
    """
    Create a bar chart showing estimated download times for various file sizes.

    Args:
        download_mbps: Download speed in Mbps.

    Returns:
        plotly.graph_objects.Figure
    """
    if download_mbps <= 0:
        download_mbps = 0.01  # avoid division by zero

    file_sizes_gb = [1, 5, 10, 50, 100, 500, 1000]

    estimated_times_sec = []
    for size_gb in file_sizes_gb:
        time_seconds = (size_gb * 8 * (1024 ** 3)) / (download_mbps * 1_000_000)
        estimated_times_sec.append(time_seconds)

    # Format times nicely
    time_labels = []
    for t in estimated_times_sec:
        if t < 1:
            time_labels.append(f"{t * 1000:.0f} ms")
        elif t < 60:
            time_labels.append(f"{t:.1f} sec")
        elif t < 3600:
            time_labels.append(f"{t / 60:.1f} min")
        else:
            time_labels.append(f"{t / 3600:.1f} hrs")

    # Images at ~2 MB each
    images_count = [int(size_gb * 1024 / 2) for size_gb in file_sizes_gb]

    df = pd.DataFrame(
        {
            "File Size": [f"{size} GB" for size in file_sizes_gb],
            "Time (seconds)": estimated_times_sec,
            "Display Label": time_labels,
            "Images (~2 MB each)": images_count,
        }
    )

    fig = px.bar(
        df,
        x="File Size",
        y="Time (seconds)",
        text="Display Label",
        color="Time (seconds)",
        color_continuous_scale="Blues",
        labels={"Time (seconds)": "Estimated Time", "File Size": "File Size"},
    )

    # Add image-count annotations above each bar
    for _, row in df.iterrows():
        fig.add_annotation(
            x=row["File Size"],
            y=row["Time (seconds)"] * 1.12,
            text=f"~{row['Images (~2 MB each)']:,} imgs",
            showarrow=False,
            font=dict(size=9, color="#555555"),
        )

    fig.update_layout(
        title=dict(
            text=f"📥 Estimated Download Times at {download_mbps} Mbps",
            font=dict(size=18),
        ),
        height=480,
        xaxis_title="File Size",
        yaxis_title="Time (seconds)",
        coloraxis_showscale=False,
        font=dict(family="Segoe UI, sans-serif"),
    )

    fig.update_traces(
        textposition="outside",
        textfont_size=11,
        marker_line_color="rgb(8,48,107)",
        marker_line_width=1.5,
    )

    return fig


def create_speed_radar_figure(results: Dict) -> go.Figure:
    """
    Create a radar chart showing connection quality across four dimensions.

    Args:
        results: dict from run_speedtest()

    Returns:
        plotly.graph_objects.Figure
    """
    download_norm = min(results["download_mbps"] / 200 * 100, 100)
    upload_norm = min(results["upload_mbps"] / 100 * 100, 100)
    latency_score = max(100 - results["ping_ms"] / 1.5, 0)
    stability = min((download_norm + upload_norm + latency_score) / 3, 100)

    categories = ["Download", "Upload", "Low Latency", "Stability"]
    values = [download_norm, upload_norm, latency_score, stability]

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=values + [values[0]],
            theta=categories + [categories[0]],
            fill="toself",
            fillcolor="rgba(0, 191, 165, 0.35)",
            line=dict(color="#00BFA5", width=2.5),
            name="Your Connection",
            marker=dict(size=6, color="#00BFA5"),
        )
    )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], dtick=20, showticklabels=True),
            bgcolor="rgba(0,0,0,0)",
        ),
        title=dict(text="📡 Connection Quality Radar", font=dict(size=16)),
        height=420,
        showlegend=False,
        font=dict(family="Segoe UI, sans-serif"),
    )

    return fig


def create_speed_history_figure(history: List[Dict]) -> go.Figure:
    """
    Create a line chart showing speed test history over time.

    Args:
        history: list of result dicts from run_speedtest()

    Returns:
        plotly.graph_objects.Figure
    """
    if not history:
        return go.Figure()

    df = pd.DataFrame(history)
    df["datetime"] = pd.to_datetime(df["datetime"])

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["datetime"],
            y=df["download_mbps"],
            mode="lines+markers",
            name="Download (Mbps)",
            line=dict(color="#00BFA5", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["datetime"],
            y=df["upload_mbps"],
            mode="lines+markers",
            name="Upload (Mbps)",
            line=dict(color="#42A5F5", width=2),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df["datetime"],
            y=df["ping_ms"],
            mode="lines+markers",
            name="Ping (ms)",
            line=dict(color="#FF7043", width=2),
            yaxis="y2",
        )
    )

    fig.update_layout(
        title=dict(text="📊 Speed Test History", font=dict(size=16)),
        height=400,
        xaxis_title="Time",
        yaxis_title="Speed (Mbps)",
        yaxis2=dict(
            title="Ping (ms)",
            overlaying="y",
            side="right",
        ),
        legend=dict(x=0.01, y=0.99),
        font=dict(family="Segoe UI, sans-serif"),
    )

    return fig