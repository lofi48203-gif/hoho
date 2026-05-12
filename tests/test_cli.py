"""Tests for :mod:`checkyoutube.cli`."""

from __future__ import annotations

import json

import pytest
from click.testing import CliRunner

from checkyoutube import cli, extractor


def test_cli_renders_panel(
    monkeypatch: pytest.MonkeyPatch, sample_info: extractor.VideoInfo
) -> None:
    monkeypatch.setattr(cli, "fetch_video_info", lambda target: sample_info)
    result = CliRunner().invoke(cli.main, ["dQw4w9WgXcQ"])
    assert result.exit_code == 0, result.output
    assert "Never Gonna Give You Up" in result.output
    assert "Rick Astley" in result.output
    assert "CheckYoutube" in result.output  # panel title


def test_cli_json_output(monkeypatch: pytest.MonkeyPatch, sample_info: extractor.VideoInfo) -> None:
    monkeypatch.setattr(cli, "fetch_video_info", lambda target: sample_info)
    result = CliRunner().invoke(cli.main, ["dQw4w9WgXcQ", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["id"] == "dQw4w9WgXcQ"
    assert payload["title"] == "Never Gonna Give You Up"
    assert payload["watch_url"] == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    assert payload["view_count"] == 1_600_000_000


def test_cli_reports_lookup_errors(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(_target: str) -> extractor.VideoInfo:
        raise extractor.VideoLookupError("nope")

    monkeypatch.setattr(cli, "fetch_video_info", fail)
    result = CliRunner().invoke(cli.main, ["bad-input"])
    assert result.exit_code == 1
    # Newer click versions split stderr onto Result.stderr; older versions merge
    # everything into Result.output. Accept either path.
    combined = (result.stderr if result.stderr_bytes else "") + result.output
    assert "nope" in combined


def test_cli_version_flag() -> None:
    result = CliRunner().invoke(cli.main, ["--version"])
    assert result.exit_code == 0
    assert "checkyoutube" in result.output.lower()
