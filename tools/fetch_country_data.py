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
import urllib.error
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
    # overnight_v2 (2026-11-18); the local language can be a list (Belgium: Dutch and French)
    "at": ("Austria", "AT-", "de", ["States of Austria"], [(9.3, 46.3, 17.3, 49.1)]),
    "nl": ("Netherlands", "NL-", "nl", ["Provinces of the Netherlands"], [(3.1, 50.6, 7.4, 53.7)]),
    "pl": ("Poland", "PL-", "pl", ["Voivodeships of Poland"], [(13.9, 48.9, 24.3, 55.0)]),
    "cz": ("Czechia", "CZ-", "cs", ["Regions of the Czech Republic"], [(11.9, 48.5, 18.9, 51.1)]),
    "be": ("Belgium", "BE-", ["nl", "fr"], ["Provinces of Belgium", "Communities, regions and language areas of Belgium"],
           [(2.4, 49.4, 6.5, 51.6)]),
    # overnight_v3 (2026-11-18)
    "ch": ("Switzerland", "CH-", ["de", "fr", "it"], ["Cantons of Switzerland"], [(5.8, 45.7, 10.6, 47.9)]),
    "pt": ("Portugal", "PT-", "pt", ["Districts of Portugal"],
           [(-9.6, 36.8, -6.1, 42.2), (-31.4, 36.8, -24.9, 39.8), (-17.4, 32.3, -16.2, 33.2), (-16.2, 29.9, -15.8, 30.2)]),
    "se": ("Sweden", "SE-", "sv", ["Counties of Sweden"], [(10.8, 55.2, 24.3, 69.2)]),
    "za": ("South Africa", "ZA-", None, ["Provinces of South Africa"], [(16.3, -35.0, 33.0, -22.0)]),
    "nz": ("New Zealand", "NZ-", None, ["Regions of New Zealand"], [(166.0, -47.5, 178.8, -34.2), (-177.0, -44.5, -175.9, -43.5)]),
    "co": ("Colombia", "CO-", "es", ["Departments of Colombia"], [(-79.2, -4.3, -66.8, 12.6), (-81.8, 12.4, -81.3, 13.5)]),
    # overnight_v4 (2026-11-18)
    "cl": ("Chile", "CL-", "es", ["Regions of Chile"],
           [(-76.0, -56.2, -66.3, -17.4), (-109.5, -27.3, -109.2, -27.0), (-80.9, -34.0, -78.7, -33.5)]),
    "my": ("Malaysia", "MY-", "ms", ["States and federal territories of Malaysia"], [(99.5, 0.8, 119.5, 7.5)]),
    "kr": ("South Korea", "KR-", "ko", ["Provinces of South Korea", "Administrative divisions of South Korea"], [(124.5, 33.0, 132.0, 38.7)]),
    "pe": ("Peru", "PE-", "es", ["Regions of Peru"], [(-81.5, -18.5, -68.6, 0.1)]),
    "eg": ("Egypt", "EG-", "ar", ["Governorates of Egypt"], [(24.6, 21.5, 37.1, 31.8)]),
    # overnight_v5 (Nordic and Baltic)
    "no": ("Norway", "NO-", "no", ["Counties of Norway"], [(4.0, 57.8, 31.5, 71.3)]),
    "dk": ("Denmark", "DK-", "da", ["Regions of Denmark"], [(7.9, 54.5, 15.3, 57.8)]),
    "fi": ("Finland", "FI-", ["fi", "sv"], ["Regions of Finland"], [(19.0, 59.7, 31.7, 70.2)]),
    "is": ("Iceland", "IS-", "is", ["Regions of Iceland"], [(-24.6, 63.2, -13.4, 66.6)]),
    "ee": ("Estonia", "EE-", "et", ["Counties of Estonia"], [(21.7, 57.5, 28.3, 59.8)]),
    "lv": ("Latvia", "LV-", "lv", ["Planning regions of Latvia", "Administrative divisions of Latvia"], [(20.9, 55.6, 28.3, 58.1)]),
    "lt": ("Lithuania", "LT-", "lt", ["Counties of Lithuania"], [(20.9, 53.8, 26.9, 56.5)]),
    # overnight_v6 (Southern and Eastern Europe)
    "gr": ("Greece", "GR-", "el", ["Regions of Greece"], [(19.3, 34.7, 29.7, 41.8)]),
    "tr": ("Turkey", "TR-", "tr", ["Provinces of Turkey", "Statistical regions of Turkey", "Geographical regions of Turkey"], [(25.6, 35.8, 44.9, 42.2)]),
    "ua": ("Ukraine", "UA-", "uk", ["Oblasts of Ukraine", "Administrative divisions of Ukraine"], [(22.1, 44.3, 40.3, 52.4)]),
    "ro": ("Romania", "RO-", "ro", ["Counties of Romania"], [(20.2, 43.6, 29.8, 48.3)]),
    "hu": ("Hungary", "HU-", "hu", ["Counties of Hungary"], [(16.1, 45.7, 22.9, 48.6)]),
    # overnight_v7 (Asia)
    "vn": ("Vietnam", "VN-", "vi", ["Provinces of Vietnam", "2025 Vietnamese administrative reform"], [(102.1, 8.4, 109.5, 23.4)]),
    "th": ("Thailand", "TH-", "th", ["Provinces of Thailand", "Regions of Thailand"], [(97.3, 5.6, 105.7, 20.5)]),
    "ph": ("Philippines", "PH-", "tl", ["Regions of the Philippines", "Provinces of the Philippines"], [(116.9, 4.5, 126.7, 21.2)]),
    "id": ("Indonesia", "ID-", "id", ["Provinces of Indonesia"], [(94.9, -11.1, 141.1, 6.1)]),
    "pk": ("Pakistan", "PK-", "ur", ["Administrative units of Pakistan"], [(60.8, 23.6, 77.9, 37.1)]),
    # overnight_v8 (Africa and the Middle East)
    "ma": ("Morocco", "MA-", ["ar", "fr"], ["Regions of Morocco"], [(-17.2, 20.7, -0.9, 36.0)]),
    "ke": ("Kenya", "KE-", "sw", ["Counties of Kenya", "Provinces of Kenya"], [(33.8, -4.8, 42.0, 5.1)]),
    "et": ("Ethiopia", "ET-", "am", ["Regions of Ethiopia"], [(32.9, 3.3, 48.1, 15.0)]),
    "sa": ("Saudi Arabia", "SA-", "ar", ["Regions of Saudi Arabia"], [(34.4, 16.3, 55.7, 32.2)]),
    "ir": ("Iran", "IR-", "fa", ["Provinces of Iran"], [(44.0, 25.0, 63.4, 39.8)]),
    # overnight_v9 (Central Europe and the Balkans)
    "hr": ("Croatia", "HR-", "hr", ["Counties of Croatia"], [(13.4, 42.3, 19.5, 46.6)]),
    "rs": ("Serbia", "RS-", "sr", ["Administrative districts of Serbia", "Statistical regions of Serbia", "Kosovo"], [(18.8, 41.8, 23.1, 46.2)]),
    "bg": ("Bulgaria", "BG-", "bg", ["Provinces of Bulgaria"], [(22.3, 41.2, 28.7, 44.3)]),
    "sk": ("Slovakia", "SK-", "sk", ["Regions of Slovakia"], [(16.8, 47.7, 22.6, 49.7)]),
    "si": ("Slovenia", "SI-", "sl", ["Statistical regions of Slovenia", "Municipalities of Slovenia"], [(13.3, 45.4, 16.7, 46.9)]),
    # overnight_v10 (South America and the Caribbean)
    "ve": ("Venezuela", "VE-", "es", ["States of Venezuela", "Federal Dependencies of Venezuela", "Guayana Esequiba"],
           [(-73.4, 0.6, -59.7, 12.3), (-63.7, 15.6, -63.6, 15.7)]),
    "ec": ("Ecuador", "EC-", "es", ["Provinces of Ecuador"], [(-81.1, -5.1, -75.1, 1.5), (-92.1, -1.5, -89.2, 1.7)]),
    "bo": ("Bolivia", "BO-", "es", ["Departments of Bolivia"], [(-69.7, -23.0, -57.4, -9.6)]),
    "uy": ("Uruguay", "UY-", "es", ["Departments of Uruguay"], [(-58.5, -35.1, -53.0, -30.0)]),
    "cu": ("Cuba", "CU-", "es", ["Provinces of Cuba"], [(-85.0, 19.8, -74.1, 23.3)]),
    # overnight_v11 (South and Central Asia)
    "bd": ("Bangladesh", "BD-", "bn", ["Divisions of Bangladesh", "Districts of Bangladesh"], [(88.0, 20.6, 92.7, 26.7)]),
    "lk": ("Sri Lanka", "LK-", ["si", "ta"], ["Provinces of Sri Lanka", "Districts of Sri Lanka"], [(79.5, 5.9, 82.0, 9.9)]),
    "np": ("Nepal", "NP-", "ne", ["Provinces of Nepal"], [(80.0, 26.3, 88.3, 30.5)]),
    "kz": ("Kazakhstan", "KZ-", ["kk", "ru"], ["Regions of Kazakhstan"], [(46.4, 40.5, 87.4, 55.5)]),
    "uz": ("Uzbekistan", "UZ-", "uz", ["Regions of Uzbekistan"], [(55.9, 37.1, 73.2, 45.6)]),
    # overnight_v12 (Africa)
    "dz": ("Algeria", "DZ-", ["ar", "fr"], ["Provinces of Algeria"], [(-8.7, 18.9, 12.0, 37.1)]),
    "tn": ("Tunisia", "TN-", ["ar", "fr"], ["Governorates of Tunisia"], [(7.5, 30.2, 11.6, 37.6)]),
    "gh": ("Ghana", "GH-", None, ["Regions of Ghana"], [(-3.3, 4.7, 1.3, 11.2)]),
    "tz": ("Tanzania", "TZ-", "sw", ["Regions of Tanzania"], [(29.3, -11.8, 40.5, -0.9)]),
    "cd": ("DR Congo", "CD-", "fr", ["Provinces of the Democratic Republic of the Congo"], [(12.2, -13.5, 31.4, 5.4)]),
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
    """A Commons file as a 500 px render (a standard thumbnail width: others are refused). Paced at one every 2.5 s;
    a 429 (too many requests) waits as long as Commons' Retry-After header says (usually 10 minutes), then tries again."""
    if dest.exists():
        return True
    url = "https://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote(fname.replace(" ", "_")) + "?width=500"
    for a in range(3):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60).read()
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
            time.sleep(2.5)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print("   missing on Commons:", fname)
                return False
            if e.code == 429:
                wait = min(int(e.headers.get("Retry-After") or 600), 900) + 5
                print(f"   Commons asks to wait {wait} s")
                time.sleep(wait)
            else:
                time.sleep(10 * (a + 1))
        except Exception:
            time.sleep(10 * (a + 1))
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
    ap.add_argument("--no-images", action="store_true", help="skip the flags and coats of arms (fetch them later: Commons throttles)")
    ap.add_argument("--census", action="store_true", help="only census.json: every dated population of each part and the country (Wikidata)")
    a = ap.parse_args()
    for code in a.codes:
        name, prefix, lang, lists, windows = COUNTRIES[code]
        print(f"== {name}")
        if a.census:
            census(code)
            continue
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
        for lg in ([lang] if isinstance(lang, str) else lang or []):
            n_loc = articles(f"{lg}.wikipedia.org", [p["local"].get(lg) for p in live], d / "wiki" / lg)
            msg += f", {n_loc} {lg}"
        print(msg)
        if not a.no_images:
            nf = sum(image(p["flag"], d / "flags" / f'{p["iso"]}.png') for p in live if p["flag"])
            nc = sum(image(p["coa"], d / "coats" / f'{p["iso"]}.png') for p in live if p["coa"])
            print(f"   images: {nf} flags, {nc} coats of arms")
        if a.extras:
            extras(code, live)


