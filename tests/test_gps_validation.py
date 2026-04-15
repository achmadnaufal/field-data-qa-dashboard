"""Tests for GPS validation module."""

import pandas as pd
import pytest

from src.gps_validation import (
    INDONESIA_BOUNDS,
    MAX_ACCEPTABLE_ACCURACY_M,
    add_gps_flags,
    check_accuracy,
    check_coordinates_in_bounds,
    validate_gps_row,
)


class TestCheckCoordinatesInBounds:
    def test_jakarta_is_in_bounds(self) -> None:
        assert check_coordinates_in_bounds(-6.2088, 106.8456) is True

    def test_bali_is_in_bounds(self) -> None:
        assert check_coordinates_in_bounds(-8.6500, 115.2167) is True

    def test_papua_is_in_bounds(self) -> None:
        assert check_coordinates_in_bounds(-2.5489, 140.7183) is True

    def test_tokyo_is_out_of_bounds(self) -> None:
        assert check_coordinates_in_bounds(35.6762, 139.6503) is False

    def test_boundary_lat_min(self) -> None:
        assert check_coordinates_in_bounds(INDONESIA_BOUNDS["lat_min"], 120.0) is True

    def test_boundary_lat_max(self) -> None:
        assert check_coordinates_in_bounds(INDONESIA_BOUNDS["lat_max"], 120.0) is True

    def test_below_lat_min(self) -> None:
        assert check_coordinates_in_bounds(-12.0, 120.0) is False

    def test_above_lat_max(self) -> None:
        assert check_coordinates_in_bounds(7.0, 120.0) is False


class TestCheckAccuracy:
    def test_good_accuracy(self) -> None:
        assert check_accuracy(5.0) is True

    def test_threshold_accuracy(self) -> None:
        assert check_accuracy(MAX_ACCEPTABLE_ACCURACY_M) is True

    def test_poor_accuracy(self) -> None:
        assert check_accuracy(45.0) is False

    def test_very_poor_accuracy(self) -> None:
        assert check_accuracy(150.0) is False

    def test_zero_accuracy_is_invalid(self) -> None:
        assert check_accuracy(0.0) is False

    def test_negative_accuracy_is_invalid(self) -> None:
        assert check_accuracy(-1.0) is False


class TestValidateGpsRow:
    def test_valid_row(self) -> None:
        result = validate_gps_row(-6.2088, 106.8456, 5.0)
        assert result.has_coordinates is True
        assert result.in_bounds is True
        assert result.accuracy_ok is True

    def test_missing_coordinates(self) -> None:
        result = validate_gps_row(None, None, None)
        assert result.has_coordinates is False

    def test_out_of_bounds(self) -> None:
        result = validate_gps_row(35.6762, 139.6503, 5.0)
        assert result.in_bounds is False

    def test_missing_accuracy(self) -> None:
        result = validate_gps_row(-6.2088, 106.8456, None)
        assert result.accuracy_ok is False


class TestAddGpsFlags:
    def test_adds_flag_columns(self, sample_df: pd.DataFrame) -> None:
        result = add_gps_flags(sample_df)
        assert "gps_has_coordinates" in result.columns
        assert "gps_in_bounds" in result.columns
        assert "gps_accuracy_ok" in result.columns

    def test_does_not_mutate_original(self, sample_df: pd.DataFrame) -> None:
        original_cols = list(sample_df.columns)
        add_gps_flags(sample_df)
        assert list(sample_df.columns) == original_cols

    def test_detects_out_of_bounds(self, sample_df: pd.DataFrame) -> None:
        result = add_gps_flags(sample_df)
        assert not result["gps_in_bounds"].all()
