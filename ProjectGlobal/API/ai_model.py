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
    """Render top-level KPI cards."""
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
    st.subheader("🏢 Top 20 AI Models by Vote Count")
    chart_df = (df.groupby(["model_name", "organization"], as_index=False).agg(vote_count=("vote_count", "max"),rating=("rating", "mean"),rank=("rank", "min"),).dropna(subset=["vote_count"]).nlargest(20, "vote_count").sort_values("vote_count", ascending=True))
    barfig = px.bar(chart_df,x="vote_count",y="model_name",orientation="h",color="organization",text="vote_count",custom_data=["organization", "rating", "rank"])
    barfig.update_traces(
    texttemplate="%{text:,.0f}",
    textposition="outside",
    marker=dict(line=dict(width=0)),
    hovertemplate=("<b>%{y}</b><br><br>""🗳️ Votes: %{x:,.0f}<br>""🏢 Organization: %{customdata[0]}<br>""⭐ Rating: %{customdata[1]:.2f}<br>""🏆 Rank: %{customdata[2]}<extra></extra>"),)
    median_votes = chart_df["vote_count"].median()
    barfig.add_vline(x=median_votes,line_dash="dash",line_width=2,annotation_text="Median",)
    barfig.update_layout(title=None, xaxis=dict(title="Number of Votes",tickformat="~s",showgrid=True,gridcolor="rgba(128,128,128,0.08)",zeroline=False,),yaxis=dict(title=None,categoryorder="total ascending",tickfont=dict(size=12),),legend=dict(title="Organization",orientation="v",yanchor="middle",y=0.5,xanchor="left",x=1.02,),coloraxis_showscale=False,height=650,margin=dict(l=260,r=20,t=20,b=20,),plot_bgcolor="rgba(0,0,0,0)",paper_bgcolor="rgba(0,0,0,0)",)
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
#  6. License Distribution
# ──────────────────────────────────────────────
def license_distribution(df: pd.DataFrame) -> None:
    st.subheader("📜 License Distribution")

    license_counts = df["license"].value_counts().reset_index()
    license_counts.columns = ["license", "count"]

    # Replace NaN / empty with "Unknown"
    license_counts["license"] = license_counts["license"].fillna("Unknown").replace(
        "", "Unknown"
    )

    # Use a pie chart if categories ≤ 8, else bar
    n_cats = len(license_counts)

    if n_cats <= 8:
        fig = px.pie(
            license_counts,
            names="license",
            values="count",
            title="License Distribution",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3,
        )
    else:
        fig = px.bar(
            license_counts,
            x="license",
            y="count",
            title="License Distribution",
            labels={"license": "License", "count": "Count"},
            color="count",
            color_continuous_scale="Blues",
        )
        fig.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────
#  7. Models Added Over Time
# ──────────────────────────────────────────────
def models_over_time(df: pd.DataFrame) -> None:
    st.subheader("📅 Models Added Over Time")

    df_dates = df.dropna(subset=["leaderboard_publish_date"]).copy()

    if df_dates.empty:
        st.warning("No valid date data available.")
        return

    df_dates["year_month"] = df_dates["leaderboard_publish_date"].dt.to_period("M")
    monthly_counts = df_dates.groupby("year_month").size().reset_index(name="models_added")
    monthly_counts["year_month"] = monthly_counts["year_month"].astype(str)

    fig = px.line(
        monthly_counts,
        x="year_month",
        y="models_added",
        title="Models Added Per Month",
        labels={"year_month": "Month", "models_added": "Models Added"},
        markers=True,
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────
#  8. Rating Distribution (Histogram)
# ──────────────────────────────────────────────
def rating_distribution(df: pd.DataFrame) -> None:
    st.subheader("📊 Rating Distribution")

    fig = px.histogram(
        df,
        x="rating",
        nbins=30,
        title="Distribution of Model Ratings",
        labels={"rating": "Rating"},
        color_discrete_sequence=["#4C72B0"],
    )
    st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────
#  10. Subset Distribution
# ──────────────────────────────────────────────
def subset_distribution(df: pd.DataFrame) -> None:
    st.subheader("📂 Subset Distribution")

    if "subset" not in df.columns:
        st.info("No 'subset' column in the dataset.")
        return

    subset_counts = df["subset"].value_counts().reset_index()
    subset_counts.columns = ["subset", "count"]

    # If only one unique value, skip the chart
    if len(subset_counts) <= 1:
        st.info(
            f"Only one subset value found: '{subset_counts.iloc[0]['subset']}'. "
            "Skipping distribution chart."
        )
        return

    n_cats = len(subset_counts)

    if n_cats <= 8:
        fig = px.pie(
            subset_counts,
            names="subset",
            values="count",
            title="Subset Distribution",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
    else:
        fig = px.bar(
            subset_counts,
            x="subset",
            y="count",
            title="Subset Distribution",
            labels={"subset": "Subset", "count": "Count"},
            color="count",
            color_continuous_scale="Blues",
        )
        fig.update_layout(xaxis_tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)


# ──────────────────────────────────────────────
#  Raw Data Table
# ──────────────────────────────────────────────
def raw_data_table(df: pd.DataFrame) -> None:
    st.subheader("📋 Raw Data")
    st.dataframe(df, use_container_width=True, height=400)