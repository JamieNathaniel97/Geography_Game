"""Makes a single-page preview of the app for publishing as a claude.ai artifact (for testing).

The page has the CSS and JS inlined and loads d3/topojson from a CDN; the data files are copied
next to it. The real app (index.html) is unchanged. Usage:

  python tools/make_preview.py <output folder>
"""
import base64
import json
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



def merge_detail(src, out_data, k=3):
    """Merges a detail level's tiles k×k into one file each, and rewrites the index in the preview's states file."""
    import json, math
    code = src.name[:-len("-detail")]
    states = out_data / f"{code}-states.json"
    fc = json.loads(states.read_text(encoding="utf8"))
    d = fc["detail"]
    big = d["deg"] * k
    groups = {}
    for name, w, s_, e, n in d["tiles"]:
        key = (math.floor(w / big + 1e-9), math.floor(s_ / big + 1e-9))
        groups.setdefault(key, []).append(name)
    (out_data / src.name).mkdir(parents=True, exist_ok=True)

    def lines(g, acc):
        if not g:
            return
        t = g["type"]
        if t == "LineString":
            acc.append(g["coordinates"])
        elif t == "MultiLineString":
            acc.extend(g["coordinates"])
        elif t == "GeometryCollection":
            for x in g["geometries"]:
                lines(x, acc)
    tiles = []
    for (ix, iy), names in sorted(groups.items()):
        feats, coast, borders = [], [], []
        for nm in names:
            t = json.loads((src / f"{nm}.json").read_text(encoding="utf8"))
            feats += t["features"]
            lines(t.get("coast"), coast)
            lines(t.get("borders"), borders)
        name = f"{ix}_{iy}"
        tile = {"type": "FeatureCollection", "features": feats,
                "coast": {"type": "MultiLineString", "coordinates": coast},
                "borders": {"type": "MultiLineString", "coordinates": borders}}
        (out_data / src.name / f"{name}.json").write_text(json.dumps(tile, separators=(",", ":")), encoding="utf8")
        tiles.append([name, ix * big, iy * big, (ix + 1) * big, (iy + 1) * big])
    d["tiles"], d["deg"] = tiles, big
    states.write_text(json.dumps(fc, separators=(",", ":")), encoding="utf8")

def main(out):
    out = pathlib.Path(out)
    (out / "data").mkdir(parents=True, exist_ok=True)
    html = (ROOT / "index.html").read_text(encoding="utf8")
    head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
    body = re.search(r"<body>(.*?)</body>", html, re.S).group(1)
    title = re.search(r"<title>.*?</title>", head).group(0)
    fonts = re.search(r'<link rel="stylesheet" href="https://fonts[^>]*>', head).group(0)
    css = (ROOT / "css" / "app.css").read_text(encoding="utf8").replace("../fonts/", "fonts/")

    def script(m):
        src = m.group(1)
        if src in CDN:
            return f'<script src="{CDN[src]}"></script>'
        return "<script>\n" + (ROOT / src).read_text(encoding="utf8") + "\n</script>"

    body = re.sub(r'<script src="([^"]+)"></script>', script, body)
    # flags go inside the page (the test artifact has a file limit; the real app uses data/flags/)
    # shrunk to 320 px wide here: the page may be at most 16 MB (Mexico's coats of arms alone are 4 MB at full size)
    def small(p):
        from PIL import Image
        import io
        im = Image.open(p)
        if im.width > 320:
            im = im.resize((320, round(im.height * 320 / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "WEBP", quality=82)
        return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()
    flags = {p.stem: small(p) for p in sorted((ROOT / "data" / "flags").glob("*.webp"))}
    for d in sorted(x for x in (ROOT / "data" / "flags").iterdir() if x.is_dir()):  # states, provinces, counties
        flags.update({f"{d.name}/" + p.stem: small(p) for p in sorted(d.glob("*.webp"))})
    # the History games' portraits too (data/people/: 245 files would nearly fill the artifact's 512)
    pdir = ROOT / "data" / "people"
    portraits = {p.stem: small(p) for p in sorted(pdir.glob("*.webp"))} if pdir.exists() else {}
    body = "<script>window.GG_FLAGS=" + json.dumps(flags) + ";window.GG_PORTRAITS=" + json.dumps(portraits) + ";</script>\n" + body
    page = "\n".join([title, '<meta name="claude:viewport-fit-sides" content="cover">', fonts,
                      "<style>\n" + css + "\nhtml,body{height:100%}\n</style>", body])
    (out / "geography-game.html").write_text(page, encoding="utf8")
    for f in ("world-50m.json", "world-110m.json", "countries.json", "relief.jpg", "us-states.json", "states.json", "lakes.json", "tribal-us.json",
              "ca-provinces.json", "provinces.json", "tribal-ca.json",
              "uk-historic.json", "uk-ceremonial.json", "counties-historic.json", "counties-ceremonial.json",
              "uk-nations.json", "uk-nations-info.json", "in-states.json", "in-parts.json", "cn-provinces.json", "cn-parts.json", "ru-regions.json", "ru-parts.json", "ru-history.json", "au-states.json", "au-parts.json", "tribal-au.json", "mx-states.json", "mx-parts.json", "tribal-mx.json", "br-states.json", "br-parts.json", "tribal-br.json", "de-states.json", "de-parts.json", "jp-states.json", "jp-parts.json", "fr-states.json", "fr-parts.json", "it-states.json", "it-parts.json", "es-states.json", "es-parts.json", "esp-states.json", "esp-parts.json", "ng-states.json", "ng-parts.json", "ar-states.json", "ar-parts.json", "at-states.json", "at-parts.json", "cz-states.json", "cz-parts.json", "pl-states.json", "pl-parts.json", "nl-states.json", "nl-parts.json", "be-states.json", "be-parts.json", "ber-states.json", "ber-parts.json", "se-states.json", "se-parts.json", "za-states.json", "za-parts.json", "nz-states.json", "nz-parts.json", "pt-states.json", "pt-parts.json", "co-states.json", "co-parts.json", "ch-states.json", "ch-parts.json", "airport-sets.json", "people.json", "battles.json", "wrecks.json"):
        shutil.copy(ROOT / "data" / f, out / "data" / f)
    if (out / "data" / "relief").exists():
        shutil.rmtree(out / "data" / "relief")
    shutil.copytree(ROOT / "data" / "relief", out / "data" / "relief")
    # the finest relief level (16384 px, ~300 tiles) is left out of the preview: the artifact may hold only 512 files
    ri = json.loads((out / "data" / "relief" / "index.json").read_text(encoding="utf8"))
    ri["levels"] = [lv for lv in ri["levels"] if lv["w"] < 16384]
    (out / "data" / "relief" / "index.json").write_text(json.dumps(ri), encoding="utf8")
    shutil.rmtree(out / "data" / "relief" / "16384", ignore_errors=True)
    # country maps' detail levels (tools/detail.py): their tile folders
    # merged into 9° blocks here (the preview artifact may hold only 512 files; the repo keeps the 3° tiles)
    for d in (ROOT / "data").glob("*-detail"):
        if (out / "data" / d.name).exists():
            shutil.rmtree(out / "data" / d.name)
        merge_detail(d, out / "data")
    (out / "media").mkdir(exist_ok=True)
    for f in (ROOT / "media").glob("Learning_mode_clip*"):
        shutil.copy(f, out / "media" / f.name)
    (out / "fonts").mkdir(exist_ok=True)
    for f in (ROOT / "fonts").glob("*.woff"):
        shutil.copy(f, out / "fonts" / f.name)
    print("preview written to", out)


if __name__ == "__main__":
    main(sys.argv[1])
