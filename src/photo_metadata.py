"""Photo metadata extraction from EXIF data."""

from __future__ import annotations

from datetime import datetime
from typing import NamedTuple, Optional, Tuple

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


class PhotoMetadata(NamedTuple):
    latitude: Optional[float]
    longitude: Optional[float]
    timestamp: Optional[datetime]
    camera_make: Optional[str]
    camera_model: Optional[str]


def _dms_to_decimal(dms: tuple, ref: str) -> float:
    """Convert GPS DMS (degrees, minutes, seconds) to decimal degrees."""
    degrees = float(dms[0])
    minutes = float(dms[1])
    seconds = float(dms[2])
    decimal = degrees + minutes / 60.0 + seconds / 3600.0
    if ref in ("S", "W"):
        decimal = -decimal
    return decimal


def _extract_gps_from_exif(exif_data: dict) -> Tuple[Optional[float], Optional[float]]:
    """Extract GPS coordinates from EXIF GPS info dict."""
    gps_info_tag = None
    for tag_id, tag_name in TAGS.items():
        if tag_name == "GPSInfo":
            gps_info_tag = tag_id
            break

    if gps_info_tag is None or gps_info_tag not in exif_data:
        return None, None

    gps_info = exif_data[gps_info_tag]
    gps_data: dict[str, object] = {}
    for key in gps_info:
        decoded = GPSTAGS.get(key, key)
        gps_data[decoded] = gps_info[key]

    if "GPSLatitude" not in gps_data or "GPSLongitude" not in gps_data:
        return None, None

    lat = _dms_to_decimal(
        gps_data["GPSLatitude"],  # type: ignore[arg-type]
        str(gps_data.get("GPSLatitudeRef", "N")),
    )
    lon = _dms_to_decimal(
        gps_data["GPSLongitude"],  # type: ignore[arg-type]
        str(gps_data.get("GPSLongitudeRef", "E")),
    )
    return lat, lon


def _extract_datetime_from_exif(exif_data: dict) -> Optional[datetime]:
    """Extract timestamp from EXIF data."""
    for tag_id, tag_name in TAGS.items():
        if tag_name == "DateTimeOriginal" and tag_id in exif_data:
            try:
                return datetime.strptime(str(exif_data[tag_id]), "%Y:%m:%d %H:%M:%S")
            except (ValueError, TypeError):
                return None
    return None


def extract_metadata(image_path: str) -> PhotoMetadata:
    """Extract GPS, timestamp, and camera info from an image file."""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()  # type: ignore[attr-defined]
        if exif_data is None:
            return PhotoMetadata(None, None, None, None, None)

        lat, lon = _extract_gps_from_exif(exif_data)
        timestamp = _extract_datetime_from_exif(exif_data)

        decoded: dict[str, object] = {}
        for tag_id, value in exif_data.items():
            tag = TAGS.get(tag_id, tag_id)
            decoded[tag] = value

        return PhotoMetadata(
            latitude=lat,
            longitude=lon,
            timestamp=timestamp,
            camera_make=str(decoded.get("Make")) if "Make" in decoded else None,
            camera_model=str(decoded.get("Model")) if "Model" in decoded else None,
        )
    except Exception:
        return PhotoMetadata(None, None, None, None, None)
