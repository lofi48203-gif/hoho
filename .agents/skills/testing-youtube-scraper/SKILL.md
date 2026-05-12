---
name: testing-youtube-scraper
description: Test the YouTube metadata scraper Flask app end-to-end. Use when verifying scraping, UI, or Excel export changes.
---

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Start the Flask server: `python app.py` (runs on port 5000)
3. Verify server is up: `curl -s -o /dev/null -w '%{http_code}' http://localhost:5000` should return 200
4. If port 5000 is occupied by a stale process: `fuser -k 5000/tcp` then restart

## Test URLs

Use these well-known YouTube videos for consistent test data:
- `https://www.youtube.com/watch?v=dQw4w9WgXcQ` (Rick Astley - Never Gonna Give You Up)
- `https://youtu.be/jNQXAC9IVRw` (Me at the zoo — first YouTube video)
- `https://www.youtube.com/watch?v=9bZkp7q19f0` (PSY - Gangnam Style)

For invalid URL testing: `https://www.youtube.com/watch?v=INVALID_VIDEO_ID_123`

## Key Test Scenarios

### 1. Bulk Scrape
- Paste multiple URLs into the textarea (one per line)
- Counter below textarea should update (e.g., "3 links entered")
- Click "Scrape Metadata" — progress bar appears during processing
- Results table shows 7 columns: Date, Channel, Link, Title, Views, Likes, Comments
- All fields should be populated (not "N/A") for valid videos

### 2. Excel Export
- After scraping, click "Export to Excel"
- File `youtube_metadata.xlsx` downloads
- Verify with openpyxl: headers are bold with red background, data types correct
- View Count and Like Count should be integers; Comment Count may be abbreviated string

### 3. Invalid URL Handling
- Enter an invalid YouTube URL and scrape
- Row should show "N/A" for all metadata fields
- App should not crash or show error page

## Known Behaviors

- **Comment counts are abbreviated**: YouTube's innertube API returns display strings like "2.4M", "10M" rather than exact integers. This is expected.
- **Textarea placeholder text**: The textarea has placeholder URLs that look like real content but aren't. The link counter will show "0 links entered" until you actually type/paste URLs.
- **Browser form caching**: Chrome may restore previous textarea content on refresh, but the JS counter won't update. Use the Clear button or type fresh to trigger input events.
- **No API key required**: The scraper uses public YouTube innertube + oEmbed endpoints.
- **yt-dlp won't work**: YouTube blocks yt-dlp in server environments. The app uses direct HTTP requests to YouTube's APIs instead.

## Unit Tests

Run with: `python -m pytest tests/ -v` (13 tests, all should pass)

## Devin Secrets Needed

None — no API keys or credentials required.
