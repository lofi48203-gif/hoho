# YouTube Metadata Scraper

A web-based tool that scrapes YouTube video metadata and exports it to an Excel
(`.xlsx`) file. Paste one or more YouTube links, hit **Scrape**, preview the
results in a table, then download a neatly formatted spreadsheet.

## Features

- Bulk-process multiple YouTube links at once
- Extracts: Date (M-D-Y), Channel Name, YouTube Link, Video Title, View Count,
  Like Count, and Comment Count
- Clean, responsive Bootstrap 5 UI with progress indicator
- One-click Excel export with styled headers and auto-filter

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open <http://localhost:5000> in your browser.

## Tech Stack

| Layer     | Technology          |
| --------- | ------------------- |
| Backend   | Flask               |
| Scraping  | YouTube innertube + oEmbed APIs |
| Excel     | openpyxl            |
| Frontend  | Bootstrap 5 + vanilla JS |
