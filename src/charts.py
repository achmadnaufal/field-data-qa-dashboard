"""Interactive Plotly charts for the QA dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def submission_timeline_chart(df: pd.DataFrame) -> go.Figure:
    """Create an interactive timeline of submissions per day."""
    if "submission_date" not in df.columns or df.empty:
        return go.Figure().update_layout(title="No submission data available")

    daily = (
        df.assign(date=pd.to_datetime(df["submission_date"]).dt.date)
        .groupby("date")
        .size()
        .reset_index(name="count")
    )
    fig = px.bar(
        daily,
        x="date",
        y="count",
        title="Submissions per Day",
        labels={"date": "Date", "count": "Submissions"},
        color_discrete_sequence=["#2E86AB"],
    )
    fig.update_layout(xaxis_title="Date", yaxis_title="Number of Submissions")
    return fig


def completeness_heatmap(field_completeness: dict[str, float]) -> go.Figure:
    """Create a horizontal bar chart of per-field completeness."""
    if not field_completeness:
        return go.Figure().update_layout(title="No completeness data")

    fields = list(field_completeness.keys())
    values = [field_completeness[f] * 100 for f in fields]
    colors = ["#2ECC71" if v >= 90 else "#F39C12" if v >= 70 else "#E74C3C" for v in values]

    fig = go.Figure(
        go.Bar(
            x=values,
            y=fields,
            orientation="h",
            marker_color=colors,
            text=[f"{v:.0f}%" for v in values],
            textposition="auto",
        )
    )
    fig.update_layout(
        title="Field Completeness (%)",
        xaxis_title="Completeness %",
        yaxis_title="Field",
        xaxis=dict(range=[0, 105]),
    )
    return fig


def gps_scatter_map(df: pd.DataFrame) -> go.Figure:
    """Create a scatter plot of GPS coordinates colored by validity."""
    has_coords = df[df.get("gps_has_coordinates", pd.Series(dtype=bool))].copy() if "gps_has_coordinates" in df.columns else df.dropna(subset=["latitude", "longitude"]).copy()

    if has_coords.empty:
        return go.Figure().update_layout(title="No GPS data available")

    color_col = "gps_in_bounds" if "gps_in_bounds" in has_coords.columns else None
    if color_col:
        has_coords = has_coords.assign(
            status=has_coords[color_col].map({True: "In Bounds", False: "Out of Bounds"})
        )
        fig = px.scatter_map(
            has_coords,
            lat="latitude",
            lon="longitude",
            color="status",
            color_discrete_map={"In Bounds": "#2ECC71", "Out of Bounds": "#E74C3C"},
            hover_data=["submission_id", "plot_id", "submitter"],
            title="GPS Locations",
            zoom=3,
        )
    else:
        fig = px.scatter_map(
            has_coords,
            lat="latitude",
            lon="longitude",
            hover_data=["submission_id"] if "submission_id" in has_coords.columns else None,
            title="GPS Locations",
            zoom=3,
        )
    fig.update_layout(map_style="open-street-map", height=500)
    return fig


def flag_distribution_chart(flag_summary: dict[str, int]) -> go.Figure:
    """Create a bar chart of flag type distribution."""
    if not flag_summary:
        return go.Figure().update_layout(title="No flags found")

    fig = px.bar(
        x=list(flag_summary.keys()),
        y=list(flag_summary.values()),
        title="Flag Distribution",
        labels={"x": "Flag Type", "y": "Count"},
        color=list(flag_summary.values()),
        color_continuous_scale="Reds",
    )
    fig.update_layout(showlegend=False)
    return fig


def completeness_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Create a histogram of row-level completeness scores."""
    if "completeness_score" not in df.columns or df.empty:
        return go.Figure().update_layout(title="No completeness data")

    fig = px.histogram(
        df,
        x="completeness_score",
        nbins=20,
        title="Completeness Score Distribution",
        labels={"completeness_score": "Completeness Score"},
        color_discrete_sequence=["#3498DB"],
    )
    fig.update_layout(xaxis_title="Score", yaxis_title="Count")
    return fig
