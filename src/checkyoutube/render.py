"""Render :class:`VideoInfo` instances to the terminal with a YouTube-style theme."""

from __future__ import annotations

from rich.box import ROUNDED
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text

from .extractor import VideoInfo
from .formatting import format_count, format_duration, format_upload_date, relative_age

YOUTUBE_RED = "#FF0000"
MUTED = "grey62"
LABEL_STYLE = "bold white"


def _title_text(info: VideoInfo) -> Text:
    """Bold white title prefixed by a red ▶ play marker."""
    text = Text()
    text.append("▶ ", style=f"bold {YOUTUBE_RED}")
    text.append(info.title, style="bold white")
    return text


def _channel_text(info: VideoInfo) -> Text:
    """Channel line with an optional verified check mark in YouTube red."""
    text = Text()
    text.append("by ", style=MUTED)
    text.append(info.channel or "Unknown channel", style=f"bold {YOUTUBE_RED}")
    if info.channel_verified:
        text.append(" ✓", style=f"bold {YOUTUBE_RED}")
    return text


def _badges(info: VideoInfo) -> Text | None:
    """Return a ``[LIVE] [WAS LIVE] [18+]`` row, or ``None`` if none apply."""
    parts: list[tuple[str, str]] = []
    if info.is_live:
        parts.append(("LIVE", f"bold white on {YOUTUBE_RED}"))
    elif info.was_live:
        parts.append(("WAS LIVE", "bold white on grey35"))
    if info.age_limit and info.age_limit >= 18:
        parts.append(("18+", f"bold {YOUTUBE_RED}"))
    if not parts:
        return None
    text = Text()
    for index, (label, style) in enumerate(parts):
        if index:
            text.append(" ")
        text.append(f" {label} ", style=style)
    return text


def _stats_table(info: VideoInfo) -> Table:
    """Two-column table with right-aligned values, label/value styled separately."""
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left", style=LABEL_STYLE, no_wrap=True)
    table.add_column(justify="right", style="white")

    table.add_row("Views", format_count(info.view_count))
    table.add_row("Likes", format_count(info.like_count))
    table.add_row("Duration", format_duration(info.duration))

    date_str = format_upload_date(info.upload_date)
    age = relative_age(info.upload_date)
    published = date_str if not age else f"{date_str}  [grey62]({age})[/]"
    table.add_row("Published", published)

    return table


def _link(label: str, url: str) -> Text:
    text = Text()
    text.append(f"{label}  ", style=LABEL_STYLE)
    text.append(url, style="link " + url)
    return text


def render(info: VideoInfo, *, console: Console) -> None:
    """Print ``info`` to ``console`` using the YouTube-inspired theme."""
    body_items: list[object] = [_title_text(info), _channel_text(info)]
    badges = _badges(info)
    if badges is not None:
        body_items.append(badges)
    body_items.extend(
        [
            Rule(style=YOUTUBE_RED),
            _stats_table(info),
            Rule(style=MUTED),
            _link("Watch    ", info.watch_url),
        ]
    )
    if info.thumbnail:
        body_items.append(_link("Thumbnail", info.thumbnail))
    if info.channel_url:
        body_items.append(_link("Channel  ", info.channel_url))

    panel = Panel(
        Group(*body_items),
        box=ROUNDED,
        border_style=YOUTUBE_RED,
        padding=(1, 2),
        title=Text("CheckYoutube", style=f"bold {YOUTUBE_RED}"),
        title_align="left",
        subtitle=Text(f"id: {info.id}", style=MUTED),
        subtitle_align="right",
    )
    console.print(panel)
