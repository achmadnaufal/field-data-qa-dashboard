"""Data loading and preprocessing utilities."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd


EXPECTED_COLUMNS: tuple[str, ...] = (
    "submission_id",
    "submitter",
    "submission_date",
    "latitude",
    "longitude",
    "gps_accuracy",
    "plot_id",
    "species",
    "tree_count",
    "dbh_cm",
    "canopy_cover_pct",
    "soil_type",
    "land_use",
    "photo_id",
)

NUMERIC_COLUMNS: tuple[str, ...] = (
    "latitude",
    "longitude",
    "gps_accuracy",
    "tree_count",
    "dbh_cm",
    "canopy_cover_pct",
)


def load_csv(source: str | Path | StringIO) -> pd.DataFrame:
    """Load a CSV file and coerce numeric columns."""
    df = pd.read_csv(source)
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df = df.assign(**{col: pd.to_numeric(df[col], errors="coerce")})
    if "submission_date" in df.columns:
        df = df.assign(submission_date=pd.to_datetime(df["submission_date"], errors="coerce"))
    return df


def validate_columns(df: pd.DataFrame) -> list[str]:
    """Return list of expected columns that are missing from the DataFrame."""
    return [col for col in EXPECTED_COLUMNS if col not in df.columns]


def get_summary_stats(df: pd.DataFrame) -> dict[str, object]:
    """Return summary statistics for the dataset."""
    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "date_range": (
            f"{df['submission_date'].min()} — {df['submission_date'].max()}"
            if "submission_date" in df.columns and not df["submission_date"].isna().all()
            else "N/A"
        ),
        "unique_submitters": (
            int(df["submitter"].nunique()) if "submitter" in df.columns else 0
        ),
        "unique_plots": (
            int(df["plot_id"].nunique()) if "plot_id" in df.columns else 0
        ),
    }
