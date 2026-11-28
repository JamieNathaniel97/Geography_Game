"""Downloads the source data for Earth mode, stage 1 (jobs/geoscience.md), into tools/downloads/earth/ (git-ignored):

  pb2002_plates.json, pb2002_boundaries.json, pb2002_steps.json
      the PB2002 plate model (Bird 2003, "An updated digital model of plate boundaries", G3 4(3) 1027) as GeoJSON by
      Hugo Ahlenius (github.com/fraxen/tectonicplates, ODC-By 1.0: credit "Hugo Ahlenius, Nordpil and Peter Bird")
  gvp_holocene.json
      the Smithsonian Global Volcanism Program's Holocene volcanoes (Volcanoes of the World), from its GeoServer;
      free to use with the citation "Global Volcanism Program, Smithsonian Institution, Volcanoes of the World"
  ne_10m_geography_marine_polys.geojson
      Natural Earth's named seas, gulfs, bays and straits (public domain)

  python tools/fetch_earth.py
Re-running skips what's already there.
"""
import json
import pathlib
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tools" / "downloads" / "earth"
UA = {"User-Agent": "GaiaQuestBuild/1.0 (map quiz data build)"}
PB = "https://raw.githubusercontent.com/fraxen/tectonicplates/master/GeoJSON/"
FILES = {
    "pb2002_plates.json": PB + "PB2002_plates.json",
    "pb2002_boundaries.json": PB + "PB2002_boundaries.json",
    "pb2002_steps.json": PB + "PB2002_steps.json",
    "gvp_holocene.json": "https://webservices.volcano.si.edu/geoserver/GVP-VOTW/ows?service=WFS&version=2.0.0&request=GetFeature"
                         "&typeName=GVP-VOTW:Smithsonian_VOTW_Holocene_Volcanoes&outputFormat=application/json",
    "ne_10m_geography_marine_polys.geojson": "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_geography_marine_polys.geojson",
    "pb2002_license.txt": "https://raw.githubusercontent.com/fraxen/tectonicplates/master/LICENSE.md",
}


def get(url, tries=4):
    for a in range(tries):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300).read()
        except Exception as e:
            print("   retry", str(e)[:80])
            time.sleep(10 * (a + 1))
    raise SystemExit("gave up: " + url)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, url in FILES.items():
        f = OUT / name
        if f.exists():
            continue
        data = get(url)
        f.write_bytes(data)
        n = len(json.loads(data).get("features", [])) if name.endswith((".json", ".geojson")) else "-"
        print(f"{name}: {len(data) // 1024} KB, {n} features")
        time.sleep(2)


if __name__ == "__main__":
    main()
