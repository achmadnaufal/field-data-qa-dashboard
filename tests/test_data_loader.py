"""Tests for data loader module."""

from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from src.data_loader import (
    EXPECTED_COLUMNS,
    NUMERIC_COLUMNS,
    get_summary_stats,
    load_csv,
    validate_columns,
)


DEMO_CSV = Path(__file__).parent.parent / "demo" / "sample_data.csv"


class TestLoadCsv:
    def test_loads_demo_file(self) -> None:
        df = load_csv(DEMO_CSV)
        assert len(df) > 0

    def test_numeric_columns_are_numeric(self) -> None:
        df = load_csv(DEMO_CSV)
        for col in NUMERIC_COLUMNS:
            if col in df.columns:
                assert pd.api.types.is_numeric_dtype(df[col])

    def test_submission_date_is_datetime(self) -> None:
        df = load_csv(DEMO_CSV)
        assert pd.api.types.is_datetime64_any_dtype(df["submission_date"])

    def test_loads_from_string_io(self) -> None:
        csv_data = "submission_id,submitter\nSUB001,Test\n"
        df = load_csv(StringIO(csv_data))
        assert len(df) == 1

    def test_coerces_bad_numeric_to_nan(self) -> None:
        csv_data = "latitude,longitude\nabc,def\n"
        df = load_csv(StringIO(csv_data))
        assert df["latitude"].isna().all()


class TestValidateColumns:
    def test_demo_data_has_all_columns(self) -> None:
        df = load_csv(DEMO_CSV)
        missing = validate_columns(df)
        assert missing == []

    def test_detects_missing_columns(self) -> None:
        df = pd.DataFrame({"submission_id": [1]})
        missing = validate_columns(df)
        assert len(missing) > 0
        assert "submitter" in missing

    def test_empty_dataframe_missing_all(self) -> None:
        df = pd.DataFrame()
        missing = validate_columns(df)
        assert set(missing) == set(EXPECTED_COLUMNS)


class TestGetSummaryStats:
    def test_returns_required_keys(self) -> None:
        df = load_csv(DEMO_CSV)
        stats = get_summary_stats(df)
        assert "total_rows" in stats
        assert "unique_submitters" in stats
        assert "unique_plots" in stats

    def test_total_rows_matches(self) -> None:
        df = load_csv(DEMO_CSV)
        stats = get_summary_stats(df)
        assert stats["total_rows"] == len(df)

    def test_handles_empty_dataframe(self) -> None:
        df = pd.DataFrame()
        stats = get_summary_stats(df)
        assert stats["total_rows"] == 0
