"""Field Data QA Dashboard — Streamlit application for validating KoboToolbox/ODK submissions."""

import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from src.charts import (
    completeness_distribution_chart,
    completeness_heatmap,
    flag_distribution_chart,
    gps_scatter_map,
    submission_timeline_chart,
)
from src.completeness import add_completeness_score, compute_field_completeness
from src.data_loader import get_summary_stats, load_csv, validate_columns
from src.flagging import compute_all_flags, export_flagged_to_csv, get_flag_summary, get_flagged_records
from src.gps_validation import add_gps_flags
from src.photo_metadata import extract_metadata

DEMO_DATA_PATH = Path(__file__).parent / "demo" / "sample_data.csv"


def _initialize_session_state() -> None:
    if "review_status" not in st.session_state:
        st.session_state.review_status = {}


def _load_data() -> pd.DataFrame | None:
    st.sidebar.header("Data Source")
    source = st.sidebar.radio("Choose data source:", ["Upload CSV", "Use demo data"])

    if source == "Use demo data":
        return load_csv(DEMO_DATA_PATH)

    uploaded = st.sidebar.file_uploader("Upload CSV file", type=["csv"])
    if uploaded is not None:
        return load_csv(uploaded)
    return None


def _render_overview(df: pd.DataFrame) -> None:
    st.header("Overview")
    stats = get_summary_stats(df)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Records", stats["total_rows"])
    col2.metric("Submitters", stats["unique_submitters"])
    col3.metric("Unique Plots", stats["unique_plots"])
    col4.metric("Date Range", stats["date_range"])

    missing = validate_columns(df)
    if missing:
        st.warning(f"Missing expected columns: {', '.join(missing)}")


def _render_gps_tab(df: pd.DataFrame) -> None:
    st.subheader("GPS Plausibility")

    if "gps_has_coordinates" in df.columns:
        col1, col2, col3 = st.columns(3)
        total = len(df)
        col1.metric("Has Coordinates", f"{df['gps_has_coordinates'].sum()}/{total}")
        col2.metric("In Indonesia Bounds", f"{df['gps_in_bounds'].sum()}/{total}")
        col3.metric("Accuracy OK", f"{df['gps_accuracy_ok'].sum()}/{total}")

    fig = gps_scatter_map(df)
    st.plotly_chart(fig, use_container_width=True)

    gps_issues = df[
        (df.get("gps_in_bounds", pd.Series(dtype=bool)) == False)  # noqa: E712
        | (df.get("gps_accuracy_ok", pd.Series(dtype=bool)) == False)  # noqa: E712
        | (df.get("gps_has_coordinates", pd.Series(dtype=bool)) == False)  # noqa: E712
    ] if "gps_in_bounds" in df.columns else pd.DataFrame()

    if not gps_issues.empty:
        st.subheader("GPS Issues")
        display_cols = ["submission_id", "submitter", "latitude", "longitude", "gps_accuracy", "gps_in_bounds", "gps_accuracy_ok"]
        display_cols = [c for c in display_cols if c in gps_issues.columns]
        st.dataframe(gps_issues[display_cols], use_container_width=True)


def _render_completeness_tab(df: pd.DataFrame) -> None:
    st.subheader("Completeness Scoring")

    field_comp = compute_field_completeness(df)
    fig_heatmap = completeness_heatmap(field_comp)
    st.plotly_chart(fig_heatmap, use_container_width=True)

    fig_dist = completeness_distribution_chart(df)
    st.plotly_chart(fig_dist, use_container_width=True)

    if "completeness_score" in df.columns:
        avg = df["completeness_score"].mean()
        st.metric("Average Completeness", f"{avg:.0%}")


