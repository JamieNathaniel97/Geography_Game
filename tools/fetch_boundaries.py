"""Downloads geoBoundaries (gbOpen, CC BY 4.0 or similar: the licence is saved with each file) for country maps whose
Natural Earth divisions are out of date (jobs/overnight_v5..v8.md), into tools/downloads/<code>/geoboundaries/:

  <ISO3>_<ADM>.geojson     the boundaries (the simplified file when the full one is very large)
  <ISO3>_<ADM>.json        geoBoundaries' metadata: source, year represented, licence, number of units

  python tools/fetch_boundaries.py            (all in SETS)
  python tools/fetch_boundaries.py KEN ETH    (just those)
Re-running skips what's already there.
"""
import json
import pathlib
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads"
UA = {"User-Agent": "GaiaQuestBuild/1.0 (map quiz data build)"}

# ISO3: (our code, [levels]); ADM1 is the first level, ADM2 the second (the Philippines' provinces)
SETS = {
    "FIN": ("fi", ["ADM1"]), "LVA": ("lv", ["ADM1"]), "UKR": ("ua", ["ADM1"]), "VNM": ("vn", ["ADM1"]),
    "PHL": ("ph", ["ADM1", "ADM2"]), "IDN": ("id", ["ADM1", "ADM2"]), "MAR": ("ma", ["ADM1"]), "KEN": ("ke", ["ADM1"]),
    "ETH": ("et", ["ADM1", "ADM2", "ADM3"]), "NOR": ("no", ["ADM1"]), "HUN": ("hu", ["ADM1"]), "PAK": ("pk", ["ADM1"]), "TUR": ("tr", ["ADM1"]),
}


def get(url, tries=4):
    for a in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300).read()
        except Exception as e:
            print("   retry", str(e)[:80])
            time.sleep(10 * (a + 1))
    raise SystemExit("gave up: " + url)


def main(isos):
    for iso in isos:
        code, levels = SETS[iso]
        out = DL / code / "geoboundaries"
        out.mkdir(parents=True, exist_ok=True)
        for adm in levels:
            gj, mj = out / f"{iso}_{adm}.geojson", out / f"{iso}_{adm}.json"
            if gj.exists() and mj.exists():
                continue
            meta = json.loads(get(f"https://www.geoboundaries.org/api/current/gbOpen/{iso}/{adm}/"))
            mj.write_text(json.dumps(meta, indent=1), encoding="utf8")
            data = get(meta["gjDownloadURL"])
            if len(data) > 40_000_000 and meta.get("simplifiedGeometryGeoJSON"):  # very large: the simplified file
                data = get(meta["simplifiedGeometryGeoJSON"])
            gj.write_bytes(data)
            n = len(json.loads(data)["features"])
            print(f"{iso} {adm}: {n} units, {len(data) // 1024} KB, year {meta.get('boundaryYearRepresented')}, "
                  f"source {str(meta.get('boundarySource'))[:60]}, licence {meta.get('boundaryLicense')}")
            time.sleep(2)


if __name__ == "__main__":
    main(sys.argv[1:] or list(SETS))
