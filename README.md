# CheckYoutube

A small, YouTube-inspired command-line tool that looks up a YouTube video by
URL or ID and prints its title, channel, views, likes, duration, publish date,
and thumbnail — styled with the familiar red accent.

```text
╭─ CheckYoutube ──────────────────────────────────────────── id: dQw4w9WgXcQ ─╮
│                                                                             │
│  ▶ Never Gonna Give You Up                                                  │
│  by Rick Astley ✓                                                           │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Views         1,600,000,000                                                │
│  Likes            17,500,000                                                │
│  Duration              3:33                                                 │
│  Published       2009-10-25  (15 years ago)                                 │
│  ─────────────────────────────────────────────────────────────────────────  │
│  Watch      https://www.youtube.com/watch?v=dQw4w9WgXcQ                     │
│  Thumbnail  https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg            │
│  Channel    https://www.youtube.com/@RickAstleyYT                           │
│                                                                             │
╰─────────────────────────────────────────────────────────────────────────────╯
```

## Features

- Accepts any YouTube URL (`watch`, `youtu.be`, `shorts`, `embed`) or a bare
  11-character video ID.
- No API key required: metadata is sourced via [`yt-dlp`].
- Rich, YouTube-themed terminal output (`▶` play marker, red accent, verified
  check mark, live / age-restricted badges).
- `--json` flag for machine-readable output that's easy to pipe into `jq`.
- `--no-color` flag for clean output in pipes and CI.

## Installation

CheckYoutube targets Python 3.10+.

```bash
pip install git+https://github.com/lofi48203-gif/hoho.git
```

For an isolated install that puts `checkyoutube` on your `PATH`:

```bash
pipx install git+https://github.com/lofi48203-gif/hoho.git
```

### Development install

```bash
git clone https://github.com/lofi48203-gif/hoho.git
cd hoho
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
checkyoutube dQw4w9WgXcQ
checkyoutube https://www.youtube.com/watch?v=dQw4w9WgXcQ
checkyoutube https://youtu.be/dQw4w9WgXcQ --json | jq .view_count
checkyoutube dQw4w9WgXcQ --no-color
```

You can also invoke it as a module:

```bash
python -m checkyoutube dQw4w9WgXcQ
```

### Exit codes

| Code | Meaning                                                          |
|------|------------------------------------------------------------------|
| 0    | Success — metadata printed.                                      |
| 1    | Lookup failed (video unavailable, private, bad URL, network).    |
| 2    | Bad CLI invocation (handled by `click`, e.g. missing argument).  |

## Development

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
```

GitHub Actions runs the same `ruff` and `pytest` jobs on every push and pull
request (see `.github/workflows/ci.yml`).

## Building a Windows `.exe`

To ship a standalone Windows executable similar to the original `CheckYoutube.exe`:

```bash
pip install -e ".[dev]" pyinstaller
pyinstaller --onefile --name CheckYoutube -p src src/checkyoutube/__main__.py
```

The resulting binary lands in `dist/CheckYoutube.exe` and bundles `yt-dlp`,
`rich`, and `click` with the Python interpreter.

## License

MIT — see [`LICENSE`](LICENSE).

[`yt-dlp`]: https://github.com/yt-dlp/yt-dlp
