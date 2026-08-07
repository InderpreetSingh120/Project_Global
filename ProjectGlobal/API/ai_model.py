from pathlib import Path
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ──────────────────────────────────────────────
#  Data Loading (cached)
# ──────────────────────────────────────────────
DATA_PATH = Path(__file__).parent / "data" / "ai_model_arena_rankings_streamlit.csv"
@st.cache_data
def load_ai_data() -> pd.DataFrame:
    """Load the cleaned AI Model Arena dataset."""
    df = pd.read_csv(DATA_PATH)
    if not DATA_PATH.exists():
            st.error(f"Data file missing at {DATA_PATH}")
            return pd.DataFrame()
    # Parse dates
    if "leaderboard_publish_date" in df.columns:
        df["leaderboard_publish_date"] = pd.to_datetime(
            df["leaderboard_publish_date"], errors="coerce"
        )

    # Ensure numeric columns
    for col in ["rating", "vote_count", "rank"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# ──────────────────────────────────────────────
#  KPIs
# ──────────────────────────────────────────────
def render_kpis(df: pd.DataFrame) -> None:
    #Render top-level KPI cards
    total_models = len(df)
    total_orgs = df["organization"].nunique() 
    avg_rating = df["rating"].mean() 
    highest_rating = df["rating"].max() 
    lowest_rating = df["rating"].min() 
    latest_date = df["leaderboard_publish_date"].max()
    latest_date_str = latest_date.strftime("%Y-%m-%d")
    #columns for KPIs
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Total Models", f"{total_models}")
    col2.metric("Total Organizations", f"{total_orgs}")
    col3.metric("Average Rating", f"{avg_rating:.2f}".rstrip("0").rstrip("."))
    col4.metric("Highest Rating", f"{highest_rating:.2f}".rstrip("0").rstrip("."))
    col5.metric("Lowest Rating", f"{lowest_rating:.2f}".rstrip("0").rstrip("."))
    col6.metric("Latest Leaderboard Date", latest_date_str)
# ──────────────────────────────────────────────
#  1. Top Models by tree, donut, bar
# ──────────────────────────────────────────────
def top_models(df: pd.DataFrame) -> None:
    st.subheader("🏆 Top Models")
    treef, donotf, barf = st.tabs(["Treemap", "Donut Chart"," Bar Chart"])
    org2 = (df["organization"].value_counts().head(10).rename_axis("Organization").reset_index(name="Models"))
    with treef:
        st.write("Compare model count and average rating together")
        org1 = (df.groupby("organization").agg(avg_rating=("rating", "mean"),total_votes=("vote_count", "sum"),models=("model_name", "count")).reset_index())
        treefig = px.treemap(org1,path=[px.Constant("Organizations"), "organization"],values="models",color="avg_rating",color_continuous_scale="Viridis",title="Top Organizations by Model Count (Others Combined)")
        st.plotly_chart(treefig, use_container_width=True)
    with donotf:
        st.write("Show percentage share of models")
        donotfig = px.pie(org2,names="Organization",values="Models",hole=0.5,title="Top Organizations by Model Count (Others Combined)")
        st.plotly_chart(donotfig, use_container_width=True)
    with barf:
        st.write("Show exact model counts")
        barfig = px.bar(org2,x="Organization",y="Models",title="Top Organizations by Model Count (Others Combined)",color="Models",color_continuous_scale="Viridis")
        st.plotly_chart(barfig, use_container_width=True)
# ──────────────────────────────────────────────
#  2. Vote count vs rating (bubble chart, scatter plot)
# ──────────────────────────────────────────────
def VRcharts(df: pd.DataFrame) -> None:
    st.subheader("🗳️ Votes vs. Rating")
    bubblef, scatterf = st.tabs(["Bubble Chart", "Scatter Plot"])
    with bubblef:
        st.write("Bubble chart showing total votes vs average rating by organization")
        org_df = (df.groupby("organization").agg(model_count=("model_name", "count"),avg_rating=("rating", "mean"),total_votes=("vote_count", "sum")).reset_index())
        bubblef = px.scatter(org_df,x="total_votes",y="avg_rating",size="model_count",color="organization",hover_name="organization",hover_data={"model_count": True,"total_votes": ":,","avg_rating": ":.2f"},title="Organizations: Votes vs Average Rating",labels={"total_votes": "Total Votes", "avg_rating": "Average Rating", "model_count": "Number of Models"})
        st.plotly_chart(bubblef, use_container_width=True)
    with scatterf:
        st.write("Scatter plot showing total votes vs average rating by organization")
        scatterf = px.scatter(org_df,x="total_votes",y="avg_rating",color="organization",hover_name="organization",hover_data={"model_count": True,"total_votes": ":,","avg_rating": ":.2f",},title="Organizations: Total Votes vs Average Rating",labels={"total_votes": "Total Votes","avg_rating": "Average Rating","model_count": "Number of Models",},opacity=0.7,)
        st.plotly_chart(scatterf, use_container_width=True)

# ──────────────────────────────────────────────
#  3. Total votes bar chart
# ──────────────────────────────────────────────
def Votebarchart(df: pd.DataFrame) -> None:
    st.subheader("Top 20 AI Models by Vote Count")
    chart_df = (df.groupby(["model_name", "organization"], as_index=False).agg(vote_count=("vote_count", "max"),rating=("rating", "mean"),rank=("rank", "min"),).dropna(subset=["vote_count"]).nlargest(20, "vote_count").sort_values("vote_count"))
    barfig = px.bar(chart_df,x="vote_count",y="model_name",orientation="h",color="organization",text="vote_count",hover_data={"organization": True,"rating": ":.2f","rank": True,"vote_count": ":,",},labels={"vote_count": "Votes","model_name": "Model","organization": "Organization",},)
    barfig.update_traces(texttemplate="%{text:,.0f}",textposition="outside",)
    barfig.update_layout(height=600,yaxis=dict(categoryorder="total ascending"),legend_title_text="Organization",  )
    barfig.add_vline(x=chart_df["vote_count"].median(),line_dash="dash",annotation_text="Median",)
    st.plotly_chart(barfig, use_container_width=True, theme="streamlit")
# ──────────────────────────────────────────────
#  4. Who's held #1 (step chart)
# ──────────────────────────────────────────────
def firstplace(df: pd.DataFrame) -> None:
    st.subheader("🥇 Who Held #1?")
    leaders = (df[(df["subset"] == "text") &(df["rank"] == 1)].sort_values("leaderboard_publish_date"))
    linefig = px.line(leaders,x="leaderboard_publish_date",y="model_name",color="organization",markers=True,title="Rank #1 Model Over Time",labels={"leaderboard_publish_date": "Leaderboard Date","model_name": "#1 Model",},hover_data={"organization": True,"rating": ":.2f","vote_count": ":,",})
    linefig.update_traces(line_shape="hv")
    st.plotly_chart(linefig, use_container_width=True)
    num_models = leaders["model_name"].nunique()
    st.write(f"**{num_models} different models have held the #1 position on the text leaderboard.**")
# ──────────────────────────────────────────────
#  5. License vs Rating
# ──────────────────────────────────────────────
def license_vs_rating(df: pd.DataFrame) -> None:
    st.subheader("📜 License vs. Rating")
    chart_df = (df.dropna(subset=["license", "rating"]).copy())
    counts = chart_df["license"].value_counts()
    chart_df = chart_df[chart_df["license"].isin(counts[counts >= 5].index)]
    fig = px.box(chart_df,x="license",y="rating",color="license",points="outliers",labels={"license": "License","rating": "Arena Rating",},)
    fig.update_layout(xaxis_tickangle=-25,showlegend=False,)
    st.plotly_chart(fig, use_container_width=True)
# ──────────────────────────────────────────────
#  6. Models Added Over Time
# ──────────────────────────────────────────────
def leaderboard_activity(df: pd.DataFrame) -> None:
    st.subheader("📅 Leaderboard Activity Over Time")

    chart_df = (
        df.dropna(subset=["leaderboard_publish_date"])
        .copy()
    )

    chart_df["month"] = (
        chart_df["leaderboard_publish_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly = (
        chart_df.groupby("month")
        .size()
        .reset_index(name="Models")
    )

    fig = px.line(
        monthly,
        x="month",
        y="Models",
        markers=True,
        labels={"month": "Month","Models": "Leaderboard Entries",},)
    fig.update_traces(
        line_width=3,
        marker_size=7,
    )
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")
# ──────────────────────────────────────────────
#  7. Rating Distribution (Histogram)
# ──────────────────────────────────────────────
def rating_distribution(df: pd.DataFrame) -> None:
    st.subheader("📊 Rating Distribution")
    fig = px.histogram(df,x="rating",nbins=25,color_discrete_sequence=["#3B82F6"],labels={"rating": "Arena Rating"},)
    fig.update_traces(hovertemplate=("<b>Rating Range</b><br>""%{x}<br>""Models: %{y}<extra></extra>"))
    fig.update_layout(bargap=0.05)
    st.plotly_chart(fig, use_container_width=True, theme="streamlit")
# ──────────────────────────────────────────────
#  8. Subset Distribution
# ──────────────────────────────────────────────
def subset_distribution(df: pd.DataFrame) -> None:
    st.subheader("📂 Subset Distribution")
    donotf,barf = st.tabs(["Donut Chart", "Bar Chart"])
    with donotf:
        subset_counts = (df["subset"].value_counts().rename_axis("Subset").reset_index(name="Models"))
        donotfig = px.pie(subset_counts,names="Subset",values="Models",hole=0.55,)
        donotfig.update_traces(textinfo="percent+label",hovertemplate=("<b>%{label}</b><br>""Models: %{value}<br>""Share: %{percent}<extra></extra>"))
        st.plotly_chart(donotfig, use_container_width=True, theme="streamlit")
    with barf:
        barfig = px.bar(subset_counts.sort_values("Models"),x="Models",y="Subset",orientation="h",color="Models",text="Models",)
        barfig.update_traces(textposition="outside")
        st.plotly_chart(barfig, use_container_width=True, theme="streamlit")
# ──────────────────────────────────────────────
#  Raw Data Table
# ──────────────────────────────────────────────
def raw_data_table(df: pd.DataFrame) -> None:
    st.subheader("📋 Raw Data")
    st.dataframe(df, use_container_width=True, height=400)