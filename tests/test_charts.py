"""Tests for chart generation module."""

import pandas as pd
import plotly.graph_objects as go
import pytest

from src.charts import (
    completeness_distribution_chart,
    completeness_heatmap,
    flag_distribution_chart,
    gps_scatter_map,
    submission_timeline_chart,
)


class TestSubmissionTimelineChart:
    def test_returns_figure(self, sample_df: pd.DataFrame) -> None:
        sample_df = sample_df.assign(
            submission_date=pd.to_datetime(sample_df["submission_date"])
        )
        fig = submission_timeline_chart(sample_df)
        assert isinstance(fig, go.Figure)

    def test_empty_dataframe(self) -> None:
        fig = submission_timeline_chart(pd.DataFrame())
        assert isinstance(fig, go.Figure)

    def test_missing_date_column(self) -> None:
        df = pd.DataFrame({"a": [1, 2]})
        fig = submission_timeline_chart(df)
        assert isinstance(fig, go.Figure)


class TestCompletenessHeatmap:
    def test_returns_figure(self) -> None:
        data = {"field_a": 0.95, "field_b": 0.5, "field_c": 0.75}
        fig = completeness_heatmap(data)
        assert isinstance(fig, go.Figure)

    def test_empty_dict(self) -> None:
        fig = completeness_heatmap({})
        assert isinstance(fig, go.Figure)

    def test_all_complete(self) -> None:
        data = {"field_a": 1.0, "field_b": 1.0}
        fig = completeness_heatmap(data)
        assert isinstance(fig, go.Figure)


class TestGpsScatterMap:
    def test_returns_figure(self) -> None:
        df = pd.DataFrame({
            "latitude": [-6.2, -7.3],
            "longitude": [106.8, 110.4],
            "submission_id": ["A", "B"],
            "gps_has_coordinates": [True, True],
            "gps_in_bounds": [True, True],
            "plot_id": ["P1", "P2"],
            "submitter": ["U1", "U2"],
        })
        fig = gps_scatter_map(df)
        assert isinstance(fig, go.Figure)

    def test_empty_dataframe(self) -> None:
        df = pd.DataFrame(columns=["latitude", "longitude"])
        fig = gps_scatter_map(df)
        assert isinstance(fig, go.Figure)


class TestFlagDistributionChart:
    def test_returns_figure(self) -> None:
        summary = {"gps_out_of_bounds": 3, "low_completeness": 2}
        fig = flag_distribution_chart(summary)
        assert isinstance(fig, go.Figure)

    def test_empty_summary(self) -> None:
        fig = flag_distribution_chart({})
        assert isinstance(fig, go.Figure)


class TestCompletenessDistributionChart:
    def test_returns_figure(self) -> None:
        df = pd.DataFrame({"completeness_score": [0.5, 0.8, 1.0, 0.3]})
        fig = completeness_distribution_chart(df)
        assert isinstance(fig, go.Figure)

    def test_empty_dataframe(self) -> None:
        fig = completeness_distribution_chart(pd.DataFrame())
        assert isinstance(fig, go.Figure)
