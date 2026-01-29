# SPDX-FileCopyrightText: Copyright (C) 2025 Akshat Kotpalliwar (alias IntegerAlex) <inquiry.akshatkotpalliwar@gmail.com>
# SPDX-License-Identifier: GPL-3.0-only

"""Utilities for video file handling, frame extraction, and metadata extraction."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

try:
    import imageio
except ImportError:
    imageio = None
    logging.getLogger(__name__).warning(
        "imageio package not found. Video support will be unavailable."
    )

from PIL import Image

logger = logging.getLogger(__name__)

VIDEO_EXTENSIONS = {
    '.webm', '.mp4', '.avi', '.mov', '.mkv',
    '.flv', '.wmv', '.m4v', '.3gp', '.ogv'
}


def _get_frame_count(reader) -> int:
    """
    Get total frame count from reader, handling both modern and legacy readers.

    Args:
        reader: imageio reader object

    Returns:
        Total number of frames, or estimated value if cannot be determined
    """
    # Try modern API first
    if hasattr(reader, 'count_frames'):
        try:
            return reader.count_frames()
        except (AttributeError, NotImplementedError, TypeError):
            pass

    # Fallback: try to get from metadata
    try:
        meta = reader.get_meta_data()
        fps = meta.get('fps', 0.0)
        duration = meta.get('duration', 0.0)
        if fps > 0 and duration > 0:
            estimated = int(fps * duration)
            if estimated > 0:
                return estimated
    except (AttributeError, KeyError, TypeError):
        pass

    # If all else fails, return a large estimate to allow frame access
    # User can still navigate frames, just won't know exact total count
    logger.warning("Could not determine exact frame count, using estimate")
    return 10000  # Large estimate to allow frame access


def is_video_file(file_path: str) -> bool:
    """
    Check if a file is a video file based on its extension.

    Args:
        file_path: Path to the file to check

    Returns:
        True if the file extension matches a known video format, False otherwise
    """
    _, ext = os.path.splitext(file_path.lower())
    return ext in VIDEO_EXTENSIONS


def extract_frame_from_video(video_path: str, frame_number: int = 0) -> Image.Image:
    """
    Extract a frame from a video file using imageio.

    Process:
    1. Open video file with imageio.get_reader()
    2. Get total frame count with reader.count_frames()
    3. Validate and clamp frame_number to valid range
    4. Extract frame data with reader.get_data(frame_number)
    5. Convert numpy array to PIL Image using Image.fromarray()
    6. Return PIL Image object

    Args:
        video_path: Path to the video file
        frame_number: Frame number to extract (0-indexed)

    Returns:
        PIL Image object containing the extracted frame

    Raises:
        ImportError: If imageio is not installed
        FileNotFoundError: If video file doesn't exist
        ValueError: If video file cannot be read
    """
    if imageio is None:
        raise ImportError(
            "imageio package is required for video support. "
            "Install it with: pip install imageio imageio-ffmpeg"
        )

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        reader = imageio.get_reader(video_path)
        try:
            total_frames = _get_frame_count(reader)

            # Clamp frame_number to valid range [0, total_frames-1]
            if total_frames > 0:
                frame_number = max(0, min(frame_number, total_frames - 1))

            frame_data = reader.get_data(frame_number)

            # Convert numpy array (RGB format) to PIL Image
            return Image.fromarray(frame_data)
        finally:
            reader.close()
    except Exception as exc:
        logger.error("Failed to extract frame from video: %s", exc)
        raise ValueError(f"Failed to extract frame from video: {exc}") from exc


def get_video_metadata(video_path: str) -> Dict[str, Any]:
    """
    Extract comprehensive video metadata.

    Returns:
        Dictionary containing:
        - total_frames: int - Total number of frames
        - fps: float - Frames per second
        - duration: float - Duration in seconds
        - duration_formatted: str - HH:MM:SS format
        - codec: str - Video codec (vp8, h264, etc.)
        - size: tuple - Resolution (width, height)

    Raises:
        ImportError: If imageio is not installed
        FileNotFoundError: If video file doesn't exist
        ValueError: If video file cannot be read
    """
    if imageio is None:
        raise ImportError(
            "imageio package is required for video support. "
            "Install it with: pip install imageio imageio-ffmpeg"
        )

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        reader = imageio.get_reader(video_path)
        try:
            meta = reader.get_meta_data()

            total_frames = _get_frame_count(reader)
            fps = meta.get('fps', 0.0)
            duration = meta.get('duration', 0.0)

            # Calculate FPS if not available
            if fps == 0.0 and duration > 0 and total_frames > 0:
                fps = total_frames / duration

            # Calculate duration if not available
            if duration == 0.0 and fps > 0 and total_frames > 0:
                duration = total_frames / fps

            # Format duration as HH:MM:SS
            hours = int(duration // 3600)
            minutes = int((duration % 3600) // 60)
            seconds = int(duration % 60)
            duration_formatted = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

            # Extract codec information
            codec = meta.get('codec', meta.get('video_codec', 'Unknown'))

            # Get resolution
            size = meta.get('size', None)
            if size is None:
                first_frame = reader.get_data(0)
                size = (first_frame.shape[1], first_frame.shape[0])

            return {
                'total_frames': total_frames,
                'fps': fps,
                'duration': duration,
                'duration_formatted': duration_formatted,
                'codec': codec,
                'size': size,
            }
        finally:
            reader.close()
    except Exception as exc:
        logger.error("Failed to get video metadata: %s", exc)
        raise ValueError(f"Failed to get video metadata: {exc}") from exc


def extract_multiple_frames(
    video_path: str,
    frame_numbers: List[int],
    max_thumbnail_size: int = 200
) -> List[Image.Image]:
    """
    Extract multiple frames as thumbnails.

    Process:
    1. Open video reader
    2. For each frame number:
       - Extract frame data
       - Convert to PIL Image
       - Create thumbnail using Image.thumbnail() with LANCZOS resampling
    3. Return list of thumbnail images

    Args:
        video_path: Path to the video file
        frame_numbers: List of frame numbers to extract (0-indexed)
        max_thumbnail_size: Maximum size for thumbnails (default: 200)

    Returns:
        List of PIL Image objects (thumbnails)

    Raises:
        ImportError: If imageio is not installed
        FileNotFoundError: If video file doesn't exist
        ValueError: If video file cannot be read
    """
    if imageio is None:
        raise ImportError(
            "imageio package is required for video support. "
            "Install it with: pip install imageio imageio-ffmpeg"
        )

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    try:
        reader = imageio.get_reader(video_path)
        try:
            total_frames = _get_frame_count(reader)
            thumbnails = []

            for frame_num in frame_numbers:
                # Clamp frame number to valid range
                if total_frames > 0:
                    frame_num = max(0, min(frame_num, total_frames - 1))

                frame_data = reader.get_data(frame_num)
                pil_image = Image.fromarray(frame_data)

                # Create thumbnail with high-quality resampling
                pil_image.thumbnail(
                    (max_thumbnail_size, max_thumbnail_size),
                    Image.Resampling.LANCZOS
                )
                thumbnails.append(pil_image)

            return thumbnails
        finally:
            reader.close()
    except Exception as exc:
        logger.error("Failed to extract multiple frames: %s", exc)
        raise ValueError(f"Failed to extract multiple frames: {exc}") from exc
