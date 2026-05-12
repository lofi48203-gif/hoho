"""Unit tests for the YouTube Metadata Scraper."""

import json
from unittest.mock import patch

import pytest

from app import app as flask_app, extract_video_id


@pytest.fixture
def client():
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        yield c


class TestExtractVideoId:
    def test_standard_url(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_short_url(self):
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_embed_url(self):
        assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        assert extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_bare_id(self):
        assert extract_video_id("dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_invalid_url(self):
        assert extract_video_id("https://example.com") is None

    def test_empty_string(self):
        assert extract_video_id("") is None


class TestIndexRoute:
    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert b"YouTube Metadata Scraper" in resp.data


class TestScrapeRoute:
    def test_no_urls_returns_400(self, client):
        resp = client.post("/api/scrape", json={"urls": []})
        assert resp.status_code == 400

    @patch("app._innertube_next")
    @patch("app._oembed")
    def test_valid_url_returns_metadata(self, mock_oembed, mock_next, client):
        mock_oembed.return_value = {
            "title": "Test Video",
            "author_name": "TestChannel",
        }
        mock_next.return_value = {
            "contents": {
                "twoColumnWatchNextResults": {
                    "results": {
                        "results": {
                            "contents": [
                                {
                                    "videoPrimaryInfoRenderer": {
                                        "viewCount": {
                                            "videoViewCountRenderer": {
                                                "viewCount": {"simpleText": "1,000 views"},
                                            }
                                        },
                                        "dateText": {"simpleText": "Jun 15, 2023"},
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "engagementPanels": [
                {
                    "engagementPanelSectionListRenderer": {
                        "header": {
                            "engagementPanelTitleHeaderRenderer": {
                                "title": {"runs": [{"text": "Comments"}]},
                                "contextualInfo": {"runs": [{"text": "42"}]},
                            }
                        }
                    }
                }
            ],
        }

        resp = client.post(
            "/api/scrape",
            json={"urls": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"]},
        )
        data = json.loads(resp.data)

        assert resp.status_code == 200
        assert len(data["results"]) == 1
        result = data["results"][0]
        assert result["date"] == "06-15-2023"
        assert result["channel"] == "TestChannel"
        assert result["title"] == "Test Video"
        assert result["views"] == 1000
        assert result["comments"] == "42"

    def test_invalid_url_returns_error_in_result(self, client):
        resp = client.post(
            "/api/scrape",
            json={"urls": ["not-a-youtube-url"]},
        )
        data = json.loads(resp.data)
        assert "error" in data["results"][0]


class TestExportRoute:
    def test_empty_results_returns_400(self, client):
        resp = client.post("/api/export", json={"results": []})
        assert resp.status_code == 400

    def test_export_returns_xlsx(self, client):
        results = [
            {
                "date": "06-15-2023",
                "channel": "TestChannel",
                "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "title": "Test Video",
                "views": 1000,
                "likes": 50,
                "comments": 10,
            }
        ]
        resp = client.post("/api/export", json={"results": results})
        assert resp.status_code == 200
        assert (
            resp.content_type
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert len(resp.data) > 0
