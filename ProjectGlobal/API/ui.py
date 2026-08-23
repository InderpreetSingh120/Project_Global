# ═══════════════════════════════════════════════════════════════
# Project Global — Unified Design System
# Single source of truth for all UI: themes, colors, typography, spacing,
# components, navigation, Plotly styling, and theme switching.
# ═══════════════════════════════════════════════════════════════

from __future__ import annotations
from typing import Dict, List, Optional, Literal, Any
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px


# ═══════════════════════════════════════════════════════════════
# 1. COLOR SYSTEM — Exact specification from design brief
# ═══════════════════════════════════════════════════════════════

# Base palettes (match design brief exactly)
LIGHT_BASE = {
    "background": "#F6F8FB",
    "surface": "#FFFFFF",
    "secondary_surface": "#EEF2F7",
    "text_primary": "#172033",
    "text_secondary": "#667085",
    "text_muted": "#9CA3AF",
    "border": "#DDE3EA",
    "grid": "rgba(21,32,43,0.08)",
}

# Section accent colors (from design brief)
SECTION_ACCENTS = {
    "overview":   {"primary": "#3B82F6", "secondary": "#06B6D4", "icon": "🏠", "name": "Overview"},
    "news":       {"primary": "#2563EB", "secondary": "#6366F1", "icon": "📰", "name": "News"},
    "weather":    {"primary": "#0891B2", "secondary": "#0EA5E9", "icon": "🌤️", "name": "Weather"},
    "nasa":       {"primary": "#7C3AED", "secondary": "#4F46E5", "icon": "🪐", "name": "NASA"},
    "internet":   {"primary": "#059669", "secondary": "#0D9488", "icon": "🚀", "name": "Internet"},
    "ai_model":   {"primary": "#9333EA", "secondary": "#C026D3", "icon": "🤖", "name": "AI Models"},
    "ghi":        {"primary": "#3B82F6", "secondary": "#06B6D4", "icon": "😊", "name": "Happiness"},
    "assistant":  {"primary": "#9333EA", "secondary": "#C026D3", "icon": "💬", "name": "Assistant"},
}

# Semantic colors
SEMANTIC = {
    "success": "#10B981",
    "warning": "#F59E0B",
    "error":   "#EF4444",
    "info":    "#3B82F6",
}

# Categorical palette for charts (colorblind-safe)
CATEGORICAL = [
    "#3B82F6", "#10B981", "#F59E0B", "#EF4444",
    "#8B5CF6", "#06B6D4", "#F97316", "#EC4899",
    "#65A30D", "#9333EA",
]

# Weather condition color mapping
WEATHER_COLORS = {
    "clear":        "#F59E0B",
    "clouds":       "#6B7280",
    "rain":         "#0891B2",
    "drizzle":      "#0EA5E9",
    "thunderstorm": "#7C3AED",
    "snow":         "#E5E7EB",
    "mist":         "#9CA3AF",
    "fog":          "#9CA3AF",
    "haze":         "#9CA3AF",
    "default":      "#0891B2",
}

# AQI level colors (1-5)
AQI_COLORS = {
    1: "#10B981",  # Good
    2: "#F59E0B",  # Fair
    3: "#F97316",  # Moderate
    4: "#EF4444",  # Poor
    5: "#7F1D1D",  # Very Poor
}


# ════════════════════════════════════════════════════════════════
# 2. TYPOGRAPHY SYSTEM
# ════════════════════════════════════════════════════════════════

TYPOGRAPHY = {
    "font_family": "Inter, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Apple Color Emoji', 'Segoe UI Emoji', 'Noto Color Emoji', sans-serif",
    "font_family_mono": "JetBrains Mono, Fira Code, Consolas, 'Segoe UI Emoji', monospace",
    "scale": {
        "display":    {"size": "2.5rem", "weight": 800, "line_height": 1.1, "letter_spacing": "-0.02em"},
        "h1":         {"size": "2rem",   "weight": 700, "line_height": 1.2, "letter_spacing": "-0.01em"},
        "h2":         {"size": "1.5rem", "weight": 700, "line_height": 1.3, "letter_spacing": "0"},
        "h3":         {"size": "1.25rem","weight": 600, "line_height": 1.3, "letter_spacing": "0"},
        "h4":         {"size": "1.125rem","weight": 600, "line_height": 1.4, "letter_spacing": "0"},
        "body_lg":    {"size": "1.125rem","weight": 400, "line_height": 1.6, "letter_spacing": "0"},
        "body":       {"size": "1rem",   "weight": 400, "line_height": 1.6, "letter_spacing": "0"},
        "body_sm":    {"size": "0.875rem","weight": 400, "line_height": 1.5, "letter_spacing": "0"},
        "caption":    {"size": "0.75rem", "weight": 400, "line_height": 1.5, "letter_spacing": "0.01em"},
        "overline":   {"size": "0.75rem", "weight": 600, "line_height": 1.5, "letter_spacing": "0.05em", "text_transform": "uppercase"},
    }
}


# ════════════════════════════════════════════════════════════════
# 3. SPACING SYSTEM (4px base unit)
# ════════════════════════════════════════════════════════════════

SPACING = {
    "0":     "0",
    "1":     "0.25rem",   # 4px
    "2":     "0.5rem",    # 8px
    "3":     "0.75rem",   # 12px
    "4":     "1rem",      # 16px
    "5":     "1.25rem",   # 20px
    "6":     "1.5rem",    # 24px
    "8":     "2rem",      # 32px
    "10":    "2.5rem",    # 40px
    "12":    "3rem",      # 48px
    "16":    "4rem",      # 64px
    "20":    "5rem",      # 80px
    "24":    "6rem",      # 96px
}

