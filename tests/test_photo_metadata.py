"""Tests for photo metadata extraction module."""

import tempfile
from pathlib import Path

import pytest
from PIL import Image

from src.photo_metadata import PhotoMetadata, _dms_to_decimal, extract_metadata


class TestDmsToDecimal:
    def test_north_latitude(self) -> None:
        result = _dms_to_decimal((6, 10, 30.0), "N")
        expected = 6 + 10 / 60 + 30 / 3600
        assert abs(result - expected) < 1e-6

    def test_south_latitude(self) -> None:
        result = _dms_to_decimal((6, 10, 30.0), "S")
        expected = -(6 + 10 / 60 + 30 / 3600)
        assert abs(result - expected) < 1e-6

    def test_east_longitude(self) -> None:
        result = _dms_to_decimal((106, 50, 0.0), "E")
        expected = 106 + 50 / 60
        assert abs(result - expected) < 1e-6

    def test_west_longitude(self) -> None:
        result = _dms_to_decimal((106, 50, 0.0), "W")
        expected = -(106 + 50 / 60)
        assert abs(result - expected) < 1e-6

    def test_zero_coordinates(self) -> None:
        result = _dms_to_decimal((0, 0, 0.0), "N")
        assert result == 0.0


class TestExtractMetadata:
    def test_image_without_exif(self, tmp_path: Path) -> None:
        img = Image.new("RGB", (100, 100), color="red")
        path = tmp_path / "no_exif.jpg"
        img.save(str(path))
        result = extract_metadata(str(path))
        assert isinstance(result, PhotoMetadata)
        assert result.latitude is None
        assert result.longitude is None

    def test_nonexistent_file(self) -> None:
        result = extract_metadata("/nonexistent/path/photo.jpg")
        assert result.latitude is None
        assert result.timestamp is None

    def test_returns_named_tuple(self, tmp_path: Path) -> None:
        img = Image.new("RGB", (100, 100), color="blue")
        path = tmp_path / "test.jpg"
        img.save(str(path))
        result = extract_metadata(str(path))
        assert hasattr(result, "latitude")
        assert hasattr(result, "longitude")
        assert hasattr(result, "timestamp")
        assert hasattr(result, "camera_make")
        assert hasattr(result, "camera_model")

    def test_png_image(self, tmp_path: Path) -> None:
        img = Image.new("RGB", (50, 50), color="green")
        path = tmp_path / "test.png"
        img.save(str(path))
        result = extract_metadata(str(path))
        assert isinstance(result, PhotoMetadata)
