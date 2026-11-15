"""Downloads the flag images into data/flags/<iso3>.svg (used by Learning mode, and by the flag games in build 2).

Flags come from the flag-icons set (https://github.com/lipis/flag-icons, MIT licence), 4:3 versions,
keyed by each country's 2-letter code. Run from the repo root after tools/build_data.py:

  python tools/build_flags.py
"""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
URL = "https://cdn.jsdelivr.net/npm/flag-icons@7.2.3/flags/4x3/{}.svg"


def main():
    countries = json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf8"))
    out = ROOT / "data" / "flags"
    out.mkdir(parents=True, exist_ok=True)
    total = 0
    for c in countries:
        p = out / f"{c['iso']}.svg"
        if not p.exists():
            urllib.request.urlretrieve(URL.format(c["a2"].lower()), p)
        total += p.stat().st_size
    print(f"{len(countries)} flags, {total // 1024} KB")


if __name__ == "__main__":
    main()