# Semantic spacing aliases
SPACING_ALIAS = {
    "xs":  SPACING["1"],
    "sm":  SPACING["2"],
    "md":  SPACING["4"],
    "lg":  SPACING["6"],
    "xl":  SPACING["8"],
    "2xl": SPACING["10"],
    "3xl": SPACING["12"],
    "4xl": SPACING["16"],
}


# ════════════════════════════════════════════════════════════════
# 4. BORDER RADIUS
# ════════════════════════════════════════════════════════════════

RADIUS = {
    "none": "0",
    "sm":   "0.375rem",   # 6px
    "md":   "0.5rem",     # 8px
    "lg":   "0.75rem",    # 12px
    "xl":   "1rem",       # 16px
    "2xl":  "1.5rem",     # 24px
    "full": "9999px",
}


# ════════════════════════════════════════════════════════════════
# 5. SHADOWS
# ════════════════════════════════════════════════════════════════

SHADOWS_LIGHT = {
    "none": "none",
    "sm": "0 1px 2px rgba(15,23,42,0.05)",
    "md": "0 4px 6px rgba(15,23,42,0.07)",
    "lg": "0 10px 15px rgba(15,23,42,0.1)",
    "xl": "0 20px 25px rgba(15,23,42,0.15)",
    "inner": "inset 0 2px 4px rgba(15,23,42,0.06)",
}

# Dark mode deliberately does NOT reuse the light-mode shadow shapes with a
# darker tint — a black drop-shadow is nearly invisible against a near-black
# background and reads as a rendering glitch rather than elevation. Instead,
# depth comes from a soft 1px top highlight (light catching the card's top
# edge, the way real panels read under a single overhead light) plus a
# gentle ambient shadow for grounding. This is "Data Control" elevation:
# calm and structural, not glowing.
SHADOWS_DARK = {
    "none": "none",
    "sm": "0 1px 0 rgba(255,255,255,0.025)",
    "md": "0 1px 0 rgba(255,255,255,0.035), 0 3px 10px rgba(0,0,0,0.35)",
    "lg": "0 1px 0 rgba(255,255,255,0.045), 0 10px 24px rgba(0,0,0,0.45)",
    "xl": "0 1px 0 rgba(255,255,255,0.06), 0 20px 40px rgba(0,0,0,0.55)",
    "inner": "inset 0 1px 3px rgba(0,0,0,0.5)",
}


# ════════════════════════════════════════════════════════════════
# 6. TRANSITIONS
# ════════════════════════════════════════════════════════════════

TRANSITIONS = {
    "fast": "150ms ease",
    "normal": "200ms ease",
    "slow": "300ms ease",
}


# ════════════════════════════════════════════════════════════════
# 7. Z-INDEX LAYERS
# ════════════════════════════════════════════════════════════════

Z_INDEX = {
    "base": 0,
    "dropdown": 100,
    "sticky": 200,
    "fixed": 300,
    "modal_backdrop": 400,
    "modal": 500,
    "popover": 600,
    "tooltip": 700,
    "toast": 800,
}


# ════════════════════════════════════════════════════════════════
# 8. BREAKPOINTS
# ════════════════════════════════════════════════════════════════

BREAKPOINTS = {
    "sm":  "640px",
    "md":  "768px",
    "lg":  "1024px",
    "xl":  "1280px",
    "2xl": "1536px",
}


# ════════════════════════════════════════════════════════════════
# 9. THEME DETECTION & RESOLUTION
# ════════════════════════════════════════════════════════════════

def is_dark() -> bool:
    """Light theme only."""
    return False


def get_base_colors() -> Dict[str, str]:
    """Get the base color palette (light theme only)."""
    return LIGHT_BASE


def get_section_theme(section_key: str) -> Dict[str, Any]:
    """Get accent colors for a section."""
    return SECTION_ACCENTS.get(section_key, SECTION_ACCENTS["overview"])


def get_css_variables(section_key: str = "overview") -> str:
    """Generate CSS custom properties for current theme + section."""
    base = get_base_colors()
    dark = is_dark()
    section = get_section_theme(section_key)
    
    return f"""
    :root {{
        --bg: {base['background']};
        --surface: {base['surface']};
        --surface-secondary: {base['secondary_surface']};
        --surface-hover: {base['secondary_surface'] if dark else base['surface']};
        --border: {base['border']};
        --grid: {base['grid']};
        --text: {base['text_primary']};
        --text-secondary: {base['text_secondary']};
        --text-muted: {base['text_muted']};
        --shadow: {SHADOWS_DARK['md'] if dark else SHADOWS_LIGHT['md']};
        --shadow-resting: {SHADOWS_DARK['sm'] if dark else SHADOWS_LIGHT['sm']};
        --shadow-hover: {SHADOWS_DARK['lg'] if dark else SHADOWS_LIGHT['lg']};
        --shadow-card: {SHADOWS_DARK['md'] if dark else SHADOWS_LIGHT['md']};
        --shadow-card-hover: {SHADOWS_DARK['lg'] if dark else SHADOWS_LIGHT['lg']};
        --radius-sm: {RADIUS['sm']};
        --radius-md: {RADIUS['md']};
        --radius-lg: {RADIUS['lg']};
        --radius-xl: {RADIUS['xl']};
        --transition-fast: {TRANSITIONS['fast']};
        --transition-normal: {TRANSITIONS['normal']};
        --transition-slow: {TRANSITIONS['slow']};
        --accent-primary: {section['primary']};
        --accent-secondary: {section['secondary']};
        --accent-gradient: linear-gradient(135deg, {section['primary']}, {section['secondary']});
        --font-family: {TYPOGRAPHY['font_family']};
        --font-family-mono: {TYPOGRAPHY['font_family_mono']};
    }}
    """


