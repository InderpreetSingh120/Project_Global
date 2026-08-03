import streamlit as st
from API.NASA import get_apod
from API.News import get_news, search_query
from API.Weather import (
    geocode_location,
    get_current_weather,
    get_forecast,
    create_forecast_chart,
    get_air_quality,
    get_air_quality_forecast,
    create_aqi_forecast_chart,
)
from API.SpeedTest import (
    run_speedtest,
    get_connection_rating,
    get_overall_score,
    create_speed_gauge_figure,
    create_download_comparison_figure,
    create_speed_radar_figure,
    create_speed_history_figure,
)

# ── Page Configuration ──
st.set_page_config(
    page_title="Project Global",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Load Data ──
# get_apod() and get_news() are already @st.cache_data'd inside NASA.py / News.py
# (24h TTL) — no need to wrap them again here.
nasadata = get_apod()
newsdata = get_news()

# ── Init session state ──
if "speed_history" not in st.session_state:
    st.session_state.speed_history = []
if "geo_results" not in st.session_state:
    st.session_state.geo_results = []
if "selected_location" not in st.session_state:
    st.session_state.selected_location = None
if "last_weather_query" not in st.session_state:
    st.session_state.last_weather_query = None

# ── Sidebar ──
with st.sidebar:
    st.title("🌍 Project Global")
    st.caption("A comprehensive dashboard for weather, news, space, and speed testing.")
    st.divider()
    st.subheader("Navigation")
    st.write("• 🏠 Home — Overview")
    st.write("• 📰 News — Latest headlines & search")
    st.write("• 🌤️ Weather & AQI — Current conditions & forecasts")
    st.write("• 🚀 Speed Test — Internet speed analysis")
    st.write("• 🪐 NASA — Astronomy Picture of the Day")
    st.divider()
    st.caption("Built with Streamlit & Plotly")

# ── Tabs ──
st.title("Project Global")
Home, News_tab, weather, speedtest_tab, nasa = st.tabs(
    ["🏠 Home", "📰 News", "🌤️ Weather & AQI", "🚀 Speed Test", "🪐 NASA"]
)

# ═══════════════════════════════════════════
#  HOME
# ═══════════════════════════════════════════
with Home:
    st.header("Welcome to the Global Project!")
    st.write(
        "This dashboard provides a comprehensive overview of various data sources "
        "including live news, weather with air quality, internet speed testing, "
        "and NASA's Astronomy Picture of the Day."
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("News", "Live", "Latest headlines")
    col2.metric("Weather", "Real-time", "With AQI data")
    col3.metric("Speed Test", "Network", "Performance metrics")
    col4.metric("NASA", "APOD", "Daily astronomy")
    col5.metric("Search", "Global", "Multi-source")

    st.divider()
    st.subheader("Quick Start")
    st.write("Use the sidebar to navigate. Try the **Speed Test** tab to check "
             "your connection, or explore **NASA** for today's astronomy picture.")

# ═══════════════════════════════════════════
#  NEWS
# ═══════════════════════════════════════════
with News_tab:
    st.header("📰 News")

    query = st.text_input(
        "🔍 Search for news articles:",
        key="search_input",
        placeholder="Enter keywords...",
    )

    if query:
        st.subheader(f"Search Results for: *{query}*")
        try:
            search_result = search_query(query)
            articles = search_result.get("articles", []) if search_result else []

            if articles:
                for article in articles:
                    with st.container():
                        st.subheader(article.get("title", "Untitled"))
                        st.write(article.get("description", "No description available."))
                        url = article.get("url", "#")
                        st.write(f"[🔗 Read full article]({url})")
                        st.divider()
            else:
                st.info("No search results found. Try different keywords.")
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
    else:
        st.subheader("Top Headlines")
        if newsdata:
            articles = newsdata.get("articles", [])
            if articles:
                for article in articles[:10]:  # Show top 10
                    with st.container():
                        st.subheader(article.get("title", "Untitled"))
                        st.write(article.get("description", "No description available."))
                        url = article.get("url", "#")
                        st.write(f"[🔗 Read full article]({url})")
                        st.divider()
            else:
                st.warning("No articles available at the moment.")
        else:
            st.error("Couldn't retrieve news headlines right now.")

# ═══════════════════════════════════════════
#  WEATHER & AQI
# ═══════════════════════════════════════════
with weather:
    st.header("🌤️ Weather & Air Quality")

    city_query = st.text_input(
        "📍 Enter city or location name:",
        key="weather_search",
        placeholder="e.g., London, Tokyo...",
    )

    # ── Geocode on new query (button-triggered) ──
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
        st.warning("No locations found for that query. Please try a different name.")

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
            label = (
                f"{', '.join(p for p in parts if p)}  "
                f"({place.get('lat'):.2f}, {place.get('lon'):.2f})"
            )
            with cols[col_idx]:
                if st.button(label, key=f"loc_{i}", use_container_width=True):
                    st.session_state.selected_location = place
                    st.rerun()

    selected = st.session_state.get("selected_location")
    if selected:
        st.divider()
        lat, lon = selected["lat"], selected["lon"]
        location_name = selected.get("name", "Unknown")
        country = selected.get("country", "")

        st.subheader(f"📍 {location_name}, {country}")

        with st.spinner("Fetching weather data..."):
            try:
                current = get_current_weather(lat, lon)

                if current:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("🌡️ Temperature", f"{current['main']['temp']:.1f} °C")
                    col2.metric("🤗 Feels Like", f"{current['main']['feels_like']:.1f} °C")
                    col3.metric("💧 Humidity", f"{current['main']['humidity']}%")
                    col4.metric("💨 Wind", f"{current['wind']['speed']} m/s")
                    st.caption(
                        f"Conditions: {current['weather'][0]['description'].capitalize()}"
                    )

                    # ── Forecast ──
                    forecast = get_forecast(lat, lon)
                    if forecast:
                        st.divider()
                        st.subheader("📅 5-Day Forecast")
                        fig1 = create_forecast_chart(forecast)
                        if fig1:
                            st.plotly_chart(fig1, use_container_width=True)

                    # ── Air Quality ──
                    st.divider()
                    st.subheader("🌬️ Air Quality Index")

                    aqi_data = get_air_quality(lat, lon)
                    if aqi_data and aqi_data.get("list"):
                        current_aqi_entry = aqi_data["list"][0]
                        aqi_value = current_aqi_entry.get("main", {}).get("aqi", 0)
                        aqi_label = {
                            1: "Good",
                            2: "Fair",
                            3: "Moderate",
                            4: "Poor",
                            5: "Very Poor",
                        }.get(aqi_value, "Unknown")
                        aqi_emoji = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴", 5: "🟣"}

                        st.markdown(
                            f"**{aqi_emoji.get(aqi_value, '')} Current AQI: {aqi_value}** "
                            f"— *{aqi_label}*"
                        )

                        components = current_aqi_entry.get("components", {})
                        if components:
                            c1, c2, c3 = st.columns(3)
                            c1.metric("PM2.5", f"{components.get('pm2_5', 0):.1f} µg/m³")
                            c2.metric("PM10", f"{components.get('pm10', 0):.1f} µg/m³")
                            c3.metric("O₃", f"{components.get('o3', 0):.1f} µg/m³")

                            c4, c5, c6 = st.columns(3)
                            c4.metric("NO₂", f"{components.get('no2', 0):.1f} µg/m³")
                            c5.metric("SO₂", f"{components.get('so2', 0):.1f} µg/m³")
                            c6.metric("CO", f"{components.get('co', 0):.2f} µg/m³")

                        # ── AQI Forecast ──
                        aqi_fc = get_air_quality_forecast(lat, lon)
                        if aqi_fc:
                            st.divider()
                            st.subheader("📅 AQI Forecast")
                            aqi_fig = create_aqi_forecast_chart(aqi_fc)
                            if aqi_fig:
                                st.plotly_chart(aqi_fig, use_container_width=True)
                    else:
                        st.warning(
                            "Air quality data not available for this location."
                        )

            except Exception as e:
                st.error(f"Failed to fetch weather data: {str(e)}")
                st.info("Please check your WEATHER_KEY and internet connection.")

# ═══════════════════════════════════════════
#  SPEED TEST
# ═══════════════════════════════════════════
with speedtest_tab:
    st.header("🚀 Speed Test")
    st.write("Test your internet speed and see how your connection stacks up.")

    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        run_test = st.button(
            "🚀 Start Speed Test",
            key="start_speedtest",
            type="primary",
            use_container_width=True,
        )
    with col_info:
        history = st.session_state.speed_history
        if history:
            last = history[-1]
            st.write(
                f"**Tests run:** {len(history)} | "
                f"Last: {last['download_mbps']} Mbps ↓ / "
                f"{last['upload_mbps']} Mbps ↑ / "
                f"{last['ping_ms']} ms ping"
            )

    if run_test:
        with st.spinner("Testing your connection... This may take a moment."):
            try:
                results = run_speedtest()

                # Save to history
                st.session_state.speed_history.append(results)

                # ── Rating Badge ──
                rating_text, rating_color = get_connection_rating(
                    results["download_mbps"]
                )
                overall_score = get_overall_score(results)
                score_color = (
                    "#00C853"
                    if overall_score >= 70
                    else "#FFD600"
                    if overall_score >= 40
                    else "#FF1744"
                )

                st.divider()
                st.subheader("📊 Results Summary")

                # Rating badge + overall score side by side
                col_badge, col_score = st.columns([3, 1])
                with col_badge:
                    st.markdown(
                        f"""
                        <div style="
                            background-color:{rating_color};
                            padding:20px;
                            border-radius:15px;
                            text-align:center;
                            margin-bottom:20px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                        ">
                            <h1 style="color:white; margin:0; font-size:2em;">
                                {rating_text}
                            </h1>
                            <p style="color:white; margin:4px 0 0 0; font-size:1.1em;">
                                {results['download_mbps']} Mbps down ·
                                {results['upload_mbps']} Mbps up ·
                                {results['ping_ms']} ms ping
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col_score:
                    st.metric("Overall Score", f"{overall_score}/100")

                # ── Key Metrics ──
                col1, col2, col3 = st.columns(3)
                col1.metric("⬇️ Download", f"{results['download_mbps']} Mbps")
                col2.metric("⬆️ Upload", f"{results['upload_mbps']} Mbps")
                col3.metric("🏓 Ping", f"{results['ping_ms']} ms")

                # Server info
                st.caption(
                    f"📍 Server: {results['server']} — "
                    f"{results['location']}, {results['country']}"
                )

                # ── Image Download Estimate ──
                images_per_sec = results["download_mbps"] / 16  # ~2 MB per image
                st.info(
                    f"📸 At this speed you can download roughly "
                    f"**{images_per_sec:.1f} images/sec** "
                    f"(assuming ~2 MB per image)"
                )

                # ── Gauge Chart ──
                st.divider()
                st.subheader("📈 Speed Breakdown")
                gauge_fig = create_speed_gauge_figure(results)
                st.plotly_chart(gauge_fig, use_container_width=True)

                # ── Download Time Comparison ──
                st.divider()
                st.subheader("⏱️ Download Time Estimates")
                comp_fig = create_download_comparison_figure(results["download_mbps"])
                st.plotly_chart(comp_fig, use_container_width=True)

                # ── Radar Chart ──
                st.divider()
                st.subheader("🕸️ Connection Quality Radar")
                radar_fig = create_speed_radar_figure(results)
                st.plotly_chart(radar_fig, use_container_width=True)

                # ── History Chart ──
                if len(history) > 1:
                    st.divider()
                    st.subheader("📊 Speed Test History")
                    history_fig = create_speed_history_figure(history)
                    st.plotly_chart(history_fig, use_container_width=True)

                    col_clear, _ = st.columns([1, 4])
                    with col_clear:
                        if st.button("🗑️ Clear History", key="clear_history"):
                            st.session_state.speed_history = []
                            st.rerun()

            except ImportError:
                st.error(
                    "**`speedtest-cli` is not installed.**\n\n"
                    "Run this in your terminal to install it:\n"
                    "```\npip install speedtest-cli\n```"
                )
            except ConnectionError as e:
                st.error(f"🌐 Connection Error: {str(e)}")
                st.info(
                    "Please check your internet connection and try again."
                )
            except Exception as e:
                st.error(f"⚠️ Speedtest failed: {str(e)}")
                st.info(
                    "Make sure you have a stable internet connection and try again."
                )

# ═══════════════════════════════════════════
#  NASA
# ═══════════════════════════════════════════
with nasa:
    st.header("🪐 NASA Section")
    st.write("Explore space-related content and updates from NASA.")

    if nasadata:
        st.title("🚀 NASA Astronomy Picture of the Day")
        st.subheader(f"Title: {nasadata.get('title', 'N/A')}")
        if nasadata.get("url"):
            st.image(nasadata["url"], use_container_width=True)
        st.write(f"**Date:** {nasadata.get('date', 'N/A')}")
        st.subheader("Explanation")
        st.write(nasadata.get("explanation", "No explanation available."))
    else:
        st.error("Failed to retrieve NASA data. Please check your NASA API key.")