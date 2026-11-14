"""Makes a single-page preview of the app for publishing as a claude.ai artifact (for testing).

The page has the CSS and JS inlined and loads d3/topojson from a CDN; the data files are copied
next to it. The real app (index.html) is unchanged. Usage:

  python tools/make_preview.py <output folder>
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CDN = {
    "vendor/d3.min.js": "https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js",
    "vendor/topojson-client.min.js": "https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js",
    "vendor/d3-geo-projection.min.js": "https://cdn.jsdelivr.net/npm/d3-geo-projection@4.0.0/dist/d3-geo-projection.min.js",
}


def main(out):
    out = pathlib.Path(out)
    (out / "data").mkdir(parents=True, exist_ok=True)
    html = (ROOT / "index.html").read_text(encoding="utf8")
    head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
    body = re.search(r"<body>(.*?)</body>", html, re.S).group(1)
    title = re.search(r"<title>.*?</title>", head).group(0)
    fonts = re.search(r'<link rel="stylesheet" href="https://fonts[^>]*>', head).group(0)
    css = (ROOT / "css" / "app.css").read_text(encoding="utf8")

    def script(m):
        src = m.group(1)
        if src in CDN:
            return f'<script src="{CDN[src]}"></script>'
        return "<script>\n" + (ROOT / src).read_text(encoding="utf8") + "\n</script>"

    body = re.sub(r'<script src="([^"]+)"></script>', script, body)
    page = "\n".join([title, '<meta name="claude:viewport-fit-sides" content="cover">', fonts,
                      "<style>\n" + css + "\nhtml,body{height:100%}\n</style>", body])
    (out / "geography-game.html").write_text(page, encoding="utf8")
    for f in ("world-50m.json", "world-110m.json", "countries.json", "relief.jpg"):
        shutil.copy(ROOT / "data" / f, out / "data" / f)
    if (out / "data" / "relief").exists():
        shutil.rmtree(out / "data" / "relief")
    shutil.copytree(ROOT / "data" / "relief", out / "data" / "relief")
    print("preview written to", out)


if __name__ == "__main__":
    main(sys.argv[1])
