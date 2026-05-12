"""Flask application for scraping YouTube video metadata and exporting to Excel."""

import io
import re
from datetime import datetime

from flask import Flask, jsonify, render_template, request, send_file
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
import yt_dlp

app = Flask(__name__)


def extract_video_id(url: str) -> str | None:
    """Return the YouTube video ID from a URL, or None if unparseable."""
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/shorts/)"
        r"([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url.strip())
        if match:
            return match.group(1)
    stripped = url.strip()
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", stripped):
        return stripped
    return None


def format_count(value: int | None) -> str:
    """Return a human-readable string for a count, or 'N/A' if unavailable."""
    if value is None:
        return "N/A"
    return f"{value:,}"


def fetch_video_metadata(url: str) -> dict:
    """Fetch metadata for a single YouTube video using yt-dlp."""
    video_id = extract_video_id(url)
    if not video_id:
        return {"error": f"Invalid YouTube URL: {url}", "url": url}

    canonical_url = f"https://www.youtube.com/watch?v={video_id}"

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(canonical_url, download=False)

        upload_date = info.get("upload_date", "")
        if upload_date and len(upload_date) == 8:
            date_obj = datetime.strptime(upload_date, "%Y%m%d")
            formatted_date = date_obj.strftime("%m-%d-%Y")
        else:
            formatted_date = "N/A"

        return {
            "date": formatted_date,
            "channel": info.get("channel", info.get("uploader", "N/A")),
            "url": canonical_url,
            "title": info.get("title", "N/A"),
            "views": info.get("view_count"),
            "likes": info.get("like_count"),
            "comments": info.get("comment_count"),
        }
    except Exception as exc:
        return {"error": str(exc), "url": canonical_url}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/scrape", methods=["POST"])
def scrape():
    """Accept a list of YouTube URLs and return metadata for each."""
    data = request.get_json(silent=True) or {}
    urls = data.get("urls", [])

    if not urls:
        return jsonify({"error": "No URLs provided"}), 400

    results = []
    for url in urls:
        result = fetch_video_metadata(url)
        results.append(result)

    return jsonify({"results": results})


@app.route("/api/export", methods=["POST"])
def export():
    """Accept scraped results and return an .xlsx file."""
    data = request.get_json(silent=True) or {}
    results = data.get("results", [])

    if not results:
        return jsonify({"error": "No results to export"}), 400

    wb = Workbook()
    ws = wb.active
    ws.title = "YouTube Metadata"

    headers = [
        "Date (M-D-Y)",
        "Channel Name",
        "YouTube Link",
        "Video Title",
        "View Count",
        "Like Count",
        "Comment Count",
    ]

    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")

    for col_idx, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_alignment

    for row_idx, item in enumerate(results, 2):
        if "error" in item:
            ws.cell(row=row_idx, column=1, value="Error")
            ws.cell(row=row_idx, column=3, value=item.get("url", ""))
            ws.cell(row=row_idx, column=4, value=item.get("error", ""))
            continue

        ws.cell(row=row_idx, column=1, value=item.get("date", "N/A"))
        ws.cell(row=row_idx, column=2, value=item.get("channel", "N/A"))

        link_cell = ws.cell(row=row_idx, column=3, value=item.get("url", ""))
        link_cell.font = Font(color="0563C1", underline="single")

        ws.cell(row=row_idx, column=4, value=item.get("title", "N/A"))

        views = item.get("views")
        ws.cell(row=row_idx, column=5, value=views if views is not None else "N/A")

        likes = item.get("likes")
        ws.cell(row=row_idx, column=6, value=likes if likes is not None else "N/A")

        comments = item.get("comments")
        ws.cell(row=row_idx, column=7, value=comments if comments is not None else "N/A")

    column_widths = [14, 22, 45, 50, 14, 14, 14]
    for i, width in enumerate(column_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    ws.auto_filter.ref = ws.dimensions

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)

    return send_file(
        buf,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="youtube_metadata.xlsx",
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
