"""Tests for :mod:`checkyoutube.extractor`."""

from __future__ import annotations

from typing import Any

import pytest

from checkyoutube.extractor import (
    VideoLookupError,
    _pick_thumbnail,
    normalise_target,
    video_info_from_dict,
)


def test_video_info_from_dict_extracts_fields(raw_info: dict[str, Any]) -> None:
    info = video_info_from_dict(raw_info)
    assert info.id == "dQw4w9WgXcQ"
    assert info.title == "Never Gonna Give You Up"
    assert info.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert info.watch_url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert info.channel == "Rick Astley"
    assert info.channel_verified is True
    assert info.view_count == 1_600_000_000
    assert info.like_count == 17_500_000
    assert info.duration == 213
    assert info.upload_date == "20091025"
    assert info.thumbnail == "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
    assert info.is_live is False
    assert info.was_live is False
    assert info.age_limit == 0


def test_video_info_from_dict_falls_back_to_uploader() -> None:
    info = video_info_from_dict(
        {
            "id": "abcdefghijk",
            "title": "Hello",
            "uploader": "Some Channel",
            "uploader_url": "https://example.com/c/some",
            "thumbnail": "https://example.com/thumb.jpg",
        }
    )
    assert info.channel == "Some Channel"
    assert info.channel_url == "https://example.com/c/some"
    assert info.thumbnail == "https://example.com/thumb.jpg"
    assert info.view_count is None
    assert info.like_count is None


def test_video_info_from_dict_rejects_missing_required_fields() -> None:
    with pytest.raises(VideoLookupError):
        video_info_from_dict({"id": "abc", "title": ""})
    with pytest.raises(VideoLookupError):
        video_info_from_dict({"id": "", "title": "Hi"})


def test_pick_thumbnail_prefers_last_with_url() -> None:
    assert (
        _pick_thumbnail(
            {
                "thumbnails": [
                    {"url": "https://example.com/low.jpg"},
                    {"url": "https://example.com/high.jpg"},
                ]
            }
        )
        == "https://example.com/high.jpg"
    )


def test_pick_thumbnail_skips_entries_without_url() -> None:
    assert (
        _pick_thumbnail(
            {
                "thumbnails": [
                    {"url": "https://example.com/only.jpg"},
                    {"width": 1280},
                ],
                "thumbnail": "https://example.com/fallback.jpg",
            }
        )
        == "https://example.com/only.jpg"
    )


def test_pick_thumbnail_falls_back_to_top_level() -> None:
    assert (
        _pick_thumbnail({"thumbnails": [], "thumbnail": "https://example.com/fallback.jpg"})
        == "https://example.com/fallback.jpg"
    )


def test_pick_thumbnail_returns_none_when_missing() -> None:
    assert _pick_thumbnail({}) is None


@pytest.mark.parametrize(
    ("target", "expected"),
    [
        ("dQw4w9WgXcQ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        ("  dQw4w9WgXcQ  ", "https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
        (
            "https://youtu.be/dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
        ),
        (
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s",
        ),
    ],
)
def test_normalise_target(target: str, expected: str) -> None:
    assert normalise_target(target) == expected


def test_normalise_target_rejects_empty_input() -> None:
    with pytest.raises(VideoLookupError):
        normalise_target("   ")
