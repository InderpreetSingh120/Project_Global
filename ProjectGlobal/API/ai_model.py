from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_PATH = Path(__file__).parent / "data" / "ai_model_arena_rankings_streamlit.csv"

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Data file missing at {DATA_PATH}")


@st.cache_data
def load_ai_data() -> pd.DataFrame:
    """Load and clean the AI Model Arena dataset."""
    df = pd.read_csv(DATA_PATH)
    if "leaderboard_publish_date" in df.columns:
        df["leaderboard_publish_date"] = pd.to_datetime(df["leaderboard_publish_date"], errors="coerce")
    for col in ["rating", "vote_count", "rank"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


# ─── KPIs ────────────────────────────────────────────────

def render_kpis(df: pd.DataFrame) -> None:
    total_models = len(df)
    total_orgs = df["organization"].nunique()
    avg_rating = df["rating"].mean()
    highest_rating = df["rating"].max()
    lowest_rating = df["rating"].min()
    latest_date = df["leaderboard_publish_date"].max()
    latest_date_str = latest_date.strftime("%Y-%m-%d")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Models", f"{total_models}")
    c2.metric("Total Organizations", f"{total_orgs}")
    c3.metric("Average Rating", f"{avg_rating:.2f}".rstrip("0").rstrip("."))
    c4.metric("Highest Rating", f"{highest_rating:.2f}".rstrip("0").rstrip("."))
    c5.metric("Lowest Rating", f"{lowest_rating:.2f}".rstrip("0").rstrip("."))
    c6.metric("Latest Leaderboard Date", latest_date_str)


# ─── Visualizations ──────────────────────────────────────

def top_models(df: pd.DataFrame) -> None:
    st.subheader("🏆 Top Models")
    tree, donut, bar = st.tabs(["Treemap", "Donut Chart", "Bar Chart"])

    org_counts = df["organization"].value_counts().head(10).rename_axis("Organization").reset_index(name="Models")
    org_agg = df.groupby("organization").agg(
        avg_rating=("rating", "mean"), total_votes=("vote_count", "sum"), models=("model_name", "count")
    ).reset_index()

    with tree:
        fig = px.treemap(org_agg, path=[px.Constant("Organizations"), "organization"],
                         values="models", color="avg_rating", color_continuous_scale="Viridis",
                         title="Top Organizations by Model Count")
        st.plotly_chart(fig, use_container_width=True)

    with donut:
        fig = px.pie(org_counts, names="Organization", values="Models", hole=0.5,
                     title="Top Organizations by Model Count")
        st.plotly_chart(fig, use_container_width=True)

    with bar:
        fig = px.bar(org_counts, x="Organization", y="Models", color="Models",
                     color_continuous_scale="Viridis", title="Top Organizations by Model Count")
        st.plotly_chart(fig, use_container_width=True)


def VRcharts(df: pd.DataFrame) -> None:
    st.subheader("🗳️ Votes vs. Rating")
    bubble, scatter = st.tabs(["Bubble Chart", "Scatter Plot"])

    org_df = df.groupby("organization").agg(
        model_count=("model_name", "count"), avg_rating=("rating", "mean"), total_votes=("vote_count", "sum")
    ).reset_index()

    with bubble:
        fig = px.scatter(org_df, x="total_votes", y="avg_rating", size="model_count", color="organization",
                         hover_name="organization",
                         hover_data={"model_count": True, "total_votes": ":,", "avg_rating": ":.2f"},
                         title="Organizations: Votes vs Average Rating",
                         labels={"total_votes": "Total Votes", "avg_rating": "Average Rating", "model_count": "Number of Models"})
        st.plotly_chart(fig, use_container_width=True)

    with scatter:
        fig = px.scatter(org_df, x="total_votes", y="avg_rating", color="organization",
                         hover_name="organization",
                         hover_data={"model_count": True, "total_votes": ":,", "avg_rating": ":.2f"},
                         title="Organizations: Total Votes vs Average Rating",
                         labels={"total_votes": "Total Votes", "avg_rating": "Average Rating", "model_count": "Number of Models"},
                         opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)


def Votebarchart(df: pd.DataFrame) -> None:
    st.subheader("Top 20 AI Models by Vote Count")
    chart_df = (df.groupby(["model_name", "organization"], as_index=False)
                .agg(vote_count=("vote_count", "max"), rating=("rating", "mean"), rank=("rank", "min"))
                .dropna(subset=["vote_count"]).nlargest(20, "vote_count").sort_values("vote_count"))

    fig = px.bar(chart_df, x="vote_count", y="model_name", orientation="h", color="organization",
                 text="vote_count",
                 hover_data={"organization": True, "rating": ":.2f", "rank": True, "vote_count": ":,"},
                 labels={"vote_count": "Votes", "model_name": "Model", "organization": "Organization"})
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(height=600, yaxis=dict(categoryorder="total ascending"), legend_title_text="Organization")
    fig.add_vline(x=chart_df["vote_count"].median(), line_dash="dash", annotation_text="Median")
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def firstplace(df: pd.DataFrame) -> None:
    st.subheader("🥇 Who Held #1?")
    leaders = df[(df["subset"] == "text") & (df["rank"] == 1)].sort_values("leaderboard_publish_date")
    fig = px.line(leaders, x="leaderboard_publish_date", y="model_name", color="organization", markers=True,
                  title="Rank #1 Model Over Time",
                  labels={"leaderboard_publish_date": "Leaderboard Date", "model_name": "#1 Model"},
                  hover_data={"organization": True, "rating": ":.2f", "vote_count": ":,"})
    fig.update_traces(line_shape="hv")
    st.plotly_chart(fig, use_container_width=True)
    st.write(f"**{leaders['model_name'].nunique()} different models have held the #1 position on the text leaderboard.**")


def license_vs_rating(df: pd.DataFrame) -> None:
    st.subheader("📜 License vs. Rating")
    chart_df = df.dropna(subset=["license", "rating"]).copy()
    counts = chart_df["license"].value_counts()
    chart_df = chart_df[chart_df["license"].isin(counts[counts >= 5].index)]
    fig = px.box(chart_df, x="license", y="rating", color="license", points="outliers",
                 labels={"license": "License", "rating": "Arena Rating"})
    fig.update_layout(xaxis_tickangle=-25, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def leaderboard_activity(df: pd.DataFrame) -> None:
    st.subheader("📅 Leaderboard Activity Over Time")
    chart_df = df.dropna(subset=["leaderboard_publish_date"]).copy()
    chart_df["month"] = chart_df["leaderboard_publish_date"].dt.to_period("M").dt.to_timestamp()
    monthly = chart_df.groupby("month").size().reset_index(name="Models")
    fig = px.line(monthly, x="month", y="Models", markers=True,
                  labels={"month": "Month", "Models": "Leaderboard Entries"})
    fig.update_traces(line_width=3, marker_size=7)
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def rating_distribution(df: pd.DataFrame) -> None:
    st.subheader("📊 Rating Distribution")
    fig = px.histogram(df, x="rating", nbins=25, color_discrete_sequence=["#3B82F6"], labels={"rating": "Arena Rating"})
    fig.update_traces(hovertemplate="<b>Rating Range</b><br>%{x}<br>Models: %{y}<extra></extra>")
    fig.update_layout(bargap=0.05)
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def subset_distribution(df: pd.DataFrame) -> None:
    st.subheader("📂 Subset Distribution")
    donut, bar = st.tabs(["Donut Chart", "Bar Chart"])
    subset_counts = df["subset"].value_counts().rename_axis("Subset").reset_index(name="Models")

    with donut:
        fig = px.pie(subset_counts, names="Subset", values="Models", hole=0.55)
        fig.update_traces(textinfo="percent+label", hovertemplate="<b>%{label}</b><br>Models: %{value}<br>Share: %{percent}<extra></extra>")
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")

    with bar:
        fig = px.bar(subset_counts.sort_values("Models"), x="Models", y="Subset", orientation="h",
                     color="Models", text="Models")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True, theme="streamlit")


def raw_data_table(df: pd.DataFrame) -> None:
    st.subheader("📋 Raw Data")
    st.dataframe(df, use_container_width=True, height=400)
    st.caption("Data cleaned for analysis. See source link on dashboard for original dataset.")