# ════════════════════════════════════════════════════════════════
# 10. CSS INJECTION — Single entry point for all styles
# ════════════════════════════════════════════════════════════════

def inject_theme_css(section_key: str = "overview") -> None:
    """Inject all theme CSS for a section. Call once per page render."""
    section = get_section_theme(section_key)
    base = get_base_colors()
    dark = is_dark()
    primary = section["primary"]
    secondary = section["secondary"]
    
    # Adjust accent brightness for dark mode
    if dark:
        accent_rgb = tuple(int(primary.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        primary_bright = f"rgb({min(255, accent_rgb[0]+30)}, {min(255, accent_rgb[1]+30)}, {min(255, accent_rgb[2]+30)})"
    else:
        primary_bright = primary
    
    st.markdown(f"""
    <style>
    /* Fonts are now loaded here instead of via config.toml's [theme] font
       settings — those apply globally through Streamlit's own engine and
       end up overriding Streamlit's native icon font too (see the note
       on the icon selector below). Loading them ourselves, scoped to our
       own CSS, keeps Inter/JetBrains Mono for app content only.
       @import must be the very first thing in the stylesheet. */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined');

    {get_css_variables(section_key)}
    
    /* ─── RESET & BASE ─── */
    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }}
    
    /* ─── TYPOGRAPHY ─── */
    h1, h2, h3, h4, h5, h6 {{
        font-family: var(--font-family) !important;
        color: var(--text) !important;
    }}
    
    h1 {{ font-size: 2.5rem; font-weight: 800; line-height: 1.1; letter-spacing: -0.02em; margin-bottom: 0.5rem; }}
    h2 {{ font-size: 1.75rem; font-weight: 700; line-height: 1.2; letter-spacing: -0.01em; margin-bottom: 0.75rem; }}
    h3 {{ font-size: 1.25rem; font-weight: 600; line-height: 1.3; margin-bottom: 0.5rem; }}
    h4 {{ font-size: 1.125rem; font-weight: 600; line-height: 1.4; margin-bottom: 0.5rem; }}
    
    /* Icon elements are excluded from the blanket font rule below.
       Material Symbols icons render via ligature text (the literal word
       "arrow_right" gets substituted with a glyph) — that substitution
       only happens in a Material Symbols font. [data-testid="stIconMaterial"]
       is Streamlit's OWN native icon element (settings-menu icons,
       expander chevron, toolbar icons); it is left with NO font-family
       rule at all here so Streamlit's own stylesheet fully controls it —
       previously this file (and, before that, config.toml's global
       [theme] font setting) forced those icons onto Inter, which has no
       ligature table, so the raw word rendered as text and overlapped
       the adjacent label. */
    p, span:not([class*="material-symbols"]):not([class*="material-icons"]):not([data-testid="stIconMaterial"]),
    div:not([class*="material-symbols"]):not([class*="material-icons"]):not([data-testid="stIconMaterial"]),
    label {{ 
        font-family: var(--font-family) !important; 
        color: var(--text) !important; 
        line-height: 1.6;
    }}

    /* [class*="material-symbols"] above covers our OWN custom-rendered
       icons (the section-header icon, KPI card icons, etc. — these are
       plain <span class="material-symbols-outlined"> tags we write
       ourselves, not a Streamlit component) — those need an explicit
       font, which we now load ourselves via the @import above rather
       than assuming it's already on the page. */
    .material-symbols-outlined {{
        font-family: 'Material Symbols Outlined' !important;
        font-weight: normal;
        font-style: normal;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        white-space: nowrap;
        word-wrap: normal;
        direction: ltr;
        -webkit-font-feature-settings: 'liga';
        font-feature-settings: 'liga';
        -webkit-font-smoothing: antialiased;
    }}
    
    .text-secondary {{ color: var(--text-secondary) !important; }}
    .text-muted {{ color: var(--text-muted) !important; }}
    .text-primary {{ color: var(--accent-primary) !important; }}
    
    .overline {{
        font-size: 0.75rem; font-weight: 600; letter-spacing: 0.05em;
        text-transform: uppercase; color: var(--text-muted);
    }}
    
    .caption {{ font-size: 0.75rem; color: var(--text-muted); line-height: 1.5; }}
    
    /* ─── TOP NAVIGATION BAR ─── */
    .global-nav {{
        position: fixed;
        top: 0; left: 0; right: 0;
        z-index: {Z_INDEX['fixed']};
        background: var(--surface);
        border-bottom: 1px solid var(--border);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }}
    
    .global-nav-inner {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        height: 56px;
        padding: 0 1.5rem;
        max-width: 1400px;
        margin: 0 auto;
    }}
    
    .global-nav-brand {{
        display: flex; align-items: center; gap: 0.5rem;
        font-size: 1.25rem; font-weight: 700;
        color: var(--text);
        text-decoration: none;
    }}
    
    .global-nav-brand-icon {{
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; font-size: 1.5rem;
    }}
    
    .global-nav-links {{
        display: flex; align-items: center; gap: 0.25rem;
        background: var(--surface-secondary);
        padding: 4px; border-radius: 12px;
    }}
    
    .global-nav-link {{
        display: flex; align-items: center; gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-size: 0.875rem; font-weight: 500;
        color: var(--text-secondary);
        text-decoration: none;
        transition: all 0.2s ease;
        white-space: nowrap;
    }}
    
    .global-nav-link:hover {{
        color: var(--text);
        background: var(--surface);
    }}
    
    .global-nav-link[aria-current="page"] {{
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        color: white;
        box-shadow: 0 4px 14px rgba(59,130,246,0.25);
    }}
    
    .global-nav-actions {{
        display: flex; align-items: center; gap: 0.5rem;
    }}
    
    .nav-theme-toggle {{
        display: flex; align-items: center; justify-content: center;
        width: 40px; height: 40px;
        border-radius: 10px;
        background: var(--surface-secondary);
        border: 1px solid var(--border);
        color: var(--text);
        cursor: pointer;
        transition: all 0.2s ease;
    }}
    
    .nav-theme-toggle:hover {{
        border-color: var(--accent-primary);
        background: var(--surface-secondary);
    }}
    
    /* ─── PAGE CONTAINER ─── */
    .page-container {{
        padding-top: 72px; /* nav height + margin */
        padding-bottom: 2rem;
        max-width: 1400px;
        margin: 0 auto;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }}
    
    /* ─── SECTION HEADER ─── */
    .section-header {{
        display: flex; align-items: center; gap: 0.75rem;
        margin-bottom: 1.5rem;
    }}
    
    .section-header-icon {{
        font-size: 2rem;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    .section-header-content h2 {{
        margin: 0; font-weight: 700; color: var(--text);
        font-size: 1.5rem; line-height: 1.2;
    }}
    
    .section-header-caption {{
        margin: 0; color: var(--text-secondary);
        font-size: 0.95rem; line-height: 1.4;
    }}
    
    /* ─── CARDS ─── */
    .card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 1.5rem;
        box-shadow: var(--shadow-resting);
        transition: all var(--transition-normal);
    }}
    
    .card:hover {{
        border-color: var(--accent-primary);
        background: var(--surface-hover);
        box-shadow: var(--shadow-card-hover);
        transform: translateY(-2px);
    }}
    
    .card-header {{
        display: flex; align-items: center; justify-content: space-between;
        margin-bottom: 1rem; padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border);
    }}
    
    .card-title {{
        margin: 0; font-size: 1rem; font-weight: 600; color: var(--text);
    }}
    
    .card-subtitle {{
        margin: 0; font-size: 0.875rem; color: var(--text-secondary);
    }}
    
    /* ─── KPI / METRIC CARDS ─── */
    .kpi-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }}
    
    .kpi-card {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        padding: 1.25rem;
        box-shadow: var(--shadow-resting);
        transition: all var(--transition-normal);
        border-left: 4px solid var(--accent-primary);
    }}
    
    .kpi-card:hover {{
        border-color: var(--accent-primary);
        background: var(--surface-hover);
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }}

    .kpi-label {{
        color: var(--text-secondary) !important;
        font-size: 0.75rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }}

    .kpi-value {{
        color: var(--text) !important;
        font-size: 2rem; font-weight: 700; line-height: 1.2;
        margin-bottom: 0.5rem;
    }}

    .kpi-delta {{
        color: var(--success) !important;
        font-size: 0.8rem; font-weight: 500;
    }}
    
    .kpi-delta.negative {{ color: var(--error); }}
    
    /* ─── STATUS BADGES ─── */
    .status-badge {{
        display: inline-flex; align-items: center; gap: 0.375rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.7rem; font-weight: 600;
        text-transform: uppercase; letter-spacing: 0.02em;
    }}
    
    .status-primary {{ background: rgba(59,130,246,0.15); color: #2563EB; }}
    .status-fallback {{ background: rgba(99,102,241,0.15); color: #6366F1; }}
    .status-error {{ background: rgba(239,68,68,0.15); color: #EF4444; }}
    .status-warning {{ background: rgba(245,158,11,0.15); color: #D97706; }}
    .status-success {{ background: rgba(16,185,129,0.15); color: #059669; }}
    .status-neutral {{ background: var(--border); color: var(--text-secondary); }}
    
    /* ─── MODEL BADGE ─── */
    .model-badge {{
        display: inline-block;
        background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
        color: white;
        border-radius: 6px;
        padding: 3px 10px;
        font-size: 0.7rem; font-weight: 600;
        margin-left: 8px;
    }}
    
    /* ─── STATUS BAR ─── */
    .status-bar {{
        display: flex; align-items: center; gap: 12px;
        padding: 10px 14px;
        background: var(--surface-secondary);
        border-radius: 10px;
        margin-bottom: 1rem;
    }}
    
    /* ─── CHAT CONTAINER ─── */
    .chat-container {{
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-xl);
        box-shadow: var(--shadow-card);
    }}
    
    /* ─── INPUT STYLING ─── */
    .stChatInput > div {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 12px !important;
    }}
    
    .stChatInput input {{
        color: var(--text) !important;
    }}
    
    /* ─── EXPANDER (modern selectors) ─── */
    [data-testid="stExpander"] {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden;
    }}
    [data-testid="stExpander"] summary {{
        background: var(--surface-secondary) !important;
        border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
        font-weight: 600 !important;
        border-bottom: 1px solid var(--border) !important;
        padding: 0.75rem 1rem !important;
        color: var(--text) !important;
    }}
    [data-testid="stExpander"][open] summary {{
        border-radius: var(--radius-md) var(--radius-md) 0 0 !important;
    }}
    [data-testid="stExpanderDetails"] {{
        background: var(--surface) !important;
        padding: 1rem !important;
        color: var(--text) !important;
    }}
    
    /* ─── BUTTONS ─── */
    .stButton > button {{
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all var(--transition-fast) !important;
    }}
    
    .stButton > button[kind="primary"] {{
        background: #2563EB !important;
        border: none !important;
        color: white !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        background: #1D4ED8 !important;
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.35) !important;
        transform: translateY(-1px) !important;
    }}
    
    .stButton > button[kind="secondary"] {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }}
    
    .stButton > button[kind="secondary"]:hover {{
        border-color: var(--accent-primary) !important;
        background: var(--surface-secondary) !important;
    }}
    
    /* ─── SELECTBOX / MULTISELECT ─── */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
    }}
    
    /* ─── DIVIDER ─── */
    hr {{
        border-color: var(--border) !important;
        margin: 1.5rem 0 !important;
    }}
    
    /* ─── SCROLLBAR ─── */
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-track {{ background: var(--surface-secondary); }}
    ::-webkit-scrollbar-thumb {{
        background: var(--border);
        border-radius: 4px;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: var(--text-muted); }}
    
    /* ─── ALERTS ─── */
    .stAlert {{
        border-radius: 12px !important;
    }}

    /* ─── TABS (nested chart tabs etc.) — blue underline, never section-colored ─── */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
        background: transparent;
        padding: 2px 0;
        border-bottom: 1px solid var(--border);
    }}
    .stTabs [data-baseweb="tab"] {{
        background: transparent !important;
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        padding: 0.5rem 1rem !important;
        white-space: nowrap !important;
        transition: all 0.2s ease !important;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        color: var(--text) !important;
    }}
    .stTabs [aria-selected="true"] {{
        background: transparent !important;
        color: #2563EB !important;
        box-shadow: inset 0 -3px 0 #2563EB !important;
    }}
    /* tab panel (content area) — ensure dark background in dark mode */
    .stTabs [data-baseweb="tab-panel"] {{
        background: var(--bg) !important;
        color: var(--text) !important;
        padding-top: 1rem;
    }}
    /* kill the default moving highlight bar (it used theme primaryColor) */
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    
    /* ─── DROPDOWN / POPOVER (selectbox, multiselect menus) ─── */
    [data-baseweb="popover"] {{
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-card) !important;
    }}
    [data-baseweb="popover"] [role="listbox"] {{
        background: var(--surface) !important;
    }}
    [data-baseweb="popover"] [role="option"] {{
        background: var(--surface) !important;
        color: var(--text) !important;
        padding: 0.5rem 1rem !important;
    }}
    [data-baseweb="popover"] [role="option"]:hover,
    [data-baseweb="popover"] [role="option"][aria-selected="true"] {{
        background: var(--surface-secondary) !important;
        color: var(--text) !important;
    }}

    /* ─── RESPONSIVE ─── */
    @media (max-width: 768px) {{
        .global-nav-links {{ display: none; }}
        .page-container {{ padding-left: 1rem; padding-right: 1rem; }}
        .kpi-grid {{ grid-template-columns: 1fr 1fr; }}
        h1 {{ font-size: 2rem; }}
        h2 {{ font-size: 1.5rem; }}
    }}
    
    @media (max-width: 480px) {{
        .kpi-grid {{ grid-template-columns: 1fr; }}
    }}
    </style>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════
# 11. COMPONENT RENDERERS — Reusable UI primitives
# ═══════════════════════════════════════════════════════════════

# Page registry — single source of truth for navigation
PAGES: List[Dict[str, str]] = [
    {"key": "overview",  "emoji": "🌍", "label": "Overview",  "tagline": "Global data, intelligence and visualization"},
    {"key": "news",      "emoji": "📰", "label": "News",      "tagline": "Live global headlines"},
    {"key": "weather",   "emoji": "⛅", "label": "Weather",   "tagline": "Conditions, forecast and air quality"},
    {"key": "nasa",      "emoji": "🚀", "label": "NASA",      "tagline": "Astronomy picture of the day"},
    {"key": "internet",  "emoji": "🌐", "label": "Internet",  "tagline": "Global connectivity metrics"},
    {"key": "ai_model",  "emoji": "🤖", "label": "AI Models", "tagline": "LLM arena rankings and analysis"},
    {"key": "ghi",       "emoji": "😊", "label": "Happiness", "tagline": "World Happiness Report"},
    {"key": "assistant", "emoji": "💬", "label": "Assistant", "tagline": "RAG-powered Q&A"},
]

_PAGE_KEY_BY_LABEL = {f"{p['emoji']} {p['label']}": p["key"] for p in PAGES}


def get_active_page(default: str = "overview") -> str:
    """Return the page key currently selected in the top navigation."""
    sel = st.session_state.get("pg_nav")
    return _PAGE_KEY_BY_LABEL.get(sel, default)


def go_to_page(key: str) -> None:
    """Queue navigation to another page (call inside a button handler)."""
    page = next((p for p in PAGES if p["key"] == key), None)
    if page:
        st.session_state["pending_page"] = page["key"]
        st.rerun()


def consume_pending_page() -> None:
    """Apply queued navigation before the nav widget is created."""
    pending = st.session_state.pop("pending_page", None)
    if pending:
        page = next((p for p in PAGES if p["key"] == pending), None)
        if page:
            st.session_state["pg_nav"] = f"{page['emoji']} {page['label']}"


def render_top_nav() -> str:
    """Render brand row + segmented top navigation.

    Returns the active page key ("overview", "news", ...).
    """
    # Brand row only (no theme toggle)
    st.markdown(
        '<div class="pg-brand">🌍 PROJECT&nbsp;GLOBAL</div>',
        unsafe_allow_html=True,
    )

    # Segmented control navigation — active item highlighted natively
    options = list(_PAGE_KEY_BY_LABEL.keys())
    st.session_state.setdefault("pg_nav", options[0])
    selected = st.segmented_control(
        "Navigation",
        options,
        selection_mode="single",
        key="pg_nav",
        label_visibility="collapsed",
        width="stretch",
    )

    return _PAGE_KEY_BY_LABEL.get(selected or "", "overview")


def inject_polish_css() -> None:
    """Extra polish styles for brand, navigation and hero elements."""
    st.markdown("""
    <style>
    /* ─── APP BACKGROUND (theme-aware, works without config.toml change) ─── */
    .stApp, body, [data-testid="stAppViewContainer"] {
        background: var(--bg) !important;
        color: var(--text);
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    section[data-testid="stMain"], section[data-testid="stMain"] > div {
        background: transparent;
    }

    /* ─── NATIVE CONTAINERS ─── */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: var(--surface);
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-md);
    }

/* ─── NATIVE COMPONENT OVERRIDES (follow session theme) ─── */
    [data-testid="stMain"] [data-testid="stMetricValue"],
    [data-testid="stMain"] [data-testid="stMetricDelta"],
    [data-testid="stMain"] [data-baseweb="select"] *,
    [data-testid="stMain"] [data-baseweb="input"] *,
    [data-testid="stMain"] [data-testid="stWidgetLabel"] p,
    [data-testid="stMain"] [data-testid="stMarkdownContainer"],
    [data-testid="stMain"] [data-testid="stChatMessage"],
    [data-testid="stMain"] [data-testid="stText"],
    [data-testid="stMain"] [data-testid="stHeader"] * {
        color: var(--text) !important;
    }
    [data-testid="stMain"] [data-testid="stMetricLabel"] p {
        color: var(--text-secondary) !important;
    }
    [data-testid="stMain"] [data-testid="stCaptionContainer"],
    [data-testid="stMain"] [data-testid="stMarkdownContainer"] caption {
        color: var(--text-secondary) !important;
    }
    [data-testid="stMain"] [data-baseweb="select"] > div,
    [data-testid="stMain"] [data-baseweb="input"],
    [data-testid="stMain"] [data-testid="stChatInput"] > div,
    [data-testid="stMain"] [data-testid="stChatInput"] textarea {
        background: var(--surface) !important;
        border-color: var(--border) !important;
        color: var(--text) !important;
    }
    [data-testid="stMain"] [data-testid="stChatInput"] textarea::placeholder {
        color: var(--text-muted) !important;
    }
    /* st.info/success/warning/error: let Streamlit's own paired
       background+text colors win. The blanket stMarkdownContainer rule
       above also matches the text inside these alerts and was forcing
       our --text (near-white in dark mode) onto config.toml's semantic
       alert backgrounds, which only have light-mode-appropriate colors
       defined (see config.toml — add [theme.dark] variants for
       redBackgroundColor/redTextColor etc. to fix the background half
       of this). This selector is more specific than the blanket rule
       above so it wins even though both use !important. */
    [data-testid="stMain"] .stAlert [data-testid="stMarkdownContainer"],
    [data-testid="stMain"] .stAlert [data-testid="stMarkdownContainer"] p {
        color: revert !important;
    }

    /* ─── BRAND ─── */
    .pg-brand {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: var(--accent-gradient);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent !important;
        padding: 0.3rem 0;
    }

    /* ─── SEGMENTED NAV ─── */
    div[data-baseweb="segmented-control"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 4px;
        box-shadow: var(--shadow-card);
        margin-bottom: 1rem;
    }
    div[data-baseweb="segmented-control"] button {
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        transition: all var(--transition-fast) !important;
    }
    div[data-baseweb="segmented-control"] button[aria-checked="true"] {
        background: transparent !important;
        color: #2563EB !important;
        box-shadow: inset 0 -3px 0 #2563EB !important;
    }
    div[data-baseweb="segmented-control"] button[aria-checked="false"]:hover {
        background: var(--surface-secondary) !important;
    }

    /* ─── HERO ─── */
    .pg-hero {
        background: var(--accent-gradient);
        border-radius: var(--radius-lg);
        padding: 2rem 2.4rem;
        color: #fff;
        margin-bottom: 1.4rem;
        position: relative;
        overflow: hidden;
    }
    .pg-hero h1 {
        margin: 0;
        font-size: clamp(1.7rem, 3.2vw, 2.6rem);
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    .pg-hero p {
        margin: 0.45rem 0 0;
        opacity: 1;
        font-size: 1.02rem;
        max-width: 46rem;
        text-shadow: 0 1px 3px rgba(15, 23, 42, 0.35);
    }
    .pg-hero .pg-hero-glow {
        position: absolute;
        right: -70px;
        top: -70px;
        width: 240px;
        height: 240px;
        border-radius: 50%;
        background: rgba(255,255,255,0.14);
        filter: blur(8px);
    }
    /* hero text must stay white on the gradient (defeat global text rule) */
    .pg-hero h1, .pg-hero p, .pg-hero span {
        color: #fff !important;
        text-shadow: 0 1px 3px rgba(15, 23, 42, 0.35);
    }

    /* ─── SECTION LINK CARDS ─── */
    .pg-link-card {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 4px solid var(--card-accent, var(--accent-primary));
        border-radius: var(--radius-md);
        padding: 0.9rem 1rem;
        height: 100%;
        transition: transform var(--transition-fast), box-shadow var(--transition-fast);
    }
    .pg-link-card:hover {
        transform: translateY(-2px);
        background: var(--surface-hover);
        box-shadow: var(--shadow-card-hover);
    }
    .pg-link-card .pg-link-title {
        font-weight: 700;
        color: var(--text) !important;
        font-size: 1rem;
    }
    .pg-link-card .pg-link-desc {
        color: var(--text-secondary) !important;
        font-size: 0.82rem;
        line-height: 1.45;
    }

    /* ─── KPI CARDS TINT ─── */
    .kpi-card {
        position: relative;
        overflow: hidden;
    }
    .kpi-card::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(135deg, var(--accent-primary) 0%, transparent 65%);
        opacity: 0.06;
        pointer-events: none;
    }

    /* ─── HIDE SIDEBAR COMPLETELY ─── */
    [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"] {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)


def get_page(key: str) -> Dict[str, str]:
    """Get page registry entry by key."""
    return next((p for p in PAGES if p["key"] == key), PAGES[0])


def render_page_container() -> None:
    """Render the main page content container (below fixed nav)."""
    st.markdown('<div class="page-container">', unsafe_allow_html=True)


def close_page_container() -> None:
    """Close the page container."""
    st.markdown('</div>', unsafe_allow_html=True)


def render_section_header(
    section_key: str,
    caption: str = "",
    action: Optional[Dict[str, Any]] = None
) -> None:
    """Render a styled section header with icon, title, caption, and optional action."""
    section = get_section_theme(section_key)
    
    action_html = ""
    if action:
        action_html = f'''
        <a href="{action.get('href', '#')}" 
           class="stButton" style="margin-left: auto; text-decoration: none;">
            {action.get('label', 'Action')}
        </a>
        '''
    
    st.markdown(f"""
    <div class="section-header">
        <span class="section-header-icon material-symbols-outlined">{section['icon']}</span>
        <div class="section-header-content">
            <h2>{section['name']}</h2>
            {f'<p class="section-header-caption">{caption}</p>' if caption else ''}
        </div>
        {action_html}
    </div>
    """, unsafe_allow_html=True)


def render_kpi_row(metrics: List[Dict[str, Any]]) -> None:
    """Render a row of KPI metric cards."""
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            delta_html = ""
            if m.get("delta"):
                delta_class = " negative" if m.get("negative") else ""
                delta_html = f'<div class="kpi-delta{delta_class}">{m["delta"]}</div>'
            
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{m['label']}</div>
                <div class="kpi-value">{m['value']}</div>
                {delta_html}
            </div>
            """, unsafe_allow_html=True)


def render_kpi_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    negative: bool = False,
    accent: Optional[str] = None
) -> None:
    """Render a single KPI metric card."""
    border_color = accent or "var(--accent-primary)"
    delta_html = ""
    if delta:
        delta_class = " negative" if negative else ""
        delta_html = f'<div class="kpi-delta{delta_class}">{delta}</div>'
    
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: {border_color};">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_status_badge(
    status: Literal["primary", "fallback", "error", "warning", "success", "neutral"],
    label: str,
    icon: str = ""
) -> None:
    """Render a status badge."""
    icon_html = f'<span class="material-symbols-outlined" style="font-size:0.7rem;">{icon}</span>' if icon else ""
    st.markdown(f'''
    <span class="status-badge status-{status}">
        {icon_html}{label}
    </span>
    ''', unsafe_allow_html=True)


def render_model_badge(model_name: str, section_key: str = "assistant") -> None:
    """Render a model attribution badge."""
    theme = get_section_theme(section_key)
    st.markdown(f'''
    <span class="model-badge" style="background: linear-gradient(135deg, {theme['primary']}, {theme['secondary']});">
        {model_name}
    </span>
    ''', unsafe_allow_html=True)


def render_status_bar(
    active_backend: str,
    current_model: str,
    section_key: str = "assistant"
) -> None:
    """Render the connection status bar."""
    theme = get_section_theme(section_key)
    
    status_map = {
        "gemini": ("🟢 Primary", "status-primary", "Gemini Active"),
        "openrouter": ("🔄 Fallback", "status-fallback", "OpenRouter Active"),
        "cohere": ("🔄 Fallback", "status-fallback", "Cohere Active"),
        "none": ("⚪ No Backend", "status-error", "Check API Keys"),
    }
    label, css_class, tooltip = status_map.get(active_backend, ("⚪ Unknown", "status-error", ""))
    
    st.markdown(f"""
    <div class="status-bar">
        <span class="status-badge {css_class}">{label}</span>
        <span style="color: var(--text-secondary); font-size: 0.85rem;">{current_model}</span>
        <span style="margin-left: auto; color: var(--text-muted); font-size: 0.75rem;">{tooltip}</span>
    </div>
    """, unsafe_allow_html=True)


def render_card(
    content: str,
    title: str = "",
    subtitle: str = "",
    accent: Optional[str] = None,
    action: Optional[Dict[str, Any]] = None
) -> None:
    """Render a styled card container."""
    border_left = f"border-left: 4px solid {accent};" if accent else ""
    action_html = ""
    if action:
        action_html = f'''
        <a href="{action.get('href', '#')}" 
           style="margin-left: auto; text-decoration: none; color: var(--accent-primary); font-weight: 600;">
            {action.get('label', 'Action')}
        </a>
        '''
    
    header_html = ""
    if title:
        header_html = f"""
        <div class="card-header">
            <div>
                <div class="card-title">{title}</div>
                {f'<div class="card-subtitle">{subtitle}</div>' if subtitle else ''}
            </div>
            {action_html}
        </div>
        """
    
    st.markdown(f"""
    <div class="card" style="{border_left}">
        {header_html}
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_chart_container(
    fig: go.Figure,
    height: int = 450,
    show_legend: bool = True,
    section_key: str = "home"
) -> go.Figure:
    """Apply theme-aware styling to a Plotly figure."""
    return style_plotly(fig, height=height, show_legend=show_legend, section_key=section_key)


# ════════════════════════════════════════════════════════════════
# 12. PLOTLY THEME STYLING
# ═══════════════════════════════════════════════════════════════

def get_plotly_template() -> Dict:
    """Get theme-aware Plotly template."""
    dark = is_dark()
    base = get_base_colors()
    
    return {
        "layout": {
            "font": {"family": TYPOGRAPHY["font_family"], "color": base["text_primary"]},
            "paper_bgcolor": base["background"],
            "plot_bgcolor": base["background"],
            "title": {
                "font": {"size": 16, "color": base["text_primary"], "family": TYPOGRAPHY["font_family"]},
                "x": 0.5, "xanchor": "center",
            },
            "xaxis": {
                "gridcolor": base["grid"],
                "zerolinecolor": base["border"],
                "linecolor": base["border"],
                "tickfont": {"color": base["text_secondary"], "size": 11},
                "title": {"font": {"color": base["text_primary"], "size": 12}},
            },
            "yaxis": {
                "gridcolor": base["grid"],
                "zerolinecolor": base["border"],
                "linecolor": base["border"],
                "tickfont": {"color": base["text_secondary"], "size": 11},
                "title": {"font": {"color": base["text_primary"], "size": 12}},
            },
            "legend": {
                "bgcolor": "rgba(0,0,0,0)",
                "font": {"color": base["text_primary"], "size": 11},
                "bordercolor": base["border"],
                "borderwidth": 1,
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
            "colorway": CATEGORICAL,
            "hoverlabel": {
                "bgcolor": base["surface"],
                "font": {"color": base["text_primary"], "size": 12},
                "bordercolor": base["border"],
            },
            "margin": {"l": 60, "r": 30, "t": 60, "b": 50},
            "hovermode": "x unified",
        }
    }


def style_plotly(
    fig: go.Figure,
    height: int = 450,
    show_legend: bool = True,
    section_key: str = "home",
    tab_key: Optional[str] = None
) -> go.Figure:
    """Apply theme-aware styling to a Plotly figure.

    ``tab_key`` is kept as a deprecated alias for ``section_key``.
    """
    if tab_key is not None:
        section_key = tab_key
    base = get_base_colors()
    dark = is_dark()
    
    # Use border color without alpha for Plotly
    legend_border = base["border"]
    if legend_border.startswith("#") and len(legend_border) == 9:
        legend_border = legend_border[:7]
    
    fig.update_layout(
        template="plotly_white" if not dark else "plotly_dark",
        height=height,
        showlegend=show_legend,
        font={"family": TYPOGRAPHY["font_family"], "color": base["text_primary"]},
        paper_bgcolor=base["background"],
        plot_bgcolor=base["background"],
        margin={"l": 60, "r": 30, "t": 60, "b": 50},
        hovermode="x unified",
        legend={
            "bgcolor": "rgba(0,0,0,0)",
            "font": {"color": base["text_primary"], "size": 11},
            "bordercolor": legend_border,
            "borderwidth": 1,
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.02,
            "xanchor": "right",
            "x": 1,
        },
    )
    
    fig.update_xaxes(
        gridcolor=base["grid"],
        zerolinecolor=base["border"],
        linecolor=base["border"],
        tickfont={"color": base["text_secondary"], "size": 11},
        title_font={"color": base["text_primary"], "size": 12},
    )
    fig.update_yaxes(
        gridcolor=base["grid"],
        zerolinecolor=base["border"],
        linecolor=base["border"],
        tickfont={"color": base["text_secondary"], "size": 11},
        title_font={"color": base["text_primary"], "size": 12},
    )
    
    return fig





# ════════════════════════════════════════════════════════════════
# 14. UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_weather_color(condition: str) -> str:
    """Get color for weather condition."""
    condition = condition.lower()
    for key, color in WEATHER_COLORS.items():
        if key in condition:
            return color
    return WEATHER_COLORS["default"]


def get_aqi_color(aqi: int) -> str:
    """Get color for AQI value (1-5)."""
    return AQI_COLORS.get(aqi, AQI_COLORS[1])


def format_number(value: float, decimals: int = 1) -> str:
    """Format number with appropriate separators."""
    if value >= 1_000_000:
        return f"{value/1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"{value/1_000:.{decimals}f}K"
    return f"{value:,.{decimals}f}"


# ════════════════════════════════════════════════════════════════
# 15. EXPORTS — All public functions
# ═══════════════════════════════════════════════════════════════

__all__ = [
    # Theme detection
    "is_dark",
    "get_base_colors",
    "get_section_theme",
    "get_css_variables",
    
    # CSS injection
    "inject_theme_css",
    
    # Layout
    "render_top_nav",
    "inject_polish_css",
    "get_page",
    "get_active_page",
    "go_to_page",
    "consume_pending_page",
    "PAGES",
    "render_page_container",
    "close_page_container",
    "render_section_header",
    
    # Components
    "render_kpi_row",
    "render_kpi_card",
    "render_status_badge",
    "render_model_badge",
    "render_status_bar",
    "render_card",
    "render_chart_container",
    
    # Plotly
    "get_plotly_template",
    "style_plotly",
    
    # Colors
    "get_weather_color",
    "get_aqi_color",
    
    # Constants
    "LIGHT_BASE",
    "SECTION_ACCENTS", "SEMANTIC", "CATEGORICAL",
    "WEATHER_COLORS", "AQI_COLORS",
    "TYPOGRAPHY", "SPACING", "RADIUS", "SHADOWS_LIGHT", "SHADOWS_DARK",
    "TRANSITIONS", "Z_INDEX", "BREAKPOINTS",
]