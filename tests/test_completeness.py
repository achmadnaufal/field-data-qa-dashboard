"""Tests for completeness scoring module."""

import pandas as pd
import pytest

from src.completeness import (
    REQUIRED_FIELDS,
    add_completeness_score,
    compute_field_completeness,
    compute_row_completeness,
)


class TestComputeRowCompleteness:
    def test_fully_complete_row(self, valid_row: pd.Series) -> None:
        score = compute_row_completeness(valid_row)
        assert score == 1.0

    def test_incomplete_row(self, incomplete_row: pd.Series) -> None:
        score = compute_row_completeness(incomplete_row)
        assert score < 1.0

    def test_incomplete_row_has_correct_ratio(self, incomplete_row: pd.Series) -> None:
        score = compute_row_completeness(incomplete_row)
        present = sum(
            1 for f in REQUIRED_FIELDS
            if f in incomplete_row.index and pd.notna(incomplete_row[f])
        )
        expected = present / len(REQUIRED_FIELDS)
        assert abs(score - expected) < 1e-9

    def test_empty_required_fields(self, valid_row: pd.Series) -> None:
        score = compute_row_completeness(valid_row, required=[])
        assert score == 0.0

    def test_custom_required_fields(self, valid_row: pd.Series) -> None:
        score = compute_row_completeness(valid_row, required=["submission_id", "submitter"])
        assert score == 1.0


class TestComputeFieldCompleteness:
    def test_returns_all_required_fields(self, sample_df: pd.DataFrame) -> None:
        result = compute_field_completeness(sample_df)
        assert set(result.keys()) == set(REQUIRED_FIELDS)

    def test_values_between_zero_and_one(self, sample_df: pd.DataFrame) -> None:
        result = compute_field_completeness(sample_df)
        for val in result.values():
            assert 0.0 <= val <= 1.0

    def test_submission_id_fully_complete(self, sample_df: pd.DataFrame) -> None:
        result = compute_field_completeness(sample_df)
        assert result["submission_id"] == 1.0


class TestAddCompletenessScore:
    def test_adds_score_column(self, sample_df: pd.DataFrame) -> None:
        result = add_completeness_score(sample_df)
        assert "completeness_score" in result.columns

    def test_does_not_mutate_original(self, sample_df: pd.DataFrame) -> None:
        original_cols = list(sample_df.columns)
        add_completeness_score(sample_df)
        assert list(sample_df.columns) == original_cols

    def test_scores_between_zero_and_one(self, sample_df: pd.DataFrame) -> None:
        result = add_completeness_score(sample_df)
        assert (result["completeness_score"] >= 0.0).all()
        assert (result["completeness_score"] <= 1.0).all()