# ----- census: every dated population figure (P1082 with its P585 date) of each current part and of the country, from
# Wikidata, which records the statistics office's figures. The build picks the newest date every part has and checks
# that the parts add up to the country's figure for that date.
COUNTRY_QID = {"at": "Q40", "nl": "Q55", "pl": "Q36", "cz": "Q213", "be": "Q31",
               "ch": "Q39", "pt": "Q45", "se": "Q34", "za": "Q258", "nz": "Q664", "co": "Q739",
               "cl": "Q298", "my": "Q833", "kr": "Q884", "pe": "Q419", "eg": "Q79",
               "no": "Q20", "dk": "Q35", "fi": "Q33", "is": "Q189", "ee": "Q191", "lv": "Q211", "lt": "Q37",
               "gr": "Q41", "tr": "Q43", "ua": "Q212", "ro": "Q218", "hu": "Q28",
               "vn": "Q881", "th": "Q869", "ph": "Q928", "id": "Q252", "pk": "Q843",
               "ma": "Q1028", "ke": "Q114", "et": "Q115", "sa": "Q851", "ir": "Q794",
               "hr": "Q224", "rs": "Q403", "bg": "Q219", "sk": "Q214", "si": "Q215",
               "ve": "Q717", "ec": "Q736", "bo": "Q750", "uy": "Q77", "cu": "Q241",
               "bd": "Q902", "lk": "Q854", "np": "Q837", "kz": "Q232", "uz": "Q265",
               "dz": "Q262", "tn": "Q948", "gh": "Q117", "tz": "Q924", "cd": "Q974"}


