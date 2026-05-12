# YouTube Metadata Scraper

A desktop app that scrapes YouTube video metadata and exports it to an Excel
(`.xlsx`) file. Paste one or more YouTube links, hit **Scrape**, preview the
results in a table, then download a neatly formatted spreadsheet.

Can be built as a **standalone `.exe`** — no Python installation needed to run.

## Features

- Bulk-process multiple YouTube links at once
- Extracts: Date (M-D-Y), Channel Name, YouTube Link, Video Title, View Count,
  Like Count, and Comment Count
- Native desktop window (pywebview) — no browser required
- Clean Bootstrap 5 UI with progress indicator
- One-click Excel export with styled headers and auto-filter
- Single-file `.exe` via PyInstaller

## Quick Start (Development)

```bash
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py          # desktop window
# or
python app.py           # browser mode at http://localhost:5000
```

## Build Standalone .exe (Windows)

```bash
pip install -r requirements.txt
pyinstaller youtube_scraper.spec
```

The executable will be at `dist/YouTubeMetadataScraper.exe`. Double-click to run — no Python required.

### Build on Linux / macOS

Same command; produces a native binary at `dist/YouTubeMetadataScraper`.

## Tech Stack

| Layer     | Technology                     |
| --------- | ------------------------------ |
| Backend   | Flask                          |
| Scraping  | YouTube innertube + oEmbed APIs |
| Excel     | openpyxl                       |
| Desktop   | pywebview + PyInstaller        |
| Frontend  | Bootstrap 5 + vanilla JS       |
