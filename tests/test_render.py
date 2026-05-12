"""Tests for :mod:`checkyoutube.render`."""

from __future__ import annotations

import io

from rich.console import Console

from checkyoutube.extractor import VideoInfo, video_info_from_dict
from checkyoutube.render import render


def _capture(info: VideoInfo) -> str:
    buffer = io.StringIO()
    console = Console(file=buffer, width=80, color_system=None, force_terminal=False, record=True)
    render(info, console=console)
    return console.export_text()


def test_render_includes_title_channel_and_stats(sample_info: VideoInfo) -> None:
    output = _capture(sample_info)
    assert "Never Gonna Give You Up" in output
    assert "Rick Astley" in output
    assert "1,600,000,000" in output  # views are formatted with commas
    assert "17,500,000" in output  # likes
    assert "3:33" in output  # 213-second duration
    assert "2009-10-25" in output  # formatted upload date


def test_render_shows_watch_url_and_thumbnail(sample_info: VideoInfo) -> None:
    output = _capture(sample_info)
    assert "https://www.youtube.com/watch?v=dQw4w9WgXcQ" in output
    assert "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg" in output


def test_render_marks_live_videos() -> None:
    live = video_info_from_dict(
        {
            "id": "liveabcdefg",
            "title": "Live right now",
            "channel": "Streamer",
            "is_live": True,
        }
    )
    assert "LIVE" in _capture(live)


def test_render_marks_18plus_videos() -> None:
    restricted = video_info_from_dict(
        {
            "id": "restrictedX",
            "title": "Age restricted clip",
            "channel": "Studio",
            "age_limit": 18,
        }
    )
    assert "18+" in _capture(restricted)


def test_render_handles_missing_metadata() -> None:
    minimal = video_info_from_dict({"id": "minimalvid1", "title": "Just a title"})
    output = _capture(minimal)
    assert "Just a title" in output
    assert "Unknown channel" in output
    # Missing numeric fields are rendered as an em dash so the layout is preserved.
    assert "—" in output
