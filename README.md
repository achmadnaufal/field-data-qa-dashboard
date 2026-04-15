# Field Data QA Dashboard

[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-30%2B%20passing-green)](tests/)

Streamlit web app for validating field data submissions from **KoboToolbox/ODK**. Built for NbS/carbon field teams collecting baseline and monitoring data in Indonesia.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py

# 3. Open in browser
# http://localhost:8501
```

## Features

- **GPS Plausibility Checks** — Validates coordinates against Indonesia's bounding box and checks GPS accuracy thresholds
- **Completeness Scoring** — Scores each submission across required fields with per-field and per-row breakdowns
- **Photo Metadata Viewer** — Extracts EXIF GPS coordinates, timestamps, and camera info from uploaded photos
- **Submission Timeline** — Interactive Plotly chart showing submissions over time
- **Flag & Review UI** — Flags suspicious records (out-of-bounds GPS, low completeness, duplicates) with a review workflow
- **Export to CSV** — Download flagged records for offline review or reporting

## Sample Output

Load the included demo data (25 realistic Indonesian field records) to see:

| View | Description |
|------|-------------|
| Overview | Record count, submitter count, date range metrics |
| GPS Validation | Interactive map with in-bounds/out-of-bounds markers |
| Completeness | Per-field bar chart and score distribution histogram |
| Timeline | Daily submission count bar chart |
| Flag & Review | Expandable cards with review status and CSV export |

## Tech Stack

| Component | Library |
|-----------|---------|
| Web framework | Streamlit |
| Data processing | Pandas |
| Charts | Plotly |
| Image processing | Pillow |
| HTTP client | Requests |
| Testing | pytest |

## Project Structure

```
field-data-qa-dashboard/
├── app.py                       # Main Streamlit application
├── src/
│   ├── gps_validation.py        # GPS plausibility checks
│   ├── completeness.py          # Completeness scoring
│   ├── photo_metadata.py        # EXIF metadata extraction
│   ├── flagging.py              # Flag/review logic
│   ├── charts.py                # Interactive Plotly charts
│   └── data_loader.py           # CSV loading and validation
├── demo/
│   └── sample_data.csv          # 25 realistic Indonesian records
├── tests/
│   ├── test_gps_validation.py   # GPS check tests
│   ├── test_completeness.py     # Completeness scoring tests
│   ├── test_photo_metadata.py   # EXIF extraction tests
│   ├── test_flagging.py         # Flagging logic tests
│   ├── test_data_loader.py      # Data loader tests
│   └── test_charts.py           # Chart generation tests
├── docs/
│   └── SCREENSHOTS.md           # App screenshots documentation
├── requirements.txt
├── LICENSE
└── README.md
```

## Running Tests

```bash
pytest tests/ -v
```

## License

[MIT](LICENSE)