def census(code):
    d = DL / code
    parts = json.loads((d / "wikidata.json").read_text(encoding="utf8"))
    qids = {p["qid"]: iso for iso, p in parts.items() if not p["dissolved"]}
    qids[COUNTRY_QID[code]] = "total"
    vals = " ".join("wd:" + q for q in qids)
    q = f"""SELECT ?item ?pop ?date ?methodLabel WHERE {{ VALUES ?item {{ {vals} }}
      ?item p:P1082 ?st . ?st ps:P1082 ?pop . OPTIONAL {{ ?st pq:P585 ?date }} OPTIONAL {{ ?st pq:P459 ?method }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }} }}"""
    rows = get_json("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q))["results"]["bindings"]
    out = {}
    for r in rows:
        iso = qids[r["item"]["value"].rsplit("/", 1)[1]]
        date = r.get("date", {}).get("value", "")[:10]
        out.setdefault(iso, {})[date] = {"pop": int(float(r["pop"]["value"])), "method": r.get("methodLabel", {}).get("value", "")}
    (d / "census.json").write_text(json.dumps(out, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf8")
    print(f"   census: {len(out)} items with population figures")


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
    "at": ["Demographics of Austria", "List of ski resorts in Austria", "Austrian cuisine", "Austrian wine",
           "Austrian German", "List of castles in Austria", "List of World Heritage Sites in Austria"],
    "nl": ["Demographics of the Netherlands", "Land reclamation in the Netherlands", "Flevoland", "Dutch cuisine",
           "Dutch Low Saxon", "West Frisian language", "Limburgish", "List of World Heritage Sites in the Netherlands"],
    "pl": ["2021 Polish census", "Partitions of Poland", "Polish cuisine", "Silesian language", "Kashubian language",
           "List of castles in Poland", "List of World Heritage Sites in Poland"],
    "cz": ["2021 Czech census", "Bohemia", "Moravia", "Czech Silesia", "Czech cuisine", "Moravian dialects",
           "List of castles in the Czech Republic", "List of World Heritage Sites in the Czech Republic"],
    "be": ["Demographics of Belgium", "Communities, regions and language areas of Belgium", "Belgian cuisine",
           "Beer in Belgium", "Walloon language", "List of castles in Belgium", "List of World Heritage Sites in Belgium"],
    "ch": ["Demographics of Switzerland", "Cantons of Switzerland", "Swiss cheeses and dairy products", "Swiss chocolate",
           "Languages of Switzerland", "List of World Heritage Sites in Switzerland", "Swiss cuisine"],
    "pt": ["2021 Portuguese census", "Wine regions of Portugal", "Provinces of Portugal", "Portuguese discoveries",
           "Portuguese cuisine", "List of World Heritage Sites in Portugal"],
    "se": ["Demographics of Sweden", "Provinces of Sweden", "Lands of Sweden", "Sápmi", "List of Swedish inventions",
           "Swedish cuisine", "List of World Heritage Sites in Sweden"],
    "za": ["2022 South African census", "Languages of South Africa", "Bantustan", "Provinces of South Africa",
           "List of national parks of South Africa", "South African cuisine", "List of World Heritage Sites in South Africa"],
    "nz": ["2023 New Zealand census", "Iwi", "List of Lord of the Rings filming locations", "Regions of New Zealand",
           "New Zealand cuisine", "List of World Heritage Sites in New Zealand"],
    "co": ["2018 Colombian census", "Natural regions of Colombia", "Music of Colombia", "Colombian cuisine",
           "Coffee production in Colombia", "List of World Heritage Sites in Colombia"],
    "cl": ["Climate of Chile", "Mapuche", "Chilean wine", "Mining in Chile", "Chilean cuisine", "List of World Heritage Sites in Chile"],
    "my": ["Malay rulers", "Demographics of Malaysia", "Malaysian cuisine", "List of World Heritage Sites in Malaysia"],
    "kr": ["Three Kingdoms of Korea", "Korean cuisine", "Kimchi", "Korean dialects", "List of World Heritage Sites in South Korea"],
    "pe": ["Inca Empire", "Quechuan languages", "Peruvian cuisine", "Geography of Peru", "List of World Heritage Sites in Peru"],
    "eg": ["Upper and Lower Egypt", "Egyptian cuisine", "List of World Heritage Sites in Egypt", "Hala'ib Triangle", "Bir Tawil"],
    "no": ["Demographics of Norway", "Fjords of Norway", "Sámi people", "Norwegian cuisine", "List of World Heritage Sites in Norway"],
    "dk": ["Demographics of Denmark", "Viking ship", "Danish design", "Danish cuisine", "List of World Heritage Sites in Denmark"],
    "fi": ["Demographics of Finland", "Finnish sauna", "Sisu", "Finnish cuisine", "Languages of Finland", "List of World Heritage Sites in Finland"],
    "is": ["Demographics of Iceland", "Volcanism of Iceland", "Sagas of Icelanders", "Icelandic cuisine", "List of World Heritage Sites in Iceland"],
    "ee": ["Demographics of Estonia", "Estonian Song Festival", "e-Estonia", "Estonian cuisine", "List of World Heritage Sites in Estonia"],
    "lv": ["Demographics of Latvia", "Dainas", "Historical Latvian lands", "Latvian cuisine", "List of World Heritage Sites in Latvia"],
    "lt": ["Demographics of Lithuania", "Ethnographic regions of Lithuania", "Hill forts in Lithuania", "Lithuanian cuisine", "List of World Heritage Sites in Lithuania"],
    "gr": ["Demographics of Greece", "Greek mythology", "Greek islands", "Greek cuisine", "Mount Athos", "List of World Heritage Sites in Greece"],
    "tr": ["Demographics of Turkey", "Geographical regions of Turkey", "Hittites", "Turkish cuisine", "List of World Heritage Sites in Turkey"],
    "ua": ["Demographics of Ukraine", "Historical regions of Ukraine", "Ukrainian cuisine", "Russian-occupied territories of Ukraine", "List of World Heritage Sites in Ukraine"],
    "ro": ["Demographics of Romania", "Historical regions of Romania", "Painted churches of northern Moldavia", "Romanian cuisine", "List of World Heritage Sites in Romania"],
    "hu": ["Demographics of Hungary", "Wine regions of Hungary", "Thermal baths in Hungary", "Hungarian cuisine", "List of World Heritage Sites in Hungary"],
    "vn": ["Demographics of Vietnam", "Vietnamese cuisine", "Regions of Vietnam", "List of World Heritage Sites in Vietnam"],
    "th": ["Demographics of Thailand", "Regions of Thailand", "Loy Krathong", "Thai cuisine", "List of World Heritage Sites in Thailand"],
    "ph": ["Demographics of the Philippines", "Island groups of the Philippines", "Languages of the Philippines", "Filipino cuisine", "List of World Heritage Sites in the Philippines"],
    "id": ["Demographics of Indonesia", "Ethnic groups in Indonesia", "Batik", "Indonesian cuisine", "List of World Heritage Sites in Indonesia"],
    "pk": ["Demographics of Pakistan", "Languages of Pakistan", "Indus Valley Civilisation", "Gandhara", "Pakistani cuisine", "List of World Heritage Sites in Pakistan"],
    "ma": ["Demographics of Morocco", "Berbers", "Moroccan cuisine", "Western Sahara", "Moroccan Western Sahara Wall", "List of World Heritage Sites in Morocco"],
    "ke": ["Demographics of Kenya", "Ethnic groups in Kenya", "National parks of Kenya", "Provinces of Kenya", "Kenyan cuisine"],
    "et": ["Demographics of Ethiopia", "Ethnic groups in Ethiopia", "Kingdom of Aksum", "Coffee production in Ethiopia", "Ethiopian cuisine", "List of World Heritage Sites in Ethiopia"],
    "sa": ["Demographics of Saudi Arabia", "Holiest sites in Islam", "Saudi Arabian cuisine", "List of World Heritage Sites in Saudi Arabia"],
    "ir": ["Demographics of Iran", "Ethnicities in Iran", "Persepolis", "Persian carpet", "Iranian cuisine", "List of World Heritage Sites in Iran"],
    "hr": ["Demographics of Croatia", "Dalmatia", "Croatian islands", "Plitvice Lakes National Park", "Croatian cuisine", "List of World Heritage Sites in Croatia"],
    "rs": ["Demographics of Serbia", "Vojvodina", "Šumadija", "Serbian Orthodox monasteries", "Serbian cuisine", "List of World Heritage Sites in Serbia"],
    "bg": ["Demographics of Bulgaria", "Bulgarian rose oil", "Rila Monastery", "Thrace", "Bulgarian cuisine", "List of World Heritage Sites in Bulgaria"],
    "sk": ["Demographics of Slovakia", "Castles in Slovakia", "High Tatras", "Slovak cuisine", "List of World Heritage Sites in Slovakia"],
    "si": ["Demographics of Slovenia", "Traditional regions of Slovenia", "Postojna Cave", "Wine regions of Slovenia", "Slovenian cuisine", "List of World Heritage Sites in Slovenia"],
    "ve": ["Demographics of Venezuela", "Angel Falls", "Tepui", "Llanos", "Venezuelan cuisine", "List of World Heritage Sites in Venezuela"],
    "ec": ["Demographics of Ecuador", "Galápagos Islands", "List of volcanoes in Ecuador", "Indigenous peoples in Ecuador", "Ecuadorian cuisine", "List of World Heritage Sites in Ecuador"],
    "bo": ["Demographics of Bolivia", "Salar de Uyuni", "Lake Titicaca", "Languages of Bolivia", "Bolivian cuisine", "List of World Heritage Sites in Bolivia"],
    "uy": ["Demographics of Uruguay", "Candombe", "Uruguayan cuisine", "Gaucho", "List of World Heritage Sites in Uruguay"],
    "cu": ["Demographics of Cuba", "Music of Cuba", "Cuban cigar", "Cuban Revolution", "Guantanamo Bay Naval Base", "Cuban cuisine", "List of World Heritage Sites in Cuba"],
    "bd": ["Demographics of Bangladesh", "List of rivers of Bangladesh", "Sundarbans", "Textile industry in Bangladesh", "Bangladeshi cuisine", "List of World Heritage Sites in Bangladesh"],
    "lk": ["Demographics of Sri Lanka", "Tea production in Sri Lanka", "Ancient cities of Sri Lanka", "Sinhala language", "Sri Lankan cuisine", "List of World Heritage Sites in Sri Lanka"],
    "np": ["Demographics of Nepal", "List of mountains in Nepal", "Ethnic groups in Nepal", "Kalapani territory", "Nepalese cuisine", "List of World Heritage Sites in Nepal"],
    "kz": ["Demographics of Kazakhstan", "Kazakh Steppe", "Mining industry of Kazakhstan", "Baikonur Cosmodrome", "Kazakh cuisine", "List of World Heritage Sites in Kazakhstan"],
    "uz": ["Demographics of Uzbekistan", "Silk Road", "Khanate of Khiva", "Suzani", "Uzbek cuisine", "List of World Heritage Sites in Uzbekistan"],
    "dz": ["Demographics of Algeria", "Kabylia", "Tassili n'Ajjer", "Algerian cuisine", "List of World Heritage Sites in Algeria"],
    "tn": ["Demographics of Tunisia", "Carthage", "Tunisian cuisine", "Olive oil in Tunisia", "List of World Heritage Sites in Tunisia"],
    "gh": ["Demographics of Ghana", "Ashanti Empire", "Cocoa production in Ghana", "Ethnic groups in Ghana", "Ghanaian cuisine", "List of World Heritage Sites in Ghana"],
    "tz": ["Demographics of Tanzania", "Mount Kilimanjaro", "Serengeti National Park", "Zanzibar", "Tanzanian cuisine", "List of World Heritage Sites in Tanzania"],
    "cd": ["Demographics of the Democratic Republic of the Congo", "Languages of the Democratic Republic of the Congo",
           "Mining industry of the Democratic Republic of the Congo", "Congo River", "List of World Heritage Sites in the Democratic Republic of the Congo"],
}
FONTS = {"kr": ("NotoSansKR.ttf", "https://github.com/google/fonts/raw/main/ofl/notosanskr/NotoSansKR%5Bwght%5D.ttf"),
         "eg": ("NotoSansArabic.ttf", "https://github.com/google/fonts/raw/main/ofl/notosansarabic/NotoSansArabic%5Bwdth%2Cwght%5D.ttf"),
         "th": ("NotoSansThai.ttf", "https://github.com/google/fonts/raw/main/ofl/notosansthai/NotoSansThai%5Bwdth%2Cwght%5D.ttf"),
         "ma": ("NotoSansTifinagh.ttf", "https://github.com/google/fonts/raw/main/ofl/notosanstifinagh/NotoSansTifinagh-Regular.ttf"),
         "et": ("NotoSansEthiopic.ttf", "https://github.com/google/fonts/raw/main/ofl/notosansethiopic/NotoSansEthiopic%5Bwdth%2Cwght%5D.ttf"),
         "bd": ("NotoSansBengali.ttf", "https://github.com/google/fonts/raw/main/ofl/notosansbengali/NotoSansBengali%5Bwdth%2Cwght%5D.ttf"),
         "lk": [("NotoSansSinhala.ttf", "https://github.com/google/fonts/raw/main/ofl/notosanssinhala/NotoSansSinhala%5Bwdth%2Cwght%5D.ttf"),
                ("NotoSansTamil.ttf", "https://github.com/google/fonts/raw/main/ofl/notosanstamil/NotoSansTamil%5Bwdth%2Cwght%5D.ttf")],
         "np": ("NotoSansDevanagari.ttf", "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf"),
         "dz": ("NotoSansTifinagh.ttf", "https://github.com/google/fonts/raw/main/ofl/notosanstifinagh/NotoSansTifinagh-Regular.ttf")}
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
    fonts = FONTS.get(code, [])
    for name, url in ([fonts] if isinstance(fonts, tuple) else fonts):  # the script fonts for the card's native names (subset by tools/build_fonts.py)
        font = DL / "fonts" / name
        if not font.exists():
            font.write_bytes(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=180).read())
        print(f"   font: {font.relative_to(ROOT)} ({font.stat().st_size // 1024} KB)")
    if code == "jp":
        font = DL / "fonts" / "NotoSansJP.ttf"
        if not font.exists():
            font.write_bytes(urllib.request.urlopen(urllib.request.Request(NOTO_JP, headers=UA), timeout=180).read())
        print(f"   font: {font.relative_to(ROOT)} ({font.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    sys.stdout.reconfigure(line_buffering=True)
    main()
