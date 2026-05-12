"""Tests for :mod:`checkyoutube.formatting`."""

from __future__ import annotations

from datetime import date

import pytest

from checkyoutube.formatting import (
    format_count,
    format_duration,
    format_upload_date,
    relative_age,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "0"),
        (1234, "1,234"),
        (1_600_000_000, "1,600,000,000"),
        (None, "—"),
    ],
)
def test_format_count(value: int | None, expected: str) -> None:
    assert format_count(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "0:00"),
        (9, "0:09"),
        (65, "1:05"),
        (213, "3:33"),
        (3600, "1:00:00"),
        (3661, "1:01:01"),
        (None, "—"),
        (-1, "—"),
        ("not-a-number", "—"),
    ],
)
def test_format_duration(value: object, expected: str) -> None:
    assert format_duration(value) == expected  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("20091025", "2009-10-25"),
        ("20240101", "2024-01-01"),
        ("not-a-date", "not-a-date"),
        ("", "—"),
        (None, "—"),
    ],
)
def test_format_upload_date(value: str | None, expected: str) -> None:
    assert format_upload_date(value) == expected


def test_relative_age_known_dates() -> None:
    today = date(2024, 6, 15)
    assert relative_age("20240615", today=today) == "today"
    assert relative_age("20240614", today=today) == "yesterday"
    assert relative_age("20240601", today=today) == "14 days ago"
    assert relative_age("20240315", today=today) == "3 months ago"
    assert relative_age("20210615", today=today) == "3 years ago"


def test_relative_age_invalid_inputs() -> None:
    assert relative_age(None) is None
    assert relative_age("") is None
    assert relative_age("bad-date") is None
    assert relative_age("20990101", today=date(2024, 1, 1)) is None