def _render_photo_tab() -> None:
    st.subheader("Photo Metadata Viewer")
    st.info("Upload a photo to extract EXIF metadata (GPS, timestamp, camera info).")

    uploaded_photo = st.file_uploader("Upload photo", type=["jpg", "jpeg", "png", "tiff"])
    if uploaded_photo is not None:
        st.image(uploaded_photo, caption=uploaded_photo.name, width=400)

        with tempfile.NamedTemporaryFile(suffix=Path(uploaded_photo.name).suffix, delete=False) as tmp:
            tmp.write(uploaded_photo.getvalue())
            tmp_path = tmp.name

        metadata = extract_metadata(tmp_path)
        col1, col2 = st.columns(2)
        with col1:
            st.write("**GPS Coordinates**")
            if metadata.latitude is not None:
                st.write(f"Latitude: {metadata.latitude:.6f}")
                st.write(f"Longitude: {metadata.longitude:.6f}")
            else:
                st.write("No GPS data found")

        with col2:
            st.write("**Camera Info**")
            st.write(f"Timestamp: {metadata.timestamp or 'N/A'}")
            st.write(f"Make: {metadata.camera_make or 'N/A'}")
            st.write(f"Model: {metadata.camera_model or 'N/A'}")


def _render_timeline_tab(df: pd.DataFrame) -> None:
    st.subheader("Submission Timeline")
    fig = submission_timeline_chart(df)
    st.plotly_chart(fig, use_container_width=True)


def _render_flagging_tab(df: pd.DataFrame) -> None:
    st.subheader("Flag & Review")

    flag_summary = get_flag_summary(df)
    if flag_summary:
        fig = flag_distribution_chart(flag_summary)
        st.plotly_chart(fig, use_container_width=True)

    flagged = get_flagged_records(df)
    total_flagged = len(flagged)
    st.metric("Flagged Records", f"{total_flagged}/{len(df)}")

    if not flagged.empty:
        st.subheader("Review Flagged Records")
        for idx, row in flagged.iterrows():
            sub_id = row.get("submission_id", str(idx))
            flags_list = row.get("all_flags", [])
            flags_str = ", ".join(flags_list) if isinstance(flags_list, list) else str(flags_list)

            current_status = st.session_state.review_status.get(sub_id, "Pending")

            with st.expander(f"{sub_id} — {flags_str} [{current_status}]"):
                display_cols = [
                    "submission_id", "submitter", "submission_date", "latitude",
                    "longitude", "gps_accuracy", "plot_id", "species",
                    "completeness_score",
                ]
                display_cols = [c for c in display_cols if c in row.index]
                for col in display_cols:
                    st.write(f"**{col}:** {row[col]}")

                new_status = st.selectbox(
                    "Review status",
                    ["Pending", "Approved", "Rejected", "Needs Resubmission"],
                    key=f"status_{sub_id}",
                    index=["Pending", "Approved", "Rejected", "Needs Resubmission"].index(current_status),
                )
                if new_status != current_status:
                    st.session_state.review_status = {
                        **st.session_state.review_status,
                        sub_id: new_status,
                    }

        st.subheader("Export")
        if st.button("Export flagged records to CSV"):
            with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as tmp:
                export_path = export_flagged_to_csv(df, tmp.name)

            with open(export_path, "rb") as f:
                st.download_button(
                    label="Download CSV",
                    data=f.read(),
                    file_name="flagged_records.csv",
                    mime="text/csv",
                )
    else:
        st.success("No flagged records found.")


def main() -> None:
    """Entry point for the Streamlit app."""
    st.set_page_config(
        page_title="Field Data QA Dashboard",
        page_icon="🌿",
        layout="wide",
    )
    st.title("Field Data QA Dashboard")
    st.caption("Validate field data submissions from KoboToolbox/ODK")

    _initialize_session_state()
    df = _load_data()

    if df is None:
        st.info("Upload a CSV file or select demo data to begin.")
        return

    df = add_gps_flags(df)
    df = add_completeness_score(df)
    df = compute_all_flags(df)

    _render_overview(df)

    tab_gps, tab_complete, tab_photo, tab_timeline, tab_flags = st.tabs(
        ["GPS Validation", "Completeness", "Photo Metadata", "Timeline", "Flag & Review"]
    )

    with tab_gps:
        _render_gps_tab(df)

    with tab_complete:
        _render_completeness_tab(df)

    with tab_photo:
        _render_photo_tab()

    with tab_timeline:
        _render_timeline_tab(df)

    with tab_flags:
        _render_flagging_tab(df)


if __name__ == "__main__":
    main()
