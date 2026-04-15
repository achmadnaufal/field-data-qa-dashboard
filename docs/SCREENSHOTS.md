# Screenshots

Documentation of all pages and views in the Field Data QA Dashboard.

## Overview

The main dashboard overview displays key metrics:

- **Total Records**: Count of all submissions in the dataset
- **Submitters**: Number of unique field team members
- **Unique Plots**: Count of distinct plot IDs
- **Date Range**: Earliest to latest submission date
- **Missing Columns Warning**: Alerts when expected columns are absent

## Tab: GPS Validation

The GPS validation tab provides:

- **Metrics Row**: Counts for coordinates present, in-bounds, and accuracy OK
- **Interactive Map**: Plotly scatter map showing all GPS points on OpenStreetMap tiles, color-coded green (in Indonesia bounds) or red (out of bounds)
- **GPS Issues Table**: Sortable dataframe of all records with GPS problems (missing coordinates, out-of-bounds, poor accuracy)

## Tab: Completeness

The completeness tab shows:

- **Field Completeness Bar Chart**: Horizontal bar chart with per-field completeness percentages, color-coded green (>=90%), yellow (>=70%), or red (<70%)
- **Score Distribution Histogram**: Distribution of row-level completeness scores across all submissions
- **Average Completeness Metric**: Overall dataset average completeness score

## Tab: Photo Metadata

The photo metadata viewer provides:

- **File Upload**: Accepts JPG, JPEG, PNG, and TIFF files
- **Image Preview**: Displays the uploaded photo at 400px width
- **GPS Coordinates**: Extracted latitude and longitude from EXIF data
- **Camera Info**: Timestamp, camera make, and model from EXIF tags

## Tab: Timeline

The submission timeline shows:

- **Daily Bar Chart**: Interactive Plotly bar chart of submission counts per day
- **Hover Details**: Exact date and count on hover
- **Zoom/Pan**: Full Plotly interactivity for exploring date ranges

## Tab: Flag & Review

The flag and review tab provides:

- **Flag Distribution Chart**: Bar chart showing counts of each flag type (GPS out of bounds, poor accuracy, missing GPS, low completeness, duplicate plot)
- **Flagged Records Count**: Total flagged vs. total records metric
- **Review Cards**: Expandable cards for each flagged record showing all fields, current flags, and a review status dropdown (Pending, Approved, Rejected, Needs Resubmission)
- **CSV Export**: Button to export all flagged records with flag descriptions to a downloadable CSV file
