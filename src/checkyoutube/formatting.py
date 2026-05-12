"""Small pure-Python helpers for turning raw API values into human strings."""

from __future__ import annotations

from datetime import date, datetime


def format_count(value: int | None) -> str:
    """Format a non-negative integer with thousands separators.

    Returns ``"—"`` when the value is missing so the UI never shows a bare ``None``.
    """
    if value is None:
        return "—"
    return f"{int(value):,}"


def format_duration(seconds: int | float | None) -> str:
    """Format a duration in seconds as ``H:MM:SS`` or ``M:SS``.

    Returns ``"—"`` when the value is missing or non-positive.
    """
    if seconds is None:
        return "—"
    try:
        total = int(seconds)
    except (TypeError, ValueError):
        return "—"
    if total < 0:
        return "—"
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def format_upload_date(raw: str | None) -> str:
    """Format a ``YYYYMMDD`` string (yt-dlp's ``upload_date``) as ``YYYY-MM-DD``.

    Returns the input unchanged if it does not match the expected layout, and
    ``"—"`` when the value is missing.
    """
    if not raw:
        return "—"
    if len(raw) == 8 and raw.isdigit():
        try:
            parsed = datetime.strptime(raw, "%Y%m%d").date()
        except ValueError:
            return raw
        return parsed.isoformat()
    return raw


def relative_age(raw: str | None, *, today: date | None = None) -> str | None:
    """Return a coarse ``"N days/months/years ago"`` for a ``YYYYMMDD`` string.

    Returns ``None`` when the input cannot be parsed so the caller can omit the line.
    """
    if not raw or len(raw) != 8 or not raw.isdigit():
        return None
    try:
        parsed = datetime.strptime(raw, "%Y%m%d").date()
    except ValueError:
        return None
    reference = today or date.today()
    delta_days = (reference - parsed).days
    if delta_days < 0:
        return None
    if delta_days == 0:
        return "today"
    if delta_days == 1:
        return "yesterday"
    if delta_days < 30:
        return f"{delta_days} days ago"
    if delta_days < 365:
        months = delta_days // 30
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = delta_days // 365
    return f"{years} year{'s' if years != 1 else ''} ago"
