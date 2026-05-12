"""Shared test fixtures."""

from __future__ import annotations

from typing import Any

import pytest

from checkyoutube.extractor import VideoInfo


@pytest.fixture
def raw_info() -> dict[str, Any]:
    """A representative yt-dlp ``extract_info`` payload for a public video."""
    return {
        "id": "dQw4w9WgXcQ",
        "title": "Never Gonna Give You Up",
        "webpage_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "channel": "Rick Astley",
        "channel_url": "https://www.youtube.com/@RickAstleyYT",
        "channel_is_verified": True,
        "view_count": 1_600_000_000,
        "like_count": 17_500_000,
        "duration": 213,
        "upload_date": "20091025",
        "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
        "thumbnails": [
            {"url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/default.jpg"},
            {"url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"},
            {"url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"},
        ],
        "is_live": False,
        "was_live": False,
        "age_limit": 0,
    }


@pytest.fixture
def sample_info(raw_info: dict[str, Any]) -> VideoInfo:
    """A :class:`VideoInfo` built from :func:`raw_info`."""
    from checkyoutube.extractor import video_info_from_dict

    return video_info_from_dict(raw_info)
