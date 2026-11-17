"""Start the Plant Disease Detector and open it in the default web browser."""
import argparse
import logging
import socket
import threading
import webbrowser

from app import create_app
from app.config import DEFAULT_PORT


def find_free_port(start: int) -> int:
    for port in range(start, start + 50):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free port found between %d and %d" % (start, start + 49))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--no-browser", action="store_true", help="do not open the browser automatically")
    args = ap.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    print("Loading model and preparing database ...", flush=True)
    app = create_app()

    port = find_free_port(args.port)
    url = f"http://127.0.0.1:{port}"
    print("\n" + "=" * 60)
    print("  Plant Disease Detector is running")
    print(f"  Open: {url}")
    print("  Keep this window open. Press Ctrl+C to stop.")
    print("=" * 60 + "\n", flush=True)

    if not args.no_browser:
        threading.Timer(1.2, lambda: webbrowser.open(url)).start()

    from waitress import serve
    serve(app, host="127.0.0.1", port=port, threads=4)


if __name__ == "__main__":
    main()
