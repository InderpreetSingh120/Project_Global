import streamlit as st
from API.NASA import get_apod
from API.News import get_news, search_query
from API.ChatBot import (
    Chatbot,
    PROJECT_INFO_PATH,
    RAG_AVAILABLE,
)
from API.Weather import (
    geocode_location,
    get_current_weather,
    get_forecast,
    create_forecast_chart,
    get_air_quality,
    get_air_quality_forecast,
    create_aqi_forecast_chart,
)

# ── Page Configuration ──
st.set_page_config(
    page_title="Project Global",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed",
)
# ── Load Data ──
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

# ── Tabs ──
st.title("Project Global")
Home, assistant_tab, News_tab, weather, nasa, internet,  ai_model, global_happiness_index = st.tabs(
    [" 🏠 Home", " 💬 Assistant", "| 📰 News", " 🌤️ Weather & AQI"," 🪐 NASA |", "| 🚀 Internet",  " 🤖 AI Models", " 😊 GHI |"]
)

# ═══════════════════════════════════════════
#  HOME
# ═══════════════════════════════════════════
with Home:
    st.title("Global Intelligence Dashboard")
    st.caption("Explore data. Connect sources. Build intelligence.")
    st.markdown("""
    This project combines multiple APIs and structured datasets into a
    unified Streamlit application. It demonstrates how different types
    of information can be collected, processed, visualized, and explored
    through one interface.
    """)

    st.divider()

    st.subheader("Project Overview")
    st.markdown("""
    The dashboard brings together live information and structured datasets
    from different sources, then applies Python-based processing and
    interactive visualization to make the information easier to explore.
    """)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Live Data")
        st.markdown("""
        **News**  
        Latest news collected through an external API.

        **Weather & Air Quality**  
        Current environmental information from external data sources.

        **NASA Astronomy**  
        Astronomy Picture of the Day and related information.
        """)

    with col2:
        st.markdown("### Datasets")
        st.markdown("""
        **Internet**  
        Global internet usage, subscriptions, and broadband metrics.

        **Global Happiness**  
        Country-level happiness and related indicators.

        **AI Models**  
        Information and comparisons across AI models.

        **Packaged Food**  
        Product and nutritional information.
        """)

    st.divider()

    st.subheader("How It Works")

    st.markdown("""
    <div style="border:1px solid rgba(128,128,128,0.25);border-radius:12px;padding:18px;text-align:center;">
        <h3>DATA SOURCES</h3>
        <p>APIs &nbsp; • &nbsp; Structured Datasets</p>
    </div>
    <div style="text-align:center;font-size:24px;">↓</div>
    <div style="border:1px solid rgba(128,128,128,0.25);border-radius:12px;padding:18px;text-align:center;">
        <h3>PROCESSING</h3>
        <p>Python &nbsp; • &nbsp; Pandas &nbsp; • &nbsp; Data Cleaning</p>
    </div>
    <div style="text-align:center;font-size:24px;">↓</div>
    <div style="border:1px solid rgba(128,128,128,0.25);border-radius:12px;padding:18px;text-align:center;">
        <h3>VISUALIZATION</h3>
        <p>Streamlit &nbsp; • &nbsp; Plotly &nbsp; • &nbsp; Interactive Charts</p>
    </div>
    <div style="text-align:center;font-size:24px;">↓</div>
    <div style="border:1px solid rgba(128,128,128,0.25);border-radius:12px;padding:18px;text-align:center;">
        <h3>AI / RAG</h3>
        <p>Nomic Embeddings &nbsp; → &nbsp; ChromaDB &nbsp; → &nbsp; LLM</p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.subheader("Technologies")

    tech_cols = st.columns(4)
    technologies = [
        ("Python", "Core programming and data processing"),
        ("Streamlit", "Interactive web application"),
        ("Pandas", "Data loading and cleaning"),
        ("Plotly", "Interactive visualization"),
    ]

    for col, (name, description) in zip(tech_cols, technologies):
        with col:
            st.markdown(f"**{name}**")
            st.caption(description)

    tech_cols = st.columns(4)
    technologies = [
        ("REST APIs", "Live external data"),
        ("Nomic Embeddings", "Semantic representation"),
        ("ChromaDB", "Vector storage and retrieval"),
        ("RAG / LLM", "Context-aware information retrieval"),
    ]

    for col, (name, description) in zip(tech_cols, technologies):
        with col:
            st.markdown(f"**{name}**")
            st.caption(description)

    st.divider()
    st.info("💬 Prefer not to read all this? Ask the **Assistant** tab instead.")
    st.divider()
    st.subheader("Project Goal")
    st.markdown("""
    The goal is not simply to display data. The project demonstrates how
    different technologies can work together to collect, process,
    visualize, retrieve, and present information from heterogeneous
    sources in one application.

    It serves as a practical showcase of Python, API integration,
    data processing, visualization, embeddings, vector databases,
    and Retrieval-Augmented Generation.
    """)


# ═══════════════════════════════════════════
#  ASSISTANT
# ═══════════════════════════════════════════
with assistant_tab:
    st.markdown("""
    <style>
    .source-badge {
        display: inline-block;
        background: rgba(100, 100, 100, 0.1);
        border-radius: 6px;
        padding: 2px 8px;
        margin: 2px;
        font-size: 0.75rem;
        color: #666;
    }
    .model-badge {
        display: inline-block;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 0.7rem;
        font-weight: 600;
        margin-left: 8px;
    }
    .status-primary { color: #10b981; }
    .status-fallback { color: #f59e0b; }
    .status-error { color: #ef4444; }
    .source-expander {
        border-top: 1px solid rgba(128,128,128,0.15);
        margin-top: 12px;
        padding-top: 12px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Header ──
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown("### 💬 AI Assistant")
        st.caption("Perplexity-style: RAG retrieval → Gemini → OpenRouter → Cohere fallback chain")
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
            if "bot" in st.session_state:
                st.session_state.bot.clear_history()
            st.rerun()
    with col3:
        if st.button("🔄 New Session", use_container_width=True, type="secondary"):
            if "bot" in st.session_state:
                st.session_state.bot.start_new_chat()
            st.rerun()

    # ── Init Session ──
    if "bot" not in st.session_state:
        st.session_state.bot = Chatbot()
        st.session_state.bot.start_new_chat()

    bot = st.session_state.bot

    # ── Status Bar ──
    active_backend = getattr(bot, "active_backend", "none")
    current_model = getattr(bot, "last_used_model", "Ready")

    status_map = {
        "gemini": ("🟢 Primary", "status-primary", "Gemini Active"),
        "openrouter": ("🔄 Fallback", "status-fallback", "OpenRouter Active"),
        "cohere": ("🔄 Fallback", "status-fallback", "Cohere Active"),
        "none": ("⚪ No Backend", "status-error", "Check API Keys"),
    }
    label, css_class, tooltip = status_map.get(active_backend, ("⚪ Unknown", "status-error", ""))
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 12px; padding: 8px 12px; 
                background: rgba(128,128,128,0.05); border-radius: 8px; margin-bottom: 16px;">
        <span class="{css_class}" style="font-weight: 600;">{label}</span>
        <span style="color: #888; font-size: 0.85rem;">{current_model}</span>
        <span style="margin-left: auto; color: #aaa; font-size: 0.75rem;">{tooltip}</span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Chat Container ──
    chat_container = st.container(height=550, border=True)

    with chat_container:
        history = bot.get_display_history()
        for turn in history:
            role = turn.get("role", "user")
            content = turn.get("content", "")
            model = turn.get("model", "")
            sources = turn.get("sources")

            with st.chat_message(role):
                st.markdown(content)

                # Model badge + sources
                if role == "assistant" and model and model not in ["System", "Error", "User"]:
                    badge_html = f'<span class="model-badge">{model}</span>'
                    if sources:
                        badge_html += " " + " ".join(
                            f'<span class="source-badge">{s.get("title", "Source")}</span>'
                            for s in sources[:3]
                        )
                        if len(sources) > 3:
                            badge_html += f' <span class="source-badge">+{len(sources)-3} more</span>'
                    st.markdown(badge_html, unsafe_allow_html=True)

                    # Expandable sources
                    if sources:
                        with st.expander("📚 Sources", expanded=False):
                            for i, src in enumerate(sources, 1):
                                st.markdown(f"""
                                **{i}. {src.get('title', 'Unknown')}**  
                                Source: `{src.get('source', 'Unknown')}`  
                                Relevance: `{1 - src.get('distance', 1):.2%}`
                                """)
                                if i < len(sources):
                                    st.divider()

    # ── Input ──
    if prompt := st.chat_input("Ask anything about Project Global...", key="assistant_chat"):
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Real-time status placeholder
                status_placeholder = st.empty()
                
                def update_status(msg: str):
                    status_placeholder.info(msg)
                
                with st.spinner(""):
                    response_text = bot.send_message(prompt, progress_callback=update_status)
                
                status_placeholder.empty()

                if response_text and response_text.strip():
                    st.markdown(response_text)
                    # Model badge
                    last_model = getattr(bot, "last_used_model", "Unknown")
                    if last_model not in ["System", "Error", "User", "Ready"]:
                        st.markdown(
                            f'<span class="model-badge">{last_model}</span>',
                            unsafe_allow_html=True
                        )
                else:
                    error_text = getattr(bot, "last_error", None) or "Empty response"
                    st.error(error_text)

        st.rerun()

    # ── Debug Panel ──
    with st.expander("⚙️ Debug & System Info", expanded=False):
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
            st.error(f"**Last Error:** {last_error}")

        try:
            with open(PROJECT_INFO_PATH, "r", encoding="utf-8") as f:
                st.download_button(
                    label="📄 Download System Instructions (MD)",
                    data=f.read(),
                    file_name="Project_Vision.md",
                    mime="text/markdown"
                )
        except FileNotFoundError:
            st.warning("Project info file not found.")

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
                if st.button(label, key=f"loc_{i}", width="stretch"):
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
                            st.plotly_chart(fig1)

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
                                st.plotly_chart(aqi_fig)
                    else:
                        st.warning(
                            "Air quality data not available for this location."
                        )

            except Exception as e:
                st.error(f"Failed to fetch weather data: {str(e)}")
                st.info("Please check your WEATHER_KEY and internet connection.")

# ═══════════════════════════════════════════
# internet dataset
# ═══════════════════════════════════════════
with internet:
    st.header("Internet Dataset")
    st.write("Explore global internet metrics including usage, subscriptions, and broadband data.")
    st.write("Source: [Kaggle — Internet Dataset](https://www.kaggle.com/code/tumpanjawat/internet-use-geo-cluster-time-series/input)")
    # ── Load Data ──
    try:
        from API.Internet_data import (
            load_internet_data,
            get_latest_year,
            get_available_years,
            create_metric_map,
            create_top_countries_chart,
            create_country_comparison,
            create_metric_trend,
        )
    except ImportError:
        st.error(
            "Could not import `internet_data` module."
        )
        st.stop()
    try:
        df = load_internet_data()
    except FileNotFoundError:
        st.error(
            "Internet dataset not found.\n\n"
            "Contact Administrator"
        )
        st.stop()
    #for other errors during data loading
    except Exception as e:
        st.error(f"Failed to load internet data: {str(e)}")
        st.stop()

    if df is None or df.empty:
        st.warning("The internet dataset is empty.")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        selected_metric = st.selectbox(
            "Select Metric",
            [
                "Internet users (%)",
                "Cellular subscriptions",
                "Number of internet users",
                "Broadband subscriptions",
            ],
        )

    with col2:
        years = get_available_years(df, selected_metric)

        if not years:
            st.error("No valid years available for this metric.")
            st.stop()

        latest_year = max(years)

        selected_year = st.selectbox(
            "Select Year",
            years,
            index=years.index(latest_year),
        )


    # ── Summary ──
    year_data = df[df["Year"] == selected_year]

    col1, col2, col3 = st.columns(3)

    with col1:
        countries = year_data["Code"].ne("").sum()
        st.metric("Countries", countries)

    with col2:
        avg_users = year_data["Internet users (%)"].mean()
        st.metric("Avg. Internet Users", f"{avg_users:.1f}%")

    with col3:
        total_users = year_data["Number of internet users"].sum()
        st.metric("Total Internet Users", f"{total_users:,.0f}")


    # ── World Map ──
    st.subheader("Global Overview")

    st.plotly_chart(
        create_metric_map(
            df,
            metric=selected_metric,
            year=selected_year,
        ),
        use_container_width=True,
    )


    # ── Top Countries ──
    st.subheader("Top Countries")

    st.plotly_chart(
        create_top_countries_chart(
            df,
            metric=selected_metric,
            year=selected_year,
            top_n=10,
        ),
        use_container_width=True,
    )


    # ── Country Analysis ──
    st.subheader("Country Analysis")

    country_options = sorted(
        df["Entity"].dropna().unique().tolist()
    )

    selected_countries = st.multiselect(
        "Select countries",
        country_options,
        default=[
            country
            for country in ["India", "United States", "China"]
            if country in country_options
        ],
    )

    if selected_countries:

        st.plotly_chart(
            create_country_comparison(
                df,
                selected_countries,
                year=selected_year,
            ),
            use_container_width=True,
        )

        st.plotly_chart(
            create_metric_trend(
                df,
                metric=selected_metric,
                countries=selected_countries,
            ),
            use_container_width=True,
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
            st.image(nasadata["url"], width="stretch")
        st.write(f"**Date:** {nasadata.get('date', 'N/A')}")
        st.subheader("Explanation")
        st.write(nasadata.get("explanation", "No explanation available."))
    else:
        st.error("Failed to retrieve NASA data. Please check your NASA API key.")
# ═══════════════════════════════════════════
#  AI MODELS
# ═══════════════════════════════════════════
with ai_model:
    st.header("🤖 AI Model Arena Rankings")
    st.write(
        "Data from the AI Model Arena, showcasing the latest rankings and "
        "performance metrics of various AI models."
    )
    st.write('Source: [Kaggle — AI Model Arena Rankings 2023–2026](https://www.kaggle.com/datasets/riyagarg0314/ai-model-arena-rankings-2023-2026)'
    )
    st.divider()

    # ── Load Data ──
    try:
        from API.ai_model import (
            load_ai_data,
            render_kpis,
            top_models,
            VRcharts,
            Votebarchart,
            firstplace,
            license_vs_rating,
            leaderboard_activity,
            rating_distribution,
            subset_distribution,
            raw_data_table,
        )
    except ImportError:
        st.error(
            "Could not import `ai_model` module."
        )
        st.stop()
    try:
        df = load_ai_data()
    except FileNotFoundError:
        st.error(
            "AI model dataset not found.\n\n"
            "Contact Administrator"
        )
        st.stop()
    #for other errors during data loading
    except Exception as e:
        st.error(f"Failed to load AI model data: {str(e)}")
        st.stop()

    if df is None or df.empty:
        st.warning("The AI model dataset is empty.")
        st.stop()

    # ── KPIs ──
    st.subheader("📊 Key Metrics")
    render_kpis(df)
    st.divider()

    # ── Top Models (Rating) ──
    top_models(df)
    st.divider()

    # ── Top Models (Votes) ──
    VRcharts(df)
    st.divider()

    # ── Organization Analysis ──
    st.subheader("🏢 Organization Analysis")
    Votebarchart(df)
    st.divider()
    firstplace(df)
    st.divider()

    # ── License Analysis ──
    license_vs_rating(df)
    st.divider()

    # ── Growth Over Time ──
    leaderboard_activity(df)
    st.divider()

    # ── Rating Distribution ──
    rating_distribution(df)
    st.divider()

    # ── Subset Distribution ──
    subset_distribution(df)
    st.divider()

    # ── Raw Data Table ──
    raw_data_table(df)

with global_happiness_index:
    st.header("Global Happiness Index")
    st.write(
        "Explore global happiness, economic, social, and quality-of-life indicators."
    )

    # ── Load Data ──
    try:
        from API.GHI import (
            load_happiness_data,
            key_metrics,
            happiness_trend,
            happiness_vs_gdp,
            happiness_vs_factor,
            country_comparison,
            global_happiness,
            raw_data_table,
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

    # ── Year Selection ──
    years = sorted(
        df["year"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    if not years:
        st.error("No valid years found in the happiness dataset.")
        st.stop()

    # Prefer 2023 as the default reference year.
    default_year = 2023 if 2023 in years else years[-1]

    selected_year = st.selectbox(
        "Select Year",
        years,
        index=years.index(default_year),
    )

    # Data for the selected year.
    selected_year_df = df[df["year"] == selected_year].copy()

    st.caption(
        f"Charts using the selected year are based on {selected_year} data."
    )

    # ── Key Metrics ──
    key_metrics(selected_year_df)

    # ── Happiness Trend by Country ──
    # Uses all years so the user can see historical change.
    happiness_trend(df)

    # ── Happiness vs GDP ──
    # Uses only the selected year.
    happiness_vs_gdp(selected_year_df)

    # ── Factors Associated with Happiness ──
    # Uses only the selected year.
    happiness_vs_factor(selected_year_df)

    # ── Country Comparison ──
    # Uses only the selected year.
    country_comparison(selected_year_df)

    # ── Global Happiness Over Time ──
    # Uses all available years.
    global_happiness(df)

    # ── Raw Data ──
    # Keep the complete dataset available.
    raw_data_table(df)