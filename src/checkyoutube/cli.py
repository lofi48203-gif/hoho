"""``checkyoutube`` command-line entry point."""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from typing import IO

import click
from rich.console import Console

from . import __version__
from .extractor import CheckYoutubeError, fetch_video_info
from .render import render

_HELP = """Look up a YouTube video and print its metadata.

TARGET can be either a full YouTube URL (watch, youtu.be, shorts, embed)
or a bare 11-character video ID, e.g. dQw4w9WgXcQ.
"""


@click.command(help=_HELP)
@click.argument("target", metavar="TARGET")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    help="Print the metadata as a JSON object instead of the styled UI.",
)
@click.option(
    "--no-color",
    is_flag=True,
    help="Disable ANSI colour and styling (useful for pipes and CI).",
)
@click.version_option(__version__, prog_name="checkyoutube")
def main(target: str, as_json: bool, no_color: bool) -> None:
    """Resolve ``target`` and print its metadata to stdout."""
    _run(target=target, as_json=as_json, no_color=no_color, stdout=sys.stdout, stderr=sys.stderr)


def _run(*, target: str, as_json: bool, no_color: bool, stdout: IO[str], stderr: IO[str]) -> None:
    """Implementation used by the CLI and by the unit tests."""
    try:
        info = fetch_video_info(target)
    except CheckYoutubeError as exc:
        error_console = Console(file=stderr, no_color=no_color, force_terminal=not no_color)
        error_console.print(f"[bold red]error[/]: {exc}")
        raise SystemExit(1) from exc

    if as_json:
        payload = asdict(info)
        payload["watch_url"] = info.watch_url
        stdout.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        return

    console = Console(file=stdout, no_color=no_color, force_terminal=not no_color)
    render(info, console=console)
