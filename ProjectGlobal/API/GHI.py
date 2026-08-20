import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data" / "GlobalHappienessIndex.csv"

@st.cache_data
def load_happiness_data() -> pd.DataFrame:
    """Load and clean the World Happiness dataset."""
    if not DATA_PATH.exists():
        st.error(f"Data file missing at {DATA_PATH}")
        return pd.DataFrame()

    df = pd.read_csv(DATA_PATH)

    numeric_columns = [
        "Life Ladder", "Log GDP per capita", "Social support",
        "Healthy life expectancy at birth", "Freedom to make life choices",
        "Generosity", "Perceptions of corruption",
        "Positive affect", "Negative affect",
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")

    return df


# ─── KPIs ────────────────────────────────────────────────

def key_metrics(df):
    latest_year = df["year"].max()
    latest_data = df[df["year"] == latest_year]

    st.subheader(f"Key Metrics — {latest_year}")
    col1, col2, col3, col4, col5 = st.columns(5)

    metrics = [
        ("Life Ladder", "Life Ladder", 2),
        ("Log GDP per Capita", "Log GDP per capita", 2),
        ("Social Support", "Social support", 2),
        ("Healthy Life Expectancy", "Healthy life expectancy at birth", 1),
        ("Freedom", "Freedom to make life choices", 2),
    ]

    for col, (label, field, decimals) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            val = latest_data[field].mean()
            fmt = f"{val:.{decimals}f}" if decimals else f"{val:.0f}"
            st.metric(label, fmt)


# ─── Visualizations ──────────────────────────────────────

def happiness_trend(df):
    st.subheader("🌍 Happiness Trend by Country")
    countries = sorted(df["Country name"].dropna().unique())
    if not countries:
        st.warning("No country data available.")
        return

    default_idx = countries.index("India") if "India" in countries else 0
    selected_country = st.selectbox("Select a country", countries, index=default_idx, key="happiness_country")

    country_trend = df[df["Country name"] == selected_country].dropna(subset=["year", "Life Ladder"]).sort_values("year")
    if country_trend.empty:
        st.warning(f"No happiness data available for {selected_country}.")
        return

    fig = px.line(country_trend, x="year", y="Life Ladder", markers=True,
                  labels={"year": "Year", "Life Ladder": "Life Ladder"}, template="plotly_white")
    fig.update_traces(line=dict(width=3), marker=dict(size=8),
                      hovertemplate=f"{selected_country}<br>Year: %{{x}}<br>Life Ladder: %{{y:.2f}}<extra></extra>")
    fig.update_layout(title=f"Life Ladder in {selected_country}", title_x=0.5, height=500,
                      yaxis=dict(range=[0, 10], gridcolor="rgba(0,0,0,0.08)"),
                      xaxis=dict(gridcolor="rgba(0,0,0,0.08)"))
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def happiness_vs_gdp(df):
    st.subheader("💰 Happiness vs GDP per Capita")
    gdp_df = df.dropna(subset=["Log GDP per capita", "Life Ladder"])

    fig = px.scatter(gdp_df, x="Log GDP per capita", y="Life Ladder", color="Life Ladder",
                     hover_name="Country name", hover_data={"year": True, "Log GDP per capita": ":.2f", "Life Ladder": ":.2f"},
                     color_continuous_scale="Viridis", trendline="ols",
                     labels={"Log GDP per capita": "Log GDP per Capita", "Life Ladder": "Life Ladder"},
                     template="plotly_white")
    fig.update_traces(marker=dict(size=9, opacity=0.75, line=dict(width=0.5, color="white")), selector=dict(mode="markers"))
    fig.update_layout(title="Does Higher GDP Relate to Greater Happiness?", title_x=0.5, height=550,
                      yaxis=dict(range=[0, 10], gridcolor="rgba(0,0,0,0.08)"),
                      xaxis=dict(gridcolor="rgba(0,0,0,0.08)"),
                      coloraxis_colorbar=dict(title="Life Ladder"))
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def happiness_vs_factor(df):
    st.subheader("🤝 Factors Associated with Happiness")
    factor = st.selectbox("Select a factor", ["Social support", "Freedom to make life choices"], key="happiness_factor")

    factor_df = df.dropna(subset=[factor, "Life Ladder"])

    fig = px.scatter(factor_df, x=factor, y="Life Ladder", color="Life Ladder",
                     hover_name="Country name", hover_data={"year": True, factor: ":.2f", "Life Ladder": ":.2f"},
                     color_continuous_scale="Blues", trendline="ols",
                     labels={factor: factor, "Life Ladder": "Life Ladder"}, template="plotly_white")
    fig.update_traces(marker=dict(size=9, opacity=0.75, line=dict(width=0.5, color="white")), selector=dict(mode="markers"))
    fig.update_layout(title=f"Life Ladder vs {factor}", title_x=0.5, height=550,
                      yaxis=dict(range=[0, 10], gridcolor="rgba(0,0,0,0.08)"),
                      xaxis=dict(gridcolor="rgba(0,0,0,0.08)"), coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def country_comparison(df):
    st.subheader("📊 Country Comparison")
    countries = sorted(df["Country name"].unique())
    selected = st.multiselect("Select 2–5 countries", countries, default=countries[:3], max_selections=5, key="comparison_countries")

    metrics = ["Life Ladder", "Log GDP per capita", "Social support",
               "Healthy life expectancy at birth", "Freedom to make life choices"]

    comp_df = df[df["Country name"].isin(selected)].groupby("Country name", as_index=False)[metrics].mean()
    comp_long = comp_df.melt(id_vars="Country name", value_vars=metrics, var_name="Metric", value_name="Value")

    fig = px.bar(comp_long, x="Country name", y="Value", color="Country name",
                 facet_col="Metric", facet_col_wrap=2, barmode="group",
                 hover_data={"Country name": True, "Metric": True, "Value": ":.2f"},
                 labels={"Country name": "Country", "Value": "Average Value", "Metric": ""},
                 template="plotly_white")
    fig.update_layout(title="Average Happiness Indicators by Country", title_x=0.5, height=800, showlegend=False)
    fig.update_yaxes(matches=None)
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def global_happiness(df):
    st.subheader("📈 Global Happiness Over Time")
    global_df = df.groupby("year", as_index=False)["Life Ladder"].mean().rename(columns={"Life Ladder": "Average Life Ladder"})

    fig = px.line(global_df, x="year", y="Average Life Ladder", markers=True,
                  labels={"year": "Year", "Average Life Ladder": "Average Life Ladder"}, template="plotly_white")
    fig.update_traces(line=dict(width=3, color="#059669"), marker=dict(size=8),
                      hovertemplate="Year: %{x}<br>Average Life Ladder: %{y:.2f}<extra></extra>")
    fig.update_layout(title="Global Average Life Ladder by Year", title_x=0.5, height=500,
                      yaxis=dict(range=[0, 10], gridcolor="rgba(0,0,0,0.08)"),
                      xaxis=dict(dtick=2, gridcolor="rgba(0,0,0,0.08)"))
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def raw_data_table(df: pd.DataFrame) -> None:
    st.subheader("📋 Raw Data")
    st.dataframe(df, use_container_width=True, height=400)