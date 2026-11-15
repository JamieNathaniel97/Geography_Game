"""Makes the app icons in icons/ from tools/icon.html (the splash globe, every country lit green).

It serves the repo locally, takes a 1024 px screenshot of icon.html with Chrome or Edge in headless mode,
then scales it down. Run from anywhere:  python tools/make_icons.py
"""
import functools
import http.server
import pathlib
import shutil
import subprocess
import tempfile
import threading

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "google-chrome", "chromium", "msedge",
]


def browser():
    for b in BROWSERS:
        if pathlib.Path(b).exists() or shutil.which(b):
            return b
    raise SystemExit("Chrome or Edge is needed to draw the icon")


def main():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass
    handler = functools.partial(Quiet, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    def render(query):
        with tempfile.TemporaryDirectory() as tmp:
            shot = pathlib.Path(tmp) / "icon.png"
            url = f"http://127.0.0.1:{server.server_port}/tools/icon.html{query}"
            subprocess.run([browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1024,1024",
                            "--virtual-time-budget=5000", f"--screenshot={shot}", url],
                           check=True, capture_output=True, timeout=120)
            return Image.open(shot).convert("RGB").crop((0, 0, 1024, 1024))
    try:
        full, maskable = render(""), render("?maskable")
    finally:
        server.shutdown()
    out = ROOT / "icons"
    out.mkdir(exist_ok=True)
    for img, size, name in ((full, 512, "icon-512.png"), (full, 192, "icon-192.png"), (full, 180, "apple-touch-icon.png"),
                            (maskable, 512, "icon-maskable-512.png"), (maskable, 192, "icon-maskable-192.png")):
        img.resize((size, size), Image.LANCZOS).save(out / name)
    print("icons written")


if __name__ == "__main__":
    main()
