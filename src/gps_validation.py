"""GPS plausibility checks for Indonesian field data."""

from __future__ import annotations

from typing import NamedTuple

import pandas as pd


INDONESIA_BOUNDS = {
    "lat_min": -11.0,
    "lat_max": 6.0,
    "lon_min": 95.0,
    "lon_max": 141.0,
}

MAX_ACCEPTABLE_ACCURACY_M = 30.0


class GpsCheckResult(NamedTuple):
    in_bounds: bool
    accuracy_ok: bool
    has_coordinates: bool


def check_coordinates_in_bounds(lat: float, lon: float) -> bool:
    """Return True if coordinates fall within the Indonesia bounding box."""
    return (
        INDONESIA_BOUNDS["lat_min"] <= lat <= INDONESIA_BOUNDS["lat_max"]
        and INDONESIA_BOUNDS["lon_min"] <= lon <= INDONESIA_BOUNDS["lon_max"]
    )


def check_accuracy(accuracy_m: float) -> bool:
    """Return True if GPS accuracy is within acceptable threshold."""
    return 0 < accuracy_m <= MAX_ACCEPTABLE_ACCURACY_M


def validate_gps_row(
    lat: object, lon: object, accuracy: object
) -> GpsCheckResult:
    """Validate a single row's GPS data, returning a structured result."""
    has_coords = pd.notna(lat) and pd.notna(lon)
    if not has_coords:
        return GpsCheckResult(in_bounds=False, accuracy_ok=False, has_coordinates=False)

    in_bounds = check_coordinates_in_bounds(float(lat), float(lon))

    accuracy_ok = (
        check_accuracy(float(accuracy)) if pd.notna(accuracy) else False
    )

    return GpsCheckResult(
        in_bounds=in_bounds, accuracy_ok=accuracy_ok, has_coordinates=True
    )


def add_gps_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Return a new DataFrame with GPS validation flag columns appended."""
    results = [
        validate_gps_row(row.get("latitude"), row.get("longitude"), row.get("gps_accuracy"))
        for _, row in df.iterrows()
    ]
    return df.assign(
        gps_has_coordinates=[r.has_coordinates for r in results],
        gps_in_bounds=[r.in_bounds for r in results],
        gps_accuracy_ok=[r.accuracy_ok for r in results],
    )
