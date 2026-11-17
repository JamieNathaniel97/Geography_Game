"""Downloads the source data for new country maps into tools/downloads/<code>/ (git-ignored), ready for their build
scripts and plans (jobs/download_new_countries.md).

For each country:
  wikidata.json       every first- (and second-) level division with an ISO 3166-2 code (Wikidata): its kinds,
                      English and local Wikipedia titles, flag and coat of arms files, capital, and whether it's dissolved
  wiki/en/, wiki/<local>/   each division's Wikipedia article (raw wikitext), the sources for the Learning card facts
  wiki/lists/         the country's list articles (census figures, areas, capitals) as raw wikitext
  flags/, coats/      flags and coats of arms from Wikimedia Commons (500 px PNG renders: a standard thumbnail width)
  coast_f.geojson     full-resolution shoreline (GSHHG 2.3.7, level f, about 100 m): land (L1) and lakes (L2), clipped
                      to the country's windows. New country maps use it as standard (PLAN.md, "High-resolution coasts").

  python tools/fetch_country_data.py jp de fr it es ng ar     (all steps)
  python tools/fetch_country_data.py --coast-only mx br        (just the shoreline)
  python tools/fetch_country_data.py --extras jp de fr it es ng ar   (also the card-fact sources: extras.json and
      wiki/lists/, census articles, Nigeria's seals in seals/, the Japanese font in tools/downloads/fonts/)
Re-running skips files already downloaded.
"""
import argparse
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads"
UA = {"User-Agent": "GaiaQuestBuild/1.0 (map quiz data build)"}
GSHHG = DL / "uk" / "gshhg-shp-2.3.7.zip"

# code: name, ISO 3166-2 prefix, local Wikipedia language, list articles, windows (lon/lat boxes) for the shoreline
COUNTRIES = {
    "jp": ("Japan", "JP-", "ja", ["Prefectures of Japan", "List of Japanese prefectures by population", "Regions of Japan"],
           [(122, 23.5, 154.5, 46)]),
    "de": ("Germany", "DE-", "de", ["States of Germany"], [(5, 47, 15.5, 55.2)]),
    "fr": ("France", "FR-", "fr", ["Regions of France", "Departments of France", "List of French departments by population"],
           [(-5.5, 41.2, 10, 51.2), (-61.9, 15.8, -60.9, 16.6), (-61.3, 14.3, -60.7, 15),
            (-54.7, 2, -51.5, 5.9), (55.1, -21.5, 56, -20.8), (44.9, -13.1, 45.4, -12.5)]),
    "it": ("Italy", "IT-", "it", ["Regions of Italy", "Provinces of Italy"], [(6.5, 35.4, 18.6, 47.1)]),
    "es": ("Spain", "ES-", "es", ["Autonomous communities of Spain", "Provinces of Spain"],
           [(-9.4, 35.1, 4.4, 43.9), (-18.3, 27.5, -13.3, 29.5)]),
    "ng": ("Nigeria", "NG-", None, ["States of Nigeria"], [(2.6, 4.2, 14.7, 13.9)]),
    "ar": ("Argentina", "AR-", "es", ["Provinces of Argentina"], [(-73.6, -55.1, -53.6, -21.7)]),
    # not built yet: high-resolution shoreline only (their other data was fetched before)
    "mx": ("Mexico", None, None, [], [(-118.5, 14.4, -86.6, 32.8)]),
    "br": ("Brazil", None, None, [], [(-74.1, -33.8, -28.6, 5.4)]),
}


def get_json(url, tries=6):
    for a in range(tries):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120))
        except Exception as e:
            print("   retry", str(e)[:80])
            time.sleep(20 * (a + 1))
    raise SystemExit("gave up: " + url[:120])


