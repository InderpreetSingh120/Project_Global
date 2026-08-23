import streamlit as st

from API.NASA import get_apod
from API.News import get_news, search_query
from API.ChatBot import Chatbot, PROJECT_INFO_PATH, RAG_AVAILABLE
from API.Weather import (
    geocode_location, get_current_weather, get_forecast,
    create_forecast_chart, get_air_quality, get_air_quality_forecast,
    create_aqi_forecast_chart,
)
from API.ui import (
    consume_pending_page, get_active_page,
    inject_theme_css, inject_polish_css, render_top_nav, go_to_page,
    get_page, get_section_theme, PAGES, render_kpi_card, style_plotly,
)

# ═══════════════════════════════════════════
# Page Configuration
# ═══════════════════════════════════════════
st.set_page_config(
    page_title="Project Global",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ═══════════════════════════════════════════
# Load Data (Cached)
# ═══════════════════════════════════════════
nasadata = get_apod()
newsdata = get_news()


@st.cache_data(ttl=900, show_spinner=False)
def overview_weather(city: str = "London"):
    """Current conditions for the Overview KPI card."""
    try:
        results = geocode_location(city)
        if not results:
            return None
        place = results[0]
        current = get_current_weather(place["lat"], place["lon"])
        if not current:
            return None
        return {
            "temp": current["main"]["temp"],
            "condition": current["weather"][0]["description"].capitalize(),
            "name": place.get("name", city),
            "country": place.get("country", ""),
        }
    except Exception:
        return None


# ═══════════════════════════════════════════
# Session State
# ═══════════════════════════════════════════
if "geo_results" not in st.session_state:
    st.session_state.geo_results = []
if "selected_location" not in st.session_state:
    st.session_state.selected_location = None
if "last_weather_query" not in st.session_state:
    st.session_state.last_weather_query = None
if "speed_history" not in st.session_state:
    st.session_state.speed_history = []

# ═══════════════════════════════════════════
# Theme + Top Navigation Chrome
# ═══════════════════════════════════════════
consume_pending_page()

page = get_active_page()
inject_theme_css(page)
inject_polish_css()
render_top_nav()


def page_header(key: str) -> None:
    """Emoji section header for sub-pages."""
    p = get_page(key)
    st.markdown(f"### {p['emoji']} {p['label']}")
    st.caption(p["tagline"])
    st.space("small")


# ═══════════════════════════════════════════
# OVERVIEW  (redesigned home)
# ═══════════════════════════════════════════
def render_overview():
    st.write(st.session_state.get("theme_mode_explicit"), st.session_state.get("theme_mode"))
    try:
        st.write(st.context.theme)
    except Exception as e:
        st.write("st.context.theme failed:", e)
    st.markdown("""
    <div class="pg-hero">
        <div class="pg-hero-glow"></div>
        <span style="position:absolute; top:1.6rem; right:2rem; background:rgba(255,255,255,.18);
              padding:.3rem .85rem; border-radius:999px; font-size:.75rem; font-weight:700;
              letter-spacing:.12em;">● LIVE</span>
        <h1>🌍 PROJECT GLOBAL</h1>
        <p>Global data, intelligence and visualization — live headlines, weather & air quality,
           NASA's daily image, worldwide connectivity metrics, LLM rankings and happiness research,
           all in one dashboard.</p>
    </div>
    """, unsafe_allow_html=True)

    # KPI row — one glanceable stat per live source
    news_count = len((newsdata or {}).get("articles", []))
    w = overview_weather()
    kpis = [
        {"label": "📰 NEWS", "value": f"{news_count} stories", "delta": "Live headlines",
         "accent": "#2563EB"},
        {"label": "⛅ WEATHER",
         "value": f"{w['temp']:.0f}°C" if w else "—",
         "delta": f"{w['name']}, {w['country']}" if w else "Weather unavailable",
         "accent": "#0891B2"},
        {"label": "🚀 NASA APOD", "value": (nasadata or {}).get("date", "—"),
         "delta": (nasadata or {}).get("title", "Picture of the day")[:42],
         "accent": "#7C3AED"},
        {"label": "🌐 INTERNET", "value": "165 countries",
         "delta": "Connectivity dataset 1995–2023", "accent": "#059669"},
    ]
    cols = st.columns(len(kpis))
    for col, m in zip(cols, kpis):
        with col:
            render_kpi_card(m["label"], m["value"], delta=m["delta"], accent=m["accent"])

    st.space("large")

    # World map hero card
    try:
        from API.Internet_data import load_internet_data, create_metric_map, get_available_years

        df = load_internet_data()
        metric_options = [
            "Internet users (%)", "Cellular subscriptions",
            "Number of internet users", "Broadband subscriptions",
        ]
        sel_metric = st.selectbox("Map metric", metric_options,
                                  key="overview_map_metric", label_visibility="collapsed")
        years = get_available_years(df, sel_metric)
        latest = max(years) if years else None

        with st.container(border=True):
            col_title, col_year = st.columns([4, 1])
            with col_title:
                st.markdown(f"#### 🌍 World Map — {sel_metric}")
                st.caption("Pick a metric above · hover a country for details")
            with col_year:
                st.badge(f"📅 {latest}", color="blue")

            fig = create_metric_map(df, metric=sel_metric, year=latest)
            fig = style_plotly(fig, height=480, section_key="overview")
            st.plotly_chart(fig, width="stretch")
    except Exception as e:
        st.warning(f"World map unavailable: {e}")

    st.space("large")
    st.markdown("#### 🧭 Explore sections")

    section_pages = [p for p in PAGES if p["key"] != "overview"]
    accents = {p["key"]: get_section_theme(p["key"])["primary"] for p in section_pages}

    for row_start in range(0, len(section_pages), 4):
        row = section_pages[row_start:row_start + 4]
        cols = st.columns(4)
        for col, p in zip(cols, row):
            accent = accents[p["key"]]
            with col:
                st.markdown(f"""
                <div class="pg-link-card" style="--card-accent:{accent};">
                    <div class="pg-link-title">{p['emoji']} {p['label']}</div>
                    <div class="pg-link-desc">{p['tagline']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Open →", key=f"go_{p['key']}", width="stretch"):
                    go_to_page(p["key"])

    st.space("medium")
    st.info("Prefer asking questions? The **💬 Assistant** does RAG-powered Q&A over this whole project.",
            icon="💡")


# ═══════════════════════════════════════════
# NEWS
# ═══════════════════════════════════════════
def render_news():
    page_header("news")

    query = st.text_input("Search for news articles", key="search_input",
                          placeholder="Enter keywords...", icon="🔎")

    if query:
        st.subheader(f"🔎 Search results for: *{query}*")
        try:
            search_result = search_query(query)
            articles = search_result.get("articles", []) if search_result else []

            if articles:
                for article in articles:
                    with st.container(border=True):
                        st.markdown(f"### 📰 {article.get('title', 'Untitled')}")
                        st.caption(article.get('description', 'No description available.'))
                        st.link_button("Read full article", article.get('url', '#'),
                                       icon="🔗")
            else:
                st.info("No search results found. Try different keywords.")
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
    else:
        st.subheader("🔥 Top headlines")
        if newsdata:
            articles = newsdata.get("articles", [])
            if articles:
                for article in articles[:10]:
                    with st.container(border=True):
                        st.markdown(f"### 📰 {article.get('title', 'Untitled')}")
                        st.caption(article.get('description', 'No description available.'))
                        st.link_button("Read full article", article.get('url', '#'),
                                       icon="🔗")
            else:
                st.warning("No articles available at the moment.")
        else:
            st.error("Couldn't retrieve news headlines right now.")


# ═══════════════════════════════════════════
# WEATHER & AQI
# ═══════════════════════════════════════════
def render_weather():
    page_header("weather")

    city_query = st.text_input(
        "Enter city or location name",
        key="weather_search",
        placeholder="e.g., London, Tokyo...",
        icon="📍",
    )

    if city_query:
        query_changed = st.session_state.get("last_weather_query") != city_query
        if query_changed:
            with st.spinner("Looking up location..."):
                try:
                    st.session_state.geo_results = geocode_location(city_query)
                    st.session_state.last_weather_query = city_query
                    st.session_state.selected_location = None
                except Exception as e:
                    st.error(f"Geocoding failed: {str(e)}")
                    st.session_state.geo_results = []

    results = st.session_state.get("geo_results", [])

    if city_query and not results:
        st.warning("No locations found. Try a different name.")

    if results:
        st.write(f"Found **{len(results)}** matching location(s) — pick one:")
        n_cols = min(len(results), 3)
        cols = st.columns(n_cols)
        for i, place in enumerate(results):
            col_idx = i % n_cols
            parts = [place.get("name", "")]
            if place.get("state"):
                parts.append(place["state"])
            parts.append(place.get("country", ""))
            label = f"{', '.join(p for p in parts if p)}  ({place.get('lat'):.2f}, {place.get('lon'):.2f})"
            with cols[col_idx]:
                if st.button(label, key=f"loc_{i}", width="stretch"):
                    st.session_state.selected_location = place
                    st.rerun()

    selected = st.session_state.get("selected_location")
    if selected:
        st.space("large")
        lat, lon = selected["lat"], selected["lon"]
        location_name = selected.get("name", "Unknown")
        country = selected.get("country", "")

        st.subheader(f"📍 {location_name}, {country}")

        with st.spinner("Fetching weather data..."):
            try:
                current = get_current_weather(lat, lon)

                if current:
                    # Current Conditions - KPI Row using st.columns
                    cols = st.columns(4)
                    with cols[0]:
                        st.metric(
                            "Temperature",
                            f"{current['main']['temp']:.1f} °C",
                            f"Feels {current['main']['feels_like']:.1f}°C"
                        )
                    with cols[1]:
                        st.metric("Humidity", f"{current['main']['humidity']}%")
                    with cols[2]:
                        st.metric("Wind", f"{current['wind']['speed']} m/s")
                    with cols[3]:
                        st.metric("Condition", current['weather'][0]['description'].capitalize())

                    st.caption(f"Conditions: {current['weather'][0]['description'].capitalize()}")
                    st.space("medium")

                    # Forecast
                    forecast = get_forecast(lat, lon)
                    fig1 = create_forecast_chart(forecast)
                    if fig1:
                        style_plotly(fig1, section_key="weather")
                        st.plotly_chart(fig1, width="stretch")
                        st.space("medium")

                    # Air Quality
                    st.subheader("🌫️ Air Quality Index")

                    aqi_data = get_air_quality(lat, lon)
                    if aqi_data and aqi_data.get("list"):
                        current_aqi_entry = aqi_data["list"][0]
                        aqi_value = current_aqi_entry.get("main", {}).get("aqi", 0)
                        aqi_labels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
                        aqi_label = aqi_labels.get(aqi_value, "Unknown")
                        aqi_colors = {1: "green", 2: "orange", 3: "orange", 4: "red", 5: "red"}

                        aqi_color = aqi_colors.get(aqi_value, "gray")
                        st.badge(f"AQI {aqi_value} — {aqi_label}", color=aqi_color)
                        st.space("small")

                        components = current_aqi_entry.get("components", {})
                        if components:
                            cols = st.columns(6)
                            with cols[0]:
                                st.metric("PM2.5", f"{components.get('pm2_5', 0):.1f} µg/m³")
                            with cols[1]:
                                st.metric("PM10", f"{components.get('pm10', 0):.1f} µg/m³")
                            with cols[2]:
                                st.metric("O₃", f"{components.get('o3', 0):.1f} µg/m³")
                            with cols[3]:
                                st.metric("NO₂", f"{components.get('no2', 0):.1f} µg/m³")
                            with cols[4]:
                                st.metric("SO₂", f"{components.get('so2', 0):.1f} µg/m³")
                            with cols[5]:
                                st.metric("CO", f"{components.get('co', 0):.2f} µg/m³")

                        # AQI Forecast
                        aqi_fc = get_air_quality_forecast(lat, lon)
                        if aqi_fc:
                            st.space("medium")
                            st.subheader("📈 AQI Forecast")
                            aqi_fig = create_aqi_forecast_chart(aqi_fc)
                            if aqi_fig:
                                style_plotly(aqi_fig, section_key="weather")
                                st.plotly_chart(aqi_fig, width="stretch")
                    else:
                        st.warning("Air quality data not available for this location.")

            except Exception as e:
                st.error(f"Failed to fetch weather data: {str(e)}")
                st.info("Please check your WEATHER_KEY and internet connection.")


# ═══════════════════════════════════════════
# NASA
# ═══════════════════════════════════════════
def render_nasa():
    page_header("nasa")

    if nasadata:
        st.subheader(f"🚀 {nasadata.get('title', 'N/A')}", anchor=False)
        st.badge(f"📅 {nasadata.get('date', 'N/A')}", color="violet")
        st.space("small")

        if nasadata.get("url"):
            st.image(nasadata["url"], width="stretch")

        st.space("medium")
        with st.container(border=True, horizontal_alignment="center"):
            st.markdown("### 🔭 Explanation")
            st.markdown(nasadata.get('explanation', 'No explanation available.'))
    else:
        st.error("Failed to retrieve NASA data. Please check your NASA API key.")


# ═══════════════════════════════════════════
# INTERNET
# ═══════════════════════════════════════════
def render_internet():
    page_header("internet")

    try:
        from API.Internet_data import (
            load_internet_data, get_latest_year, get_available_years,
            create_metric_map, create_top_countries_chart,
            create_country_comparison, create_metric_trend,
        )
    except ImportError:
        st.error("Could not import `internet_data` module.")
        st.stop()

    try:
        df = load_internet_data()
    except FileNotFoundError:
        st.error("Internet dataset not found.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to load internet data: {str(e)}")
        st.stop()

    if df is None or df.empty:
        st.warning("The internet dataset is empty.")
        st.stop()

    # Controls
    col1, col2 = st.columns(2)
    with col1:
        selected_metric = st.selectbox("Select Metric", [
            "Internet users (%)", "Cellular subscriptions",
            "Number of internet users", "Broadband subscriptions",
        ])
    with col2:
        years = get_available_years(df, selected_metric)
        if not years:
            st.error("No valid years available for this metric.")
            st.stop()
        latest_year = max(years)
        selected_year = st.selectbox("Select Year", years, index=years.index(latest_year))

    # Summary KPIs
    year_data = df[df["Year"] == selected_year]
    cols = st.columns(3)
    with cols[0]:
        st.metric("🌍 Countries", str(int(year_data["Code"].ne("").sum())))
    with cols[1]:
        st.metric("📶 Avg. Internet Users", f"{year_data['Internet users (%)'].mean():.1f}%")
    with cols[2]:
        st.metric("👥 Total Internet Users", f"{year_data['Number of internet users'].sum():,.0f}")

    # World Map
    st.subheader("🌍 Global Overview")
    fig = create_metric_map(df, metric=selected_metric, year=selected_year)
    fig = style_plotly(fig, height=500, section_key="internet")
    st.plotly_chart(fig, width="stretch")

    # Top Countries
    st.subheader("🏆 Top Countries")
    fig = create_top_countries_chart(df, metric=selected_metric, year=selected_year, top_n=10)
    fig = style_plotly(fig, section_key="internet")
    st.plotly_chart(fig, width="stretch")

    # Country Analysis
    st.subheader("🔍 Country Analysis")
    country_options = sorted(df["Entity"].dropna().unique().tolist())
    selected_countries = st.multiselect("Select countries", country_options,
        default=[c for c in ["India", "United States", "China"] if c in country_options])

    if selected_countries:
        fig = create_country_comparison(df, selected_countries, year=selected_year)
        fig = style_plotly(fig, section_key="internet")
        st.plotly_chart(fig, width="stretch")

        fig = create_metric_trend(df, metric=selected_metric, countries=selected_countries)
        fig = style_plotly(fig, section_key="internet")
        st.plotly_chart(fig, width="stretch")


# ═══════════════════════════════════════════
# AI MODELS
# ═══════════════════════════════════════════
def render_ai_models():
    page_header("ai_model")

    try:
        from API.ai_model import (
            load_ai_data, render_kpis, top_models, VRcharts, Votebarchart,
            firstplace, license_vs_rating, leaderboard_activity,
            rating_distribution, subset_distribution, raw_data_table,
        )
    except ImportError:
        st.error("Could not import `ai_model` module.")
        st.stop()

    try:
        df = load_ai_data()
    except FileNotFoundError:
        st.error("AI model dataset not found.")
        st.stop()
    except Exception as e:
        st.error(f"Failed to load AI model data: {str(e)}")
        st.stop()

    if df is None or df.empty:
        st.warning("The AI model dataset is empty.")
        st.stop()

    # All visualizations use the theme system
    st.subheader("📊 Key Metrics")
    render_kpis(df)
    st.space("medium")

    top_models(df)
    st.space("medium")

    VRcharts(df)
    st.space("medium")

    st.subheader("🏢 Organization Analysis")
    Votebarchart(df)
    st.space("medium")
    firstplace(df)
    st.space("medium")

    license_vs_rating(df)
    st.space("medium")

    leaderboard_activity(df)
    st.space("medium")

    rating_distribution(df)
    st.space("medium")

    subset_distribution(df)
    st.space("medium")

    raw_data_table(df)


# ═══════════════════════════════════════════
# GLOBAL HAPPINESS INDEX
# ═══════════════════════════════════════════
def render_ghi():
    page_header("ghi")

    try:
        from API.GHI import (
            load_happiness_data, key_metrics, happiness_trend,
            happiness_vs_gdp, happiness_vs_factor, country_comparison,
            global_happiness, raw_data_table,
        )
    except ImportError:
        st.error("Could not import `GHI` module.")
        st.stop()

    try:
        df = load_happiness_data()
    except Exception as e:
        st.error(f"Failed to load happiness data: {str(e)}")
        st.stop()

    if df is None or df.empty:
        st.warning("The happiness dataset is empty.")
        st.stop()

    # Year Selection
    years = sorted(df["year"].dropna().astype(int).unique().tolist())
    if not years:
        st.error("No valid years found in the happiness dataset.")
        st.stop()

    default_year = 2023 if 2023 in years else years[-1]
    selected_year = st.selectbox("Select Year", years, index=years.index(default_year))

    selected_year_df = df[df["year"] == selected_year].copy()
    st.caption(f"Charts using the selected year are based on {selected_year} data.")

    # Key Metrics
    key_metrics(selected_year_df)
    st.space("medium")

    # Visualizations
    happiness_trend(df)
    st.space("medium")
    happiness_vs_gdp(selected_year_df)
    st.space("medium")
    happiness_vs_factor(selected_year_df)
    st.space("medium")
    country_comparison(selected_year_df)
    st.space("medium")
    global_happiness(df)
    st.space("medium")
    raw_data_table(df)


# ═══════════════════════════════════════════
# ASSISTANT
# ═══════════════════════════════════════════
def render_assistant():
    page_header("assistant")

    # Header Actions - use horizontal container
    with st.container(horizontal=True, horizontal_alignment="right"):
        if st.button("Clear chat", icon="🗑️", type="secondary"):
            if "bot" in st.session_state:
                st.session_state.bot.clear_history()
            st.rerun()
        if st.button("New session", icon="🔄", type="secondary"):
            if "bot" in st.session_state:
                st.session_state.bot.start_new_chat()
            st.rerun()

    # Init Session
    if "bot" not in st.session_state:
        st.session_state.bot = Chatbot()
        st.session_state.bot.start_new_chat()

    bot = st.session_state.bot

    # Status Bar - use badges
    active_backend = getattr(bot, "active_backend", "none")
    current_model = getattr(bot, "last_used_model", "Ready")

    status_map = {
        "gemini": ("Gemini Active", "green", "✅"),
        "openrouter": ("OpenRouter Active", "blue", "🔀"),
        "cohere": ("Cohere Active", "violet", "🔀"),
        "none": ("No Backend", "red", "❌"),
    }
    label, color, icon = status_map.get(active_backend, ("Unknown", "gray", "❓"))

    st.badge(label, icon=icon, color=color)
    st.caption(f"Model: {current_model}")
    st.space("medium")

    # Chat Container
    chat_container = st.container(height=550, border=True)

    with chat_container:
        history = bot.get_display_history()
        for turn in history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            model = turn.get("model", "")

            with st.chat_message(role):
                st.markdown(content)

                if role == "assistant" and model and model not in ["System", "Error", "User"]:
                    st.badge(model, color="violet")

    # Input
    if prompt := st.chat_input("Ask anything about Project Global...", key="assistant_chat"):
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                status_placeholder = st.empty()

                def update_status(msg: str):
                    status_placeholder.info(msg)

                with st.spinner(""):
                    response_text = bot.send_message(prompt, progress_callback=update_status)

                status_placeholder.empty()

                if response_text and response_text.strip():
                    st.markdown(response_text)
                    last_model = getattr(bot, "last_used_model", "Unknown")
                    if last_model not in ["System", "Error", "User", "Ready"]:
                        st.badge(last_model, color="violet")
                else:
                    error_text = getattr(bot, "last_error", None) or "Empty response"
                    st.error(error_text)

        st.rerun()

    # Debug Panel
    with st.expander("Debug & System Info", icon="⚙️", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Backend:** {active_backend}")
            st.write(f"**Model:** {current_model}")
            st.write(f"**State:** {getattr(bot, 'last_event', 'N/A')}")
        with col2:
            st.write(f"**History Length:** {len(bot.get_display_history())}")
            st.write(f"**Max History:** {bot.max_history}")
            st.write(f"**RAG Enabled:** {'Yes' if RAG_AVAILABLE else 'No'}")

        last_error = getattr(bot, "last_error", None)
        if last_error:
            st.error(f"Last Error: {last_error}")

        try:
            with open(PROJECT_INFO_PATH, "r", encoding="utf-8") as f:
                st.download_button(
                    label="Download System Instructions",
                    data=f.read(),
                    file_name="Project_Vision.md",
                    mime="text/markdown",
                    icon="⬇️",
                )
        except FileNotFoundError:
            st.warning("Project info file not found.")


# ═══════════════════════════════════════════
# Router
# ═══════════════════════════════════════════
ROUTES = {
    "overview": render_overview,
    "news": render_news,
    "weather": render_weather,
    "nasa": render_nasa,
    "internet": render_internet,
    "ai_model": render_ai_models,
    "ghi": render_ghi,
    "assistant": render_assistant,
}

ROUTES.get(page, render_overview)()