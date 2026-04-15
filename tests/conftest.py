"""Shared test fixtures."""

from pathlib import Path

import pandas as pd
import pytest


DEMO_CSV = Path(__file__).parent.parent / "demo" / "sample_data.csv"


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Load the demo sample data."""
    return pd.read_csv(DEMO_CSV)


@pytest.fixture
def valid_row() -> pd.Series:
    """A single valid Indonesian field data row."""
    return pd.Series({
        "submission_id": "TEST001",
        "submitter": "Test User",
        "submission_date": "2026-03-01",
        "latitude": -6.2088,
        "longitude": 106.8456,
        "gps_accuracy": 5.0,
        "plot_id": "PLT-TEST",
        "species": "Rhizophora apiculata",
        "tree_count": 45,
        "dbh_cm": 18.3,
        "canopy_cover_pct": 72,
        "soil_type": "alluvial",
        "land_use": "mangrove_restoration",
        "photo_id": "IMG_TEST.jpg",
    })


@pytest.fixture
def incomplete_row() -> pd.Series:
    """A row with several missing fields."""
    return pd.Series({
        "submission_id": "TEST002",
        "submitter": "Test User",
        "submission_date": "2026-03-02",
        "latitude": None,
        "longitude": None,
        "gps_accuracy": None,
        "plot_id": "PLT-TEST2",
        "species": None,
        "tree_count": None,
        "dbh_cm": None,
        "canopy_cover_pct": None,
        "soil_type": None,
        "land_use": None,
        "photo_id": None,
    })


@pytest.fixture
def flaggable_df() -> pd.DataFrame:
    """DataFrame with GPS and completeness flags already computed."""
    from src.gps_validation import add_gps_flags
    from src.completeness import add_completeness_score

    df = pd.read_csv(DEMO_CSV)
    df = add_gps_flags(df)
    df = add_completeness_score(df)
    return df