def wikidata(prefix):
    q = f'''SELECT ?item ?iso ?label ?kindLabel ?en ?local ?flag ?coa ?capLabel ?end WHERE {{
      ?item wdt:P300 ?iso . FILTER(STRSTARTS(?iso, "{prefix}"))
      OPTIONAL {{ ?item wdt:P31 ?kind }} OPTIONAL {{ ?item wdt:P41 ?flag }} OPTIONAL {{ ?item wdt:P94 ?coa }}
      OPTIONAL {{ ?item wdt:P36 ?cap }} OPTIONAL {{ ?item wdt:P576 ?end }}
      OPTIONAL {{ ?en schema:about ?item ; schema:isPartOf <https://en.wikipedia.org/> }}
      OPTIONAL {{ ?local schema:about ?item ; schema:isPartOf ?site . ?site wikibase:wikiGroup "wikipedia" .
                 FILTER(?site != <https://en.wikipedia.org/>) }}
      ?item rdfs:label ?label . FILTER(LANG(?label) = "en")
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}'''
    rows = get_json("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q))["results"]["bindings"]
    out = {}
    for r in rows:
        v = lambda k: r[k]["value"] if k in r else None
        d = out.setdefault(v("iso"), {"iso": v("iso"), "qid": v("item").rsplit("/", 1)[1], "name": v("label"), "kinds": set(),
                                      "en": None, "local": {}, "flag": None, "coa": None, "capital": set(), "dissolved": False})
        if v("kindLabel"): d["kinds"].add(v("kindLabel"))
        if v("en"): d["en"] = urllib.parse.unquote(v("en").rsplit("/wiki/", 1)[1]).replace("_", " ")
        if v("local"):
            host = urllib.parse.urlparse(v("local")).netloc.split(".")[0]
            d["local"][host] = urllib.parse.unquote(v("local").rsplit("/wiki/", 1)[1]).replace("_", " ")
        if v("flag") and not d["flag"]: d["flag"] = urllib.parse.unquote(v("flag").rsplit("/", 1)[1])
        if v("coa") and not d["coa"]: d["coa"] = urllib.parse.unquote(v("coa").rsplit("/", 1)[1])
        if v("capLabel"): d["capital"].add(v("capLabel"))
        if v("end"): d["dissolved"] = True
    for d in out.values():
        d["kinds"] = sorted(d["kinds"]); d["capital"] = sorted(d["capital"])
    return dict(sorted(out.items()))


def articles(host, titles, folder):
    folder.mkdir(parents=True, exist_ok=True)
    todo = [t for t in titles if t and not (folder / (t.replace("/", "_").replace(":", "_") + ".wiki")).exists()]
    for i in range(0, len(todo), 20):
        q = urllib.parse.urlencode({"action": "query", "prop": "revisions", "rvprop": "content", "rvslots": "main", "format": "json",
                                    "redirects": 1, "titles": "|".join(todo[i:i + 20])})
        data = get_json(f"https://{host}/w/api.php?" + q)["query"]
        back = {}
        for n in data.get("normalized", []) + data.get("redirects", []):
            back[n["to"]] = back.get(n["from"], n["from"])
        for p in data.get("pages", {}).values():
            if "revisions" in p:
                t = back.get(p["title"], p["title"])
                (folder / (t.replace("/", "_").replace(":", "_") + ".wiki")).write_text(p["revisions"][0]["slots"]["main"]["*"], encoding="utf8")
        time.sleep(3)
    return len(list(folder.glob("*.wiki")))


def image(fname, dest):
    if dest.exists():
        return True
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(fname.replace(" ", "_")) + "?width=500"  # a standard Wikimedia thumbnail width (others are rejected)
    for a in range(5):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            time.sleep(1.5)
            return True
        except Exception as e:
            if "404" in str(e):
                print("   missing on Commons:", fname)
                return False
            time.sleep(15 * (a + 1))
    print("   FAILED", fname)
    return False


def coast(code, windows):
    import geopandas as gpd
    import pandas as pd
    out = DL / code / "coast_f.geojson"
    if out.exists():
        return
    parts = []
    for level in ("L1", "L2"):
        for w in windows:
            g = gpd.read_file(f"zip://{GSHHG}!GSHHS_shp/f/GSHHS_f_{level}.shp", bbox=w)
            if len(g):
                g = g.clip(w)
                g["level"] = {"L1": "land", "L2": "lake"}[level]
                parts.append(g[["level", "geometry"]])
    out.parent.mkdir(parents=True, exist_ok=True)
    gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=4326).to_file(out, driver="GeoJSON")
    print(f"   coast: {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("codes", nargs="+")
    ap.add_argument("--coast-only", action="store_true")
    ap.add_argument("--extras", action="store_true", help="also the card-fact sources, census articles, Nigeria's seals, the Japanese font")
    a = ap.parse_args()
    for code in a.codes:
        name, prefix, lang, lists, windows = COUNTRIES[code]
        print(f"== {name}")
        coast(code, windows)
        if a.coast_only or not prefix:
            continue
        d = DL / code
        wd_file = d / "wikidata.json"
        if wd_file.exists():
            parts = json.loads(wd_file.read_text(encoding="utf8"))
        else:
            parts = wikidata(prefix)
            wd_file.write_text(json.dumps(parts, ensure_ascii=False, indent=1), encoding="utf8")
        live = [p for p in parts.values() if not p["dissolved"]]
        print(f"   {len(parts)} divisions with ISO codes ({len(live)} current)")
        articles("en.wikipedia.org", lists, d / "wiki" / "lists")
        n_en = articles("en.wikipedia.org", [p["en"] for p in live], d / "wiki" / "en")
        msg = f"   articles: {n_en} English"
        if lang:
            n_loc = articles(f"{lang}.wikipedia.org", [p["local"].get(lang) for p in live], d / "wiki" / lang)
            msg += f", {n_loc} {lang}"
        print(msg)
        nf = sum(image(p["flag"], d / "flags" / f'{p["iso"]}.png') for p in live if p["flag"])
        nc = sum(image(p["coa"], d / "coats" / f'{p["iso"]}.png') for p in live if p["coa"])
        print(f"   images: {nf} flags, {nc} coats of arms")
        if a.extras:
            extras(code, live)


# ----- extras: the sources for the chosen card facts (jobs/download_new_countries.md, "Still to fetch") -----
# Each entry is a search: the best-matching English Wikipedia article is saved in wiki/lists/ (titles move; a search
# finds the current one). The census entry is the article with the national total for the census year used.
EXTRAS = {
    "jp": ["Demographics of Japan", "Prefectural symbols of Japan", "Yuru-chara", "Provinces of Japan", "Onsen",
           "Meibutsu", "Traditional crafts of Japan", "Japanese dialects", "List of castles in Japan"],
    "de": ["2022 German census", "German dialects", "List of castles in Germany", "States of the Weimar Republic",
           "List of German football champions", "German wine"],
    "fr": ["Demographics of France", "Provinces of France", "List of French cheeses", "French wine",
           "Languages of France", "2016 reform of regions of France"],
    "it": ["2021 Italian census", "List of Italian products with protected designation of origin", "Italian wine",
           "Italian unification", "Languages of Italy", "Regions of Italy"],
    "es": ["Demographics of Spain", "Languages of Spain", "Spanish cuisine", "Fiestas of Spain", "Crown of Castile",
           "Al-Andalus", "Valencian language", "Basque language", "Galician language"],
    "ng": ["2006 Nigerian census", "List of Nigerian state nicknames", "Traditional rulers of Nigeria",
           "Ethnic groups in Nigeria", "Nigerian cuisine"],
    "ar": ["2022 Argentina census", "Regions of Argentina", "List of football clubs in Argentina",
           "Indigenous peoples in Argentina", "Argentine cuisine"],
}
NOTO_JP = "https://github.com/google/fonts/raw/main/ofl/notosansjp/NotoSansJP%5Bwght%5D.ttf"


def search_title(q):
    # a title starting with the words first; else the best full-text match
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "opensearch", "search": q, "limit": 1, "format": "json"})
    r = get_json(url)
    if r[1]:
        return r[1][0]
    url = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({"action": "query", "list": "search", "srsearch": q, "srlimit": 1, "format": "json"})
    hits = get_json(url)["query"]["search"]
    return hits[0]["title"] if hits else None


