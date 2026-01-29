# SPDX-FileCopyrightText: Copyright (C) 2025 Akshat Kotpalliwar (alias IntegerAlex) <inquiry.akshatkotpalliwar@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

"""Utilities for extracting and formatting metadata about the loaded image."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional

from PIL import ExifTags

try:
    from src.video_utils import is_video_file, get_video_metadata
except ImportError:
    # Video support not available
    is_video_file = None
    get_video_metadata = None

logger = logging.getLogger(__name__)

EXIF_TAGS = {tag_id: name for tag_id, name in ExifTags.TAGS.items()}


def build_metadata_text(image_path: str, image) -> str:
    """
    Construct a detailed metadata string for the image or video, including file system
    details and any EXIF information the image exposes, or video metadata.
    """
    logger.debug("Building metadata text for image: %s", image_path)
    
    # Check if it's a video file
    is_video = False
    video_meta = {}
    if is_video_file is not None and is_video_file(image_path):
        try:
            is_video = True
            video_meta = get_video_metadata(image_path)
            logger.debug("Detected video file, metadata: %s", video_meta)
        except Exception as e:
            logger.debug("Failed to get video metadata: %s", e)
            is_video = False

    details = _collect_metadata(image_path, image)
    
    sections = [
        "FILE INFO",
        f" • File: {details['filename']}",
        f" • Location: {details['abs_path']}",
        f" • Directory: {details['directory']}",
        f" • Size: {details['size_kb']:.1f} KB ({details['size_mb']:.2f} MB)",
        f" • Created: {details['created']}",
        f" • Modified: {details['modified']}",
        "",
    ]

    if is_video and video_meta:
        # Video metadata section
        sections.extend([
            "VIDEO INFO",
            f" • Format: Video ({details['mode']})",
            f" • Dimensions: {details['width']}×{details['height']} px",
            f" • Total Frames: {video_meta.get('total_frames', 0)}",
            f" • FPS: {video_meta.get('fps', 0.0):.2f}",
            f" • Duration: {video_meta.get('duration_formatted', 'Unknown')}",
            f" • Codec: {video_meta.get('codec', 'Unknown')}",
        ])
    else:
        # Image metadata section
        sections.extend([
            "IMAGE INFO",
            f" • Format: {details['format']} ({details['mode']})",
            f" • Dimensions: {details['width']}×{details['height']} px",
            f" • DPI: {details['dpi']}",
        ])

        exif_lines = _format_exif(details["exif"])
        if exif_lines:
            sections.extend(["", "EXIF", *exif_lines])
            logger.debug("Found %d EXIF tags", len(exif_lines))
        else:
            logger.debug("No EXIF data found in image")

    result = "\n".join(sections)
    logger.debug("Metadata text built: %d lines, %d bytes", len(sections), len(result))
    return result


def _collect_metadata(image_path: str, image) -> Dict[str, Any]:
    """Gather raw metadata fields for internal use."""
    logger.debug("Collecting metadata for: %s", image_path)
    abs_path = os.path.abspath(image_path)
    directory = os.path.dirname(abs_path)
    try:
        file_stats = os.stat(abs_path)
        size_kb = file_stats.st_size / 1024
        created = _format_timestamp(file_stats.st_ctime)
        modified = _format_timestamp(file_stats.st_mtime)
        logger.debug("File stats: size=%.2f KB, created=%s, modified=%s", size_kb, created, modified)
    except OSError as exc:
        logger.debug("Error reading file stats: %s", exc)
        size_kb = 0.0
        created = "Unknown"
        modified = "Unknown"

    width, height = image.size
    dpi = image.info.get("dpi", ("Unknown", "Unknown"))
    dpi_text = f"{dpi[0]}×{dpi[1]} dpi" if dpi != ("Unknown", "Unknown") else "Unknown"
    logger.debug("Image dimensions: %dx%d, DPI: %s, format: %s, mode: %s", 
                 width, height, dpi_text, getattr(image, "format", "Unknown"), image.mode)

    exif = _extract_exif(image)
    logger.debug("Extracted %d EXIF tags", len(exif))

    return {
        "filename": os.path.basename(image_path),
        "abs_path": abs_path,
        "directory": directory or ".",
        "format": getattr(image, "format", "Unknown") or "Unknown",
        "mode": image.mode,
        "width": width,
        "height": height,
        "size_kb": size_kb,
        "size_mb": size_kb / 1024,
        "created": created,
        "modified": modified,
        "dpi": dpi_text,
        "exif": exif,
    }


def _format_timestamp(timestamp: float) -> str:
    try:
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError):
        return "Unknown"


def _extract_exif(image) -> Dict[str, str]:
    """Return a subset of EXIF tags in human-readable form."""
    exif_data = {}
    try:
        raw_exif = image.getexif()
        logger.debug("Raw EXIF data retrieved: %d tags", len(raw_exif) if raw_exif else 0)
    except AttributeError:
        logger.debug("Image does not support EXIF (AttributeError)")
        raw_exif = None

    if not raw_exif:
        logger.debug("No EXIF data available")
        return exif_data

    desired_tags = {
        "Make",
        "Model",
        "LensModel",
        "FNumber",
        "ExposureTime",
        "ISOSpeedRatings",
        "FocalLength",
        "DateTimeOriginal",
        "GPSInfo",
    }

    for tag_id, value in raw_exif.items():
        tag_name = EXIF_TAGS.get(tag_id)
        if tag_name in desired_tags:
            formatted_value = _format_exif_value(tag_name, value)
            exif_data[tag_name] = formatted_value
            logger.debug("EXIF tag extracted: %s = %s", tag_name, formatted_value)

    logger.debug("Total desired EXIF tags found: %d", len(exif_data))
    return exif_data


def _format_exif(exif: Dict[str, str]) -> Optional[list[str]]:
    if not exif:
        return None

    lines = []
    mapping = [
        ("Make", "Camera Make"),
        ("Model", "Camera Model"),
        ("LensModel", "Lens"),
        ("FNumber", "Aperture"),
        ("ExposureTime", "Exposure"),
        ("ISOSpeedRatings", "ISO"),
        ("FocalLength", "Focal Length"),
        ("DateTimeOriginal", "Shot Time"),
        ("GPSInfo", "GPS"),
    ]

    for key, label in mapping:
        value = exif.get(key)
        if value:
            lines.append(f" • {label}: {value}")

    return lines


def _format_exif_value(tag_name: str, value: Any) -> str:
    if tag_name == "FNumber":
        try:
            return f"f/{float(value):.1f}"
        except (ValueError, TypeError):
            return str(value)
    if tag_name == "ExposureTime":
        if isinstance(value, tuple) and value[1]:
            return f"{value[0]}/{value[1]}s"
        return f"{value}s"
    if tag_name == "FocalLength":
        if isinstance(value, tuple) and value[1]:
            return f"{value[0]/value[1]:.1f} mm"
        return f"{value} mm"
    if tag_name == "ISOSpeedRatings":
        if isinstance(value, (list, tuple)):
            return ", ".join(str(v) for v in value)
        return str(value)
    if tag_name == "GPSInfo":
        return _format_gps(value)
    return str(value)


def _format_gps(gps_info: Any) -> str:
    """Convert GPS EXIF info into a readable lat/long string."""
    try:
        gps_data = {EXIF_TAGS.get(key, key): val for key, val in gps_info.items()}
        lat = _convert_gps_coordinate(gps_data.get("GPSLatitude"), gps_data.get("GPSLatitudeRef"))
        lon = _convert_gps_coordinate(gps_data.get("GPSLongitude"), gps_data.get("GPSLongitudeRef"))
        if lat is None or lon is None:
            return "Unavailable"
        return f"{lat:.6f}, {lon:.6f}"
    except Exception:  # pylint: disable=broad-except
        return "Unavailable"


def _convert_gps_coordinate(values, ref) -> Optional[float]:
    if not values or not ref:
        return None

    try:
        degrees = values[0][0] / values[0][1]
        minutes = values[1][0] / values[1][1]
        seconds = values[2][0] / values[2][1]
        decimal = degrees + (minutes / 60) + (seconds / 3600)
        if ref in ("S", "W"):
            decimal *= -1
        return decimal
    except Exception:  # pylint: disable=broad-except
        return None

