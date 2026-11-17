"""Builds the airport data for the airport code games (Misc_games.md, idea_01):

  data/airports.json  every airport with scheduled passenger flights and a three-letter IATA code, large and medium:
                      [{"code": "LHR", "name": "London Heathrow Airport", "city": "London", "cityFull": null, "iso": "GBR",
                        "ll": [-0.461941, 51.4706], "size": "L", "capital": true}, ...]
                      size: "L" (large) or "M" (medium), as OurAirports grades them
                      city: the source's city with any bracketed detail removed; cityFull keeps the original
                      capital: the airport's city is its country's capital (from data/countries.json)
                      suspended: true for airports kept although they have no scheduled flights now (SUSPENDED_OK)
                      iso: the app's three-letter country code; null for territories that aren't one of the 197

Source: OurAirports (https://ourairports.com/data/), public domain, airports.csv.
Run from the repo root:  python tools/build_airports.py
It reads tools/downloads/ourairports/airports.csv, downloading it first if it isn't there.
"""
import csv
import json
import pathlib
import re
import unicodedata
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads" / "ourairports"
SRC = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv"
OUT = ROOT / "data" / "airports.json"
# Countries whose airports are kept even with no scheduled flights right now (OurAirports marks them as having none).
# Ukraine: airspace closed to passenger flights since February 2022; the user wants its airports in the games.
SUSPENDED_OK = {"UA"}


def fold(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return "".join(ch for ch in s if ch.isalnum())


def main():
    csv_path = DL / "airports.csv"
    if not csv_path.exists():
        DL.mkdir(parents=True, exist_ok=True)
        print("downloading", SRC)
        urllib.request.urlretrieve(SRC, csv_path)

    countries = json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf-8"))
    a2_to_iso = {c["a2"]: c["iso"] for c in countries if c.get("a2")}
    a2_to_iso.setdefault("XK", "UNK")  # Kosovo: OurAirports uses XK
    capitals = {c["iso"]: {fold(x) for x in c["capitals"]} for c in countries}

    out = []
    with open(csv_path, encoding="utf-8") as f:
        for a in csv.DictReader(f):
            code = a["iata_code"].strip().upper()
            if a["type"] not in ("large_airport", "medium_airport"):
                continue
            suspended = a["scheduled_service"] != "yes"
            if suspended and a["iso_country"] not in SUSPENDED_OK:
                continue
            if len(code) != 3 or not code.isalpha():
                continue
            iso = a2_to_iso.get(a["iso_country"])
            full = a["municipality"].strip()
            city = re.sub(r"\s*\(.*?\)", "", full).strip() or full  # "Paris (Roissy-en-France, Val-d'Oise)" -> "Paris"
            out.append({
                "code": code,
                "name": a["name"].strip(),
                "city": city,
                "cityFull": full if full != city else None,
                "iso": iso,
                "ll": [round(float(a["longitude_deg"]), 4), round(float(a["latitude_deg"]), 4)],
                "size": "L" if a["type"] == "large_airport" else "M",
                "capital": bool(iso and city and fold(city) in capitals.get(iso, ())),
                **({"suspended": True} if suspended else {}),
            })

    # one record per code (the source has a few duplicates); large beats medium
    best = {}
    for a in out:
        if a["code"] not in best or (a["size"] == "L" and best[a["code"]]["size"] != "L"):
            best[a["code"]] = a
    out = sorted(best.values(), key=lambda a: a["code"])

    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    large = sum(a["size"] == "L" for a in out)
    print(f"{OUT.relative_to(ROOT)}: {len(out)} airports ({large} large, {len(out) - large} medium)")
    print("countries with no airport here:",
          sorted(c["iso"] for c in countries if not any(a["iso"] == c["iso"] for a in out)))


if __name__ == "__main__":
    main()
