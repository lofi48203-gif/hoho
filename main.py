"""Desktop entry-point: launches Flask in a background thread and opens a pywebview window."""

import socket
import threading
import time

import webview

from app import app


def _free_port() -> int:
    """Find an available TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _run_flask(port: int) -> None:
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False)


def main() -> None:
    port = _free_port()

    server = threading.Thread(target=_run_flask, args=(port,), daemon=True)
    server.start()

    # Give Flask a moment to bind
    time.sleep(0.5)

    webview.create_window(
        "YouTube Metadata Scraper",
        f"http://127.0.0.1:{port}",
        width=1100,
        height=750,
        min_size=(800, 500),
    )
    webview.start()


if __name__ == "__main__":
    main()
