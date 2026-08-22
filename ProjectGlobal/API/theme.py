# Theme-aware color utilities for Plotly charts
# Provides consistent colors that work in both light and dark themes

from typing import Dict, List
import streamlit as st

# ── Color Palettes ─────────────────────────────────────────

# Primary brand colors (work in both themes)
BRAND_PRIMARY = "#2563eb"      # Blue 600
BRAND_SECONDARY = "#0891b2"    # Cyan 600
BRAND_ACCENT = "#f59e0b"       # Amber 500
BRAND_SUCCESS = "#059669"      # Emerald 600
BRAND_WARNING = "#dc2626"      # Red 600

# Categorical palette (colorblind-safe, distinct)
CATEGORICAL_PALETTE = [
    "#2563eb",  # Blue
    "#059669",  # Emerald
    "#dc2626",  # Red
    "#f59e0b",  # Amber
    "#7c3aed",  # Violet
    "#0891b2",  # Cyan
    "#ea580c",  # Orange
    "#db2777",  # Pink
    "#65a30d",  # Lime
    "#9333ea",  # Purple
]

# Sequential palettes for continuous data
SEQ_BLUE = ["#eff6ff", "#bfdbfe", "#60a5fa", "#2563eb", "#1e40af", "#172554"]
SEQ_GREEN = ["#f0fdf4", "#bbf7d0", "#4ade80", "#059669", "#047857", "#022c22"]
SEQ_RED = ["#fef2f2", "#fecaca", "#f87171", "#dc2626", "#b91c1c", "#7f1d1d"]
SEQ_VIRIDIS = ["#fde725", "#7ad151", "#22a884", "#2a788e", "#414487", "#440154"]

# Diverging palette
DIVERGING_RDBU = ["#67001f", "#b2182b", "#d6604d", "#f4a582", "#fddbc7",
                  "#f7f7f7", "#d1e5f0", "#92c5de", "#4393c3", "#2166ac", "#053061"]

# ── Theme Detection ────────────────────────────────────────

def is_dark_theme() -> bool:
    """Detect if Streamlit is in dark mode."""
    try:
        return st.get_option("theme.base") == "dark"
    except Exception:
        return False


def get_theme_colors() -> Dict[str, str]:
    """Return theme-aware color values."""
    dark = is_dark_theme()
    if dark:
        return {
            "bg": "#0f172a",
            "bg_secondary": "#1e293b",
            "text": "#f1f5f9",
            "text_muted": "#94a3b8",
            "grid": "rgba(148,163,184,0.15)",
            "border": "rgba(148,163,184,0.2)",
            "card_bg": "#1e293b",
        }
    return {
        "bg": "#ffffff",
        "bg_secondary": "#f8fafc",
        "text": "#1e293b",
        "text_muted": "#64748b",
        "grid": "rgba(15,23,42,0.08)",
        "border": "rgba(15,23,42,0.1)",
        "card_bg": "#ffffff",
    }


# ── Plotly Template ────────────────────────────────────────

def get_plotly_template() -> Dict:
    """Generate a theme-aware Plotly template."""
    colors = get_theme_colors()
    dark = is_dark_theme()

    return {
        "layout": {
            "font": {"family": "Inter, system-ui, sans-serif", "color": colors["text"]},
            "paper_bgcolor": colors["bg"],
            "plot_bgcolor": colors["bg"],
            "title": {
                "font": {"size": 16, "color": colors["text"], "family": "Inter, system-ui, sans-serif"},
                "x": 0.5,
                "xanchor": "center",
            },
            "xaxis": {
                "gridcolor": colors["grid"],
                "zerolinecolor": colors["border"],
                "linecolor": colors["border"],
                "tickfont": {"color": colors["text_muted"], "size": 11},
                "title": {"font": {"color": colors["text"], "size": 12}},
            },
            "yaxis": {
                "gridcolor": colors["grid"],
                "zerolinecolor": colors["border"],
                "linecolor": colors["border"],
                "tickfont": {"color": colors["text_muted"], "size": 11},
                "title": {"font": {"color": colors["text"], "size": 12}},
            },
            "legend": {
                "bgcolor": "rgba(0,0,0,0)",
                "font": {"color": colors["text"], "size": 11},
                "bordercolor": colors["border"],
                "borderwidth": 1,
            },
            "colorway": CATEGORICAL_PALETTE,
            "hoverlabel": {
                "bgcolor": colors["card_bg"],
                "font": {"color": colors["text"], "size": 12},
                "bordercolor": colors["border"],
            },
            "margin": {"l": 60, "r": 30, "t": 60, "b": 50},
            "hovermode": "x unified",
        }
    }


# ── Chart Helpers ──────────────────────────────────────────

def apply_theme(fig, height: int = 450, show_legend: bool = True):
    """Apply theme-aware styling to a Plotly figure."""
    colors = get_theme_colors()
    dark = is_dark_theme()

    fig.update_layout(
        template="plotly_white" if not dark else "plotly_dark",
        height=height,
        showlegend=show_legend,
        font={"family": "Inter, system-ui, sans-serif", "color": colors["text"]},
        paper_bgcolor=colors["bg"],
        plot_bgcolor=colors["bg"],
        margin={"l": 60, "r": 30, "t": 60, "b": 50},
        hovermode="x unified",
        legend={
            "bgcolor": "rgba(0,0,0,0)",
            "font": {"color": colors["text"], "size": 11},
            "bordercolor": colors["border"],
            "borderwidth": 1,
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
    )

    fig.update_xaxes(
        gridcolor=colors["grid"],
        zerolinecolor=colors["border"],
        linecolor=colors["border"],
        tickfont={"color": colors["text_muted"], "size": 11},
        title_font={"color": colors["text"], "size": 12},
    )

    fig.update_yaxes(
        gridcolor=colors["grid"],
        zerolinecolor=colors["border"],
        linecolor=colors["border"],
        tickfont={"color": colors["text_muted"], "size": 11},
        title_font={"color": colors["text"], "size": 12},
    )

    return fig


def get_categorical_colors(n: int) -> List[str]:
    """Get n distinct colors from categorical palette."""
    if n <= len(CATEGORICAL_PALETTE):
        return CATEGORICAL_PALETTE[:n]
    # Cycle if more needed
    return [CATEGORICAL_PALETTE[i % len(CATEGORICAL_PALETTE)] for i in range(n)]


# ── KPI Card Helpers ───────────────────────────────────────

def render_kpi_card(label: str, value: str, delta: str = None, icon: str = None):
    """Render a styled KPI metric card."""
    st.metric(label=label, value=value, delta=delta)


def render_metric_row(metrics: list):
    """Render a row of KPI metrics."""
    cols = st.columns(len(metrics))
    for col, (label, value, delta, icon) in zip(cols, metrics):
        with col:
            st.metric(label=label, value=value, delta=delta)