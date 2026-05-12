"""Thin wrapper around ``yt-dlp`` that returns just the fields we care about.

``yt-dlp`` is the data source because it does not require an API key, handles
URL/ID normalisation for us, and exposes the metadata we need (title, channel,
view/like counts, duration, upload date, and thumbnail).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any


class CheckYoutubeError(Exception):
    """Base class for user-facing errors raised by :mod:`checkyoutube`."""


class VideoLookupError(CheckYoutubeError):
    """Raised when the video cannot be located or its metadata cannot be parsed."""


@dataclass(frozen=True)
class VideoInfo:
    """Normalised subset of the metadata returned by ``yt-dlp``.

    Only fields rendered by the CLI live here. Missing values are represented
    as ``None`` so that :mod:`checkyoutube.formatting` can render placeholders
    consistently.
    """

    id: str
    title: str
    url: str
    channel: str | None
    channel_url: str | None
    channel_verified: bool
    view_count: int | None
    like_count: int | None
    duration: int | None
    upload_date: str | None
    thumbnail: str | None
    is_live: bool
    was_live: bool
    age_limit: int | None

    @property
    def watch_url(self) -> str:
        """Canonical ``https://www.youtube.com/watch?v=…`` URL."""
        return f"https://www.youtube.com/watch?v={self.id}"


_VIDEO_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")


def normalise_target(target: str) -> str:
    """Return a value ``yt-dlp`` can resolve.

    Bare 11-character IDs are expanded to a full watch URL so users can paste
    just an ID (``dQw4w9WgXcQ``) instead of the full URL.
    """
    cleaned = target.strip()
    if not cleaned:
        raise VideoLookupError("No video URL or ID was provided.")
    if _VIDEO_ID_RE.match(cleaned):
        return f"https://www.youtube.com/watch?v={cleaned}"
    return cleaned


def _pick_thumbnail(info: dict[str, Any]) -> str | None:
    """Choose the highest-quality thumbnail available."""
    thumbnails = info.get("thumbnails") or []
    if thumbnails:
        # yt-dlp orders thumbnails from low to high quality; pick the last one
        # with a usable URL.
        for entry in reversed(thumbnails):
            url = entry.get("url") if isinstance(entry, dict) else None
            if url:
                return url
    fallback = info.get("thumbnail")
    return fallback if isinstance(fallback, str) else None


def _to_int(value: Any) -> int | None:
    """Best-effort conversion to ``int``; returns ``None`` for unusable input."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def video_info_from_dict(info: dict[str, Any]) -> VideoInfo:
    """Build a :class:`VideoInfo` from a ``yt-dlp`` ``extract_info`` payload."""
    video_id = info.get("id")
    title = info.get("title") or info.get("fulltitle")
    if not video_id or not title:
        raise VideoLookupError("yt-dlp returned a response with no id or title.")

    return VideoInfo(
        id=str(video_id),
        title=str(title),
        url=str(info.get("webpage_url") or f"https://www.youtube.com/watch?v={video_id}"),
        channel=info.get("channel") or info.get("uploader"),
        channel_url=info.get("channel_url") or info.get("uploader_url"),
        channel_verified=bool(info.get("channel_is_verified")),
        view_count=_to_int(info.get("view_count")),
        like_count=_to_int(info.get("like_count")),
        duration=_to_int(info.get("duration")),
        upload_date=info.get("upload_date"),
        thumbnail=_pick_thumbnail(info),
        is_live=bool(info.get("is_live")),
        was_live=bool(info.get("was_live")),
        age_limit=_to_int(info.get("age_limit")),
    )


def fetch_video_info(target: str) -> VideoInfo:
    """Resolve ``target`` (URL or ID) to a :class:`VideoInfo`.

    Network calls are delegated to ``yt-dlp``. We import it lazily so the help
    output and unit tests do not pay its import cost.
    """
    # Imported lazily: yt-dlp pulls in a lot of submodules at import time.
    from yt_dlp import YoutubeDL  # noqa: PLC0415
    from yt_dlp.utils import DownloadError  # noqa: PLC0415

    url = normalise_target(target)
    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
        "extract_flat": False,
    }
    try:
        with YoutubeDL(options) as ydl:
            raw = ydl.extract_info(url, download=False)
    except DownloadError as exc:
        raise VideoLookupError(_friendly_error(str(exc))) from exc

    if raw is None:
        raise VideoLookupError("yt-dlp returned no metadata for that URL.")

    # Playlists or channels resolve to a list of entries; we only support a
    # single video.
    if raw.get("_type") == "playlist":
        entries = list(raw.get("entries") or [])
        if not entries:
            raise VideoLookupError("That URL resolves to an empty playlist, not a single video.")
        if len(entries) > 1:
            raise VideoLookupError(
                "That URL resolves to a playlist or channel; please pass a single "
                "video URL or ID instead."
            )
        raw = entries[0]

    return video_info_from_dict(raw)


def _friendly_error(message: str) -> str:
    """Map noisy yt-dlp errors into a short sentence for the CLI."""
    lowered = message.lower()
    if "video unavailable" in lowered:
        return "That video is unavailable (it may have been removed or made private)."
    if "private video" in lowered:
        return "That video is private."
    if "is not a valid url" in lowered or "unsupported url" in lowered:
        return "That input does not look like a YouTube video URL or ID."
    return f"Could not fetch video metadata: {message.strip()}"
