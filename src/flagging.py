"""Flag and review logic for suspicious field data records."""

from __future__ import annotations

from typing import Sequence

import pandas as pd


FLAG_REASONS = {
    "gps_out_of_bounds": "GPS coordinates outside Indonesia",
    "gps_poor_accuracy": "GPS accuracy exceeds threshold",
    "gps_missing": "Missing GPS coordinates",
    "low_completeness": "Completeness score below 70%",
    "duplicate_plot": "Duplicate plot_id on same date",
}

COMPLETENESS_THRESHOLD = 0.7


def flag_gps_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Return new DataFrame with gps-related flag columns."""
    flags: list[list[str]] = []
    for _, row in df.iterrows():
        row_flags: list[str] = []
        if not row.get("gps_has_coordinates", True):
            row_flags.append("gps_missing")
        elif not row.get("gps_in_bounds", True):
            row_flags.append("gps_out_of_bounds")
        if row.get("gps_has_coordinates", False) and not row.get("gps_accuracy_ok", True):
            row_flags.append("gps_poor_accuracy")
        flags.append(row_flags)
    return df.assign(gps_flags=flags)


def flag_completeness_issues(df: pd.DataFrame) -> pd.DataFrame:
    """Return new DataFrame with completeness flag column."""
    flags = [
        ["low_completeness"] if row.get("completeness_score", 1.0) < COMPLETENESS_THRESHOLD else []
        for _, row in df.iterrows()
    ]
    return df.assign(completeness_flags=flags)


def flag_duplicate_plots(df: pd.DataFrame) -> pd.DataFrame:
    """Return new DataFrame with duplicate plot flag column."""
    if "plot_id" not in df.columns or "submission_date" not in df.columns:
        return df.assign(duplicate_flags=[[] for _ in range(len(df))])

    duplicates = df.duplicated(subset=["plot_id", "submission_date"], keep=False)
    flags = [["duplicate_plot"] if dup else [] for dup in duplicates]
    return df.assign(duplicate_flags=flags)


def compute_all_flags(df: pd.DataFrame) -> pd.DataFrame:
    """Run all flagging checks and merge into a single 'all_flags' column."""
    result = flag_gps_issues(df)
    result = flag_completeness_issues(result)
    result = flag_duplicate_plots(result)

    all_flags = [
        row.get("gps_flags", []) + row.get("completeness_flags", []) + row.get("duplicate_flags", [])
        for _, row in result.iterrows()
    ]
    return result.assign(
        all_flags=all_flags,
        is_flagged=[len(f) > 0 for f in all_flags],
    )


def get_flagged_records(df: pd.DataFrame) -> pd.DataFrame:
    """Return only the flagged records."""
    if "is_flagged" not in df.columns:
        return df.head(0)
    return df[df["is_flagged"]].copy()


def get_flag_summary(df: pd.DataFrame) -> dict[str, int]:
    """Return counts of each flag type across the dataset."""
    if "all_flags" not in df.columns:
        return {}
    all_flags_flat: list[str] = []
    for flags in df["all_flags"]:
        if isinstance(flags, list):
            all_flags_flat.extend(flags)
    summary: dict[str, int] = {}
    for flag in all_flags_flat:
        summary[flag] = summary.get(flag, 0) + 1
    return summary


def export_flagged_to_csv(df: pd.DataFrame, path: str) -> str:
    """Export flagged records to CSV and return the path."""
    flagged = get_flagged_records(df)
    export_cols = [
        c for c in flagged.columns
        if c not in ("gps_flags", "completeness_flags", "duplicate_flags")
    ]
    export_df = flagged[export_cols].copy()
    if "all_flags" in export_df.columns:
        export_df = export_df.assign(
            all_flags=export_df["all_flags"].apply(
                lambda x: "; ".join(x) if isinstance(x, list) else str(x)
            )
        )
    export_df.to_csv(path, index=False)
    return path
