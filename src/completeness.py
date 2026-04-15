"""Completeness scoring across required fields."""

from __future__ import annotations

from typing import Sequence

import pandas as pd


REQUIRED_FIELDS: tuple[str, ...] = (
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


def compute_row_completeness(
    row: pd.Series, required: Sequence[str] = REQUIRED_FIELDS
) -> float:
    """Return fraction (0.0–1.0) of required fields that are non-null for a row."""
    present = sum(1 for field in required if field in row.index and pd.notna(row[field]))
    return present / len(required) if required else 0.0


def compute_field_completeness(
    df: pd.DataFrame, required: Sequence[str] = REQUIRED_FIELDS
) -> dict[str, float]:
    """Return per-field completeness rates across the entire dataframe."""
    return {
        field: float(df[field].notna().mean()) if field in df.columns else 0.0
        for field in required
    }


def add_completeness_score(
    df: pd.DataFrame, required: Sequence[str] = REQUIRED_FIELDS
) -> pd.DataFrame:
    """Return a new DataFrame with a completeness_score column appended."""
    scores = [compute_row_completeness(row, required) for _, row in df.iterrows()]
    return df.assign(completeness_score=scores)
