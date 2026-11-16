"""Downloads all flag images, each in its real proportions (e.g. Switzerland square, Nepal its pennant shape):

  data/flags/<ISO3>.webp              the 197 quiz countries (Learning mode and the flag games)
  data/flags/territories/<ISO3>.webp  dependent territories (Greenland, Puerto Rico, Aruba...), for later builds
  data/flags/us/<code>.webp           the 50 US states and Washington, D.C., for build 3
  data/flags/extra.json               names for the territory and US files

Source: Flagpedia (https://flagpedia.net, served from flagcdn.com, free to use), 640 px wide WebP: about twice the
size flags are shown at, so they stay sharp on high-resolution phones. Run from the repo root after build_data.py:

  python tools/build_flags.py
"""
import json
import pathlib
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads"
OUT = ROOT / "data" / "flags"
URL = "https://flagcdn.com/w640/{}.webp"
HEADERS = {"User-Agent": "GaiaQuestFlagBuilder/1.0 (geography learning app; offline build script)"}

US_STATES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
    "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
    "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
    "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
    "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming", "DC": "Washington, D.C.",
}


def get(code, path):
    """Download one flag (code as flagcdn spells it, e.g. "np" or "us-ca"); retry a couple of times if busy."""
    if path.exists():
        return True
    for attempt in range(3):
        try:
            req = urllib.request.Request(URL.format(code), headers=HEADERS)
            with urllib.request.urlopen(req, timeout=60) as r:
                path.write_bytes(r.read())
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print("no flag for", code)
                return False
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"could not download {code}")


def folder_size(folder):
    files = list(folder.glob("*.webp"))
    return f"{len(files)} flags, {sum(f.stat().st_size for f in files) // 1024} KB"


def main():
    countries = json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf8"))
    OUT.mkdir(parents=True, exist_ok=True)
    for c in countries:
        get(c["a2"].lower(), OUT / f"{c['iso']}.webp")

    # territories: everything in the source country list that isn't a quiz country
    quiz = {c["iso"] for c in countries}
    (OUT / "territories").mkdir(exist_ok=True)
    territories = {}
    for c in json.loads((DL / "world-countries.json").read_text(encoding="utf8")):
        iso3 = "XKX" if c["cca3"] == "UNK" else c["cca3"]
        if iso3 in quiz or not c.get("cca2"):
            continue
        if get(c["cca2"].lower(), OUT / "territories" / f"{iso3}.webp"):
            territories[iso3] = c["name"]["common"]

    (OUT / "us").mkdir(exist_ok=True)
    us = {code: name for code, name in US_STATES.items() if get("us-" + code.lower(), OUT / "us" / f"{code}.webp")}

    (OUT / "extra.json").write_text(json.dumps({"territories": territories, "us": us}, ensure_ascii=False, indent=1), encoding="utf8")
    print("countries:", folder_size(OUT))
    print("territories:", folder_size(OUT / "territories"))
    print("us:", folder_size(OUT / "us"))


if __name__ == "__main__":
    main()
