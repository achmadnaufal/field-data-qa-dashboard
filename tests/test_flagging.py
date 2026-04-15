"""Tests for flagging module."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from src.flagging import (
    COMPLETENESS_THRESHOLD,
    compute_all_flags,
    export_flagged_to_csv,
    flag_completeness_issues,
    flag_duplicate_plots,
    flag_gps_issues,
    get_flag_summary,
    get_flagged_records,
)


class TestFlagGpsIssues:
    def test_flags_missing_coordinates(self) -> None:
        df = pd.DataFrame({
            "gps_has_coordinates": [False],
            "gps_in_bounds": [False],
            "gps_accuracy_ok": [False],
        })
        result = flag_gps_issues(df)
        assert "gps_missing" in result["gps_flags"].iloc[0]

    def test_flags_out_of_bounds(self) -> None:
        df = pd.DataFrame({
            "gps_has_coordinates": [True],
            "gps_in_bounds": [False],
            "gps_accuracy_ok": [True],
        })
        result = flag_gps_issues(df)
        assert "gps_out_of_bounds" in result["gps_flags"].iloc[0]

    def test_flags_poor_accuracy(self) -> None:
        df = pd.DataFrame({
            "gps_has_coordinates": [True],
            "gps_in_bounds": [True],
            "gps_accuracy_ok": [False],
        })
        result = flag_gps_issues(df)
        assert "gps_poor_accuracy" in result["gps_flags"].iloc[0]

    def test_no_flags_for_valid_row(self) -> None:
        df = pd.DataFrame({
            "gps_has_coordinates": [True],
            "gps_in_bounds": [True],
            "gps_accuracy_ok": [True],
        })
        result = flag_gps_issues(df)
        assert result["gps_flags"].iloc[0] == []


class TestFlagCompletenessIssues:
    def test_flags_low_completeness(self) -> None:
        df = pd.DataFrame({"completeness_score": [0.3]})
        result = flag_completeness_issues(df)
        assert "low_completeness" in result["completeness_flags"].iloc[0]

    def test_no_flag_for_high_completeness(self) -> None:
        df = pd.DataFrame({"completeness_score": [0.95]})
        result = flag_completeness_issues(df)
        assert result["completeness_flags"].iloc[0] == []

    def test_threshold_boundary(self) -> None:
        df = pd.DataFrame({"completeness_score": [COMPLETENESS_THRESHOLD]})
        result = flag_completeness_issues(df)
        assert result["completeness_flags"].iloc[0] == []


class TestFlagDuplicatePlots:
    def test_detects_duplicate(self) -> None:
        df = pd.DataFrame({
            "plot_id": ["PLT-001", "PLT-001"],
            "submission_date": ["2026-03-01", "2026-03-01"],
        })
        result = flag_duplicate_plots(df)
        assert all("duplicate_plot" in f for f in result["duplicate_flags"])

    def test_no_duplicate_different_dates(self) -> None:
        df = pd.DataFrame({
            "plot_id": ["PLT-001", "PLT-001"],
            "submission_date": ["2026-03-01", "2026-03-02"],
        })
        result = flag_duplicate_plots(df)
        assert all(f == [] for f in result["duplicate_flags"])


class TestComputeAllFlags:
    def test_adds_all_flags_column(self, flaggable_df: pd.DataFrame) -> None:
        result = compute_all_flags(flaggable_df)
        assert "all_flags" in result.columns
        assert "is_flagged" in result.columns

    def test_is_flagged_boolean(self, flaggable_df: pd.DataFrame) -> None:
        result = compute_all_flags(flaggable_df)
        assert result["is_flagged"].dtype == bool


class TestGetFlaggedRecords:
    def test_returns_only_flagged(self, flaggable_df: pd.DataFrame) -> None:
        result = compute_all_flags(flaggable_df)
        flagged = get_flagged_records(result)
        assert all(flagged["is_flagged"])

    def test_returns_empty_without_flags(self) -> None:
        df = pd.DataFrame({"a": [1, 2]})
        assert get_flagged_records(df).empty


class TestGetFlagSummary:
    def test_returns_dict(self, flaggable_df: pd.DataFrame) -> None:
        result = compute_all_flags(flaggable_df)
        summary = get_flag_summary(result)
        assert isinstance(summary, dict)

    def test_counts_are_positive(self, flaggable_df: pd.DataFrame) -> None:
        result = compute_all_flags(flaggable_df)
        summary = get_flag_summary(result)
        for count in summary.values():
            assert count > 0


class TestExportFlaggedToCsv:
    def test_creates_csv_file(self, flaggable_df: pd.DataFrame, tmp_path: Path) -> None:
        result = compute_all_flags(flaggable_df)
        path = str(tmp_path / "export.csv")
        export_flagged_to_csv(result, path)
        assert Path(path).exists()

    def test_csv_contains_flagged_only(self, flaggable_df: pd.DataFrame, tmp_path: Path) -> None:
        result = compute_all_flags(flaggable_df)
        path = str(tmp_path / "export.csv")
        export_flagged_to_csv(result, path)
        exported = pd.read_csv(path)
        expected_count = len(get_flagged_records(result))
        assert len(exported) == expected_count
