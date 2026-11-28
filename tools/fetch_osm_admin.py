"""Downloads a country's first-level divisions from OpenStreetMap (Overpass API) where no other source is up to date
(jobs/overnight_v12.md: Algeria's 58 wilayas; jobs/overnight_v11.md: Kazakhstan's 20 regions since 2022), into
tools/downloads/<code>/osm/:

  admin<level>.json      the raw Overpass answer (relations with their member ways' geometry)
  admin<level>.geojson   the relations assembled into polygons (shapely polygonize), with name, name:en, ISO3166-2
                         and wikidata tags; only those whose ISO3166-2 code starts with the country's prefix

OpenStreetMap data is © OpenStreetMap contributors, under the ODbL (decided with the user 2026-11-27: credit it on
the map and offer the derived boundary data under the same licence).

  python tools/fetch_osm_admin.py dz kz dz6
Re-running skips the download if admin<level>.json is already there.
"""
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads"
UA = {"User-Agent": "GaiaQuestBuild/1.0 (map quiz data build)"}
API = "https://overpass-api.de/api/interpreter"

# key: (our code, ISO 3166-1, admin_level, the ISO 3166-2 prefix the parts must have: None keeps every unit, neighbours'
# included, for the build to filter). Algeria's daïras (level 6): El Aricha, the 69th wilaya (2025), isn't mapped as a
# wilaya in OSM yet (2026-11-28), so the build cuts it from Tlemcen with its daïra.
SETS = {"dz": ("dz", "DZ", 4, "DZ-"), "kz": ("kz", "KZ", 4, "KZ-"), "dz6": ("dz", "DZ", 6, None)}


def fetch(iso, level):
    q = f'''[out:json][timeout:900];
area["ISO3166-1"="{iso}"]["admin_level"="2"]->.a;
rel(area.a)["boundary"="administrative"]["admin_level"="{level}"];
out geom;'''
    for a in range(4):
        try:
            req = urllib.request.Request(API, data=urllib.parse.urlencode({"data": q}).encode(), headers=UA)
            return urllib.request.urlopen(req, timeout=1000).read()
        except Exception as e:
            print("   retry", str(e)[:80])
            time.sleep(60 * (a + 1))
    raise SystemExit("gave up: " + iso)


def assemble(raw, prefix):
    from shapely.geometry import LineString, mapping
    from shapely.ops import polygonize, unary_union
    feats = []
    for el in raw["elements"]:
        t = el.get("tags", {})
        code = t.get("ISO3166-2", "")
        if el["type"] != "relation" or (prefix and not code.startswith(prefix)):
            continue
        lines = [LineString([(p["lon"], p["lat"]) for p in m["geometry"]])
                 for m in el.get("members", []) if m["type"] == "way" and m.get("role") in ("outer", "") and len(m.get("geometry", [])) > 1]
        polys = list(polygonize(unary_union(lines)))
        if not polys:
            print("   no polygon for", code, t.get("name"))
            continue
        geom = unary_union(polys)
        feats.append({"type": "Feature", "geometry": mapping(geom),
                      "properties": {k: t.get(k) for k in ("name", "name:en", "name:fr", "name:ar", "name:kk", "name:ru", "ISO3166-2", "wikidata", "ref", "admin_level")} | {"osm_id": el["id"]}})
    return {"type": "FeatureCollection", "features": sorted(feats, key=lambda f: (f["properties"]["ISO3166-2"] or "", f["properties"]["name"] or ""))}


def main(codes):
    for code in codes:
        folder, iso, level, prefix = SETS[code]
        out = DL / folder / "osm"
        out.mkdir(parents=True, exist_ok=True)
        rj = out / f"admin{level}.json"
        if not rj.exists():
            rj.write_bytes(fetch(iso, level))
        raw = json.loads(rj.read_text(encoding="utf8"))
        fc = assemble(raw, prefix)
        gj = out / f"admin{level}.geojson"
        gj.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf8")
        names = [f'{f["properties"]["ISO3166-2"] or ""} {f["properties"].get("name:fr") or f["properties"].get("name:en") or f["properties"]["name"]}'.strip() for f in fc["features"]]
        print(f"{code}: {len(fc['features'])} units ({rj.stat().st_size // 1024} KB raw): " + ", ".join(names))
        time.sleep(30)


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    main(sys.argv[1:] or list(SETS))
