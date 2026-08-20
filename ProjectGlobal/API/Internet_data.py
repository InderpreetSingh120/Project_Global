"""
Global Internet Data Module

Expected CSV columns:
    Entity, Code, Year, Cellular subscriptions, Internet users (%), Number of internet users, Broadband subscriptions
"""

from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


DATA_PATH = Path(__file__).parent / "data" / "internet_dataset.csv"

EXPECTED_COLUMNS = {
    "Entity", "Code", "Year",
    "Cellular subscriptions", "Internet users (%)",
    "Number of internet users", "Broadband subscriptions",
}


# ─── Data Loading ────────────────────────────────────────

def load_internet_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
    """Load and clean the global internet dataset."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Internet dataset not found: {path}")

    df = pd.read_csv(path)
    df = df.rename(columns={
        "Cellular Subscription": "Cellular subscriptions",
        "Internet Users(%)": "Internet users (%)",
        "No. of Internet Users": "Number of internet users",
        "Broadband Subscription": "Broadband subscriptions",
    })

    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    df = df.copy()
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df = df.dropna(subset=["Year", "Entity"])
    df["Year"] = df["Year"].astype(int)

    for col in ["Cellular subscriptions", "Internet users (%)", "Number of internet users", "Broadband subscriptions"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Code"] = df["Code"].fillna("").astype(str).str.upper()
    return df.sort_values(["Year", "Entity"]).reset_index(drop=True)


# ─── Query Helpers ───────────────────────────────────────

def get_latest_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    return df.loc[df["Year"] == df["Year"].max()].copy()


def get_available_years(df: pd.DataFrame, metric: str) -> list[int]:
    valid = df.loc[df[metric] > 0, "Year"]
    return sorted(valid.dropna().astype(int).unique().tolist())


def get_latest_year(df: pd.DataFrame) -> Optional[int]:
    if df.empty:
        return None
    return int(df["Year"].max())


def get_country_data(df: pd.DataFrame, country: str, latest_only: bool = True) -> pd.DataFrame:
    result = df[df["Entity"].str.casefold() == country.casefold()].copy()
    if latest_only and not result.empty:
        result = result[result["Year"] == result["Year"].max()]
    return result.sort_values("Year").reset_index(drop=True)


# ─── Visualizations ──────────────────────────────────────

def create_metric_map(df: pd.DataFrame, metric: str = "Internet users (%)", year: Optional[int] = None) -> go.Figure:
    allowed = {"Internet users (%)", "Cellular subscriptions", "Number of internet users", "Broadband subscriptions"}
    if metric not in allowed:
        raise ValueError(f"Unsupported metric '{metric}'. Choose from: {', '.join(sorted(allowed))}")

    if year is None:
        year = get_latest_year(df)

    map_df = df[(df["Year"] == year) & (df["Code"].str.len() == 3)].copy()

    labels = {
        "Internet users (%)": "Internet Users (%)", "Cellular subscriptions": "Cellular Subscriptions",
        "Number of internet users": "Internet Users", "Broadband subscriptions": "Broadband Subscriptions",
    }

    fig = px.choropleth(map_df, locations="Code", color=metric, hover_name="Entity",
                        hover_data={"Code": False, metric: ":,.2f"}, color_continuous_scale="Viridis",
                        labels={metric: labels[metric]}, title=f"{labels[metric]} — {year}")
    fig.update_layout(height=520, margin=dict(t=60, b=10, l=10, r=10))
    return fig


def create_metric_trend(df: pd.DataFrame, metric: str = "Internet users (%)", countries: Optional[list[str]] = None) -> go.Figure:
    if metric not in EXPECTED_COLUMNS:
        raise ValueError(f"Unsupported metric: {metric}")

    trend_df = df.copy()
    if countries:
        wanted = {c.casefold() for c in countries}
        trend_df = trend_df[trend_df["Entity"].str.casefold().isin(wanted)]
    trend_df = trend_df.dropna(subset=[metric])

    fig = px.line(trend_df, x="Year", y=metric, color="Entity", markers=True,
                  labels={"Year": "Year", metric: metric, "Entity": "Country"}, title=f"{metric} Over Time")
    fig.update_layout(height=450, margin=dict(t=60, b=20, l=20, r=20))
    return fig


def create_top_countries_chart(df: pd.DataFrame, metric: str = "Internet users (%)", year: Optional[int] = None, top_n: int = 10) -> go.Figure:
    if metric not in EXPECTED_COLUMNS:
        raise ValueError(f"Unsupported metric: {metric}")

    if year is None:
        year = get_latest_year(df)

    chart_df = df[(df["Year"] == year) & (df["Code"].str.len() == 3)].dropna(subset=[metric])
    chart_df = chart_df.sort_values(metric, ascending=False).head(top_n).sort_values(metric)

    fig = px.bar(chart_df, x=metric, y="Entity", orientation="h", text=metric,
                 labels={metric: metric, "Entity": "Country"}, title=f"Top {top_n} Countries — {metric} ({year})")
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig.update_layout(height=max(400, top_n * 38), margin=dict(t=60, b=20, l=20, r=40))
    return fig


def create_country_comparison(df: pd.DataFrame, countries: list[str], year: Optional[int] = None) -> go.Figure:
    if year is None:
        year = get_latest_year(df)

    wanted = {c.casefold() for c in countries}
    comp = df[(df["Year"] == year) & df["Entity"].str.casefold().isin(wanted)].copy()
    if comp.empty:
        return go.Figure()

    metrics = ["Internet users (%)", "Cellular subscriptions", "Broadband subscriptions"]
    rows = []
    for _, row in comp.iterrows():
        for m in metrics:
            if pd.notna(row[m]):
                rows.append({"Entity": row["Entity"], "Metric": m, "Value": row[m]})

    chart_df = pd.DataFrame(rows)
    if chart_df.empty:
        return go.Figure()

    fig = px.bar(chart_df, x="Metric", y="Value", color="Entity", barmode="group",
                 labels={"Value": "Value", "Metric": "Metric"}, title=f"Country Comparison — {year}")
    fig.update_layout(height=450, margin=dict(t=60, b=20, l=20, r=20))
    return fig


def get_dataset_summary(df: pd.DataFrame) -> dict:
    latest = get_latest_data(df)
    return {
        "latest_year": get_latest_year(df),
        "countries": int(latest["Code"].ne("").sum()),
        "avg_internet_users": round(latest["Internet users (%)"].mean(), 2) if not latest.empty else 0,
        "total_internet_users": latest["Number of internet users"].sum() if not latest.empty else 0,
    }