def extras(code, live):
    d = DL / code
    found = {}
    for q in EXTRAS.get(code, []):
        t = search_title(q)
        found[q] = t
        time.sleep(1)
    titles = [t for t in found.values() if t]
    articles("en.wikipedia.org", titles, d / "wiki" / "lists")
    (d / "extras.json").write_text(json.dumps(found, ensure_ascii=False, indent=1), encoding="utf8")
    print(f"   extras: {len(titles)} of {len(found)} list articles", [q for q, t in found.items() if not t] or "")
    if code == "ng":  # seals and coats of arms from the state articles' infoboxes (Wikidata has few)
        import re
        got, missing = 0, []
        for p in live:
            f = d / "wiki" / "en" / (p["en"].replace("/", "_").replace(":", "_") + ".wiki")
            text = f.read_text(encoding="utf8") if f.exists() else ""
            m = re.search(r"\|\s*(?:image_seal|image_shield|image_coat_of_arms|seal|coat_of_arms)\s*=\s*([^\n|]+\.(?:svg|png|jpe?g|gif))", text, re.I)
            if m and image(m.group(1).strip().replace("File:", ""), d / "seals" / f'{p["iso"]}.png'):
                got += 1
            else:
                missing.append(p["name"])
        print(f"   seals: {got} of {len(live)}; none for", missing)
    if code == "jp":
        font = DL / "fonts" / "NotoSansJP.ttf"
        if not font.exists():
            font.write_bytes(urllib.request.urlopen(urllib.request.Request(NOTO_JP, headers=UA), timeout=180).read())
        print(f"   font: {font.relative_to(ROOT)} ({font.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    main()
