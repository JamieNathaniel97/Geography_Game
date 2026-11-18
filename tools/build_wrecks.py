"""Builds the famous shipwrecks data for the History games (History_games.md, H3):

  data/wrecks.json  shipwrecks with where and when the ship sank:
                    [{"id": "Q25173", "name": "RMS Titanic", "desc": "...", "year": 1912, "ll": [-49.9469, 41.7258],
                      "iso": null, "deaths": 1517, "found": 1985, "raised": false, "war": false,
                      "links": 150, "picked": true}, ...]
                    year: when it sank (negative for BC); ll: [longitude, latitude] of the wreck
                    iso: the app's country code when the wreck is in a country's waters or on land, else null
                    deaths: lives lost, if Wikidata says; found: year the wreck was found, if Wikidata says
                    raised: the wreck was raised and is now on land or in a museum (Vasa, Mary Rose)
                    war: sunk in war (Wikidata says it was sunk in a battle or by an attack)

Source: Wikidata (https://www.wikidata.org), CC0 (public domain). Needs network access to query.wikidata.org,
so run it in VS Code. Run from the repo root:  python tools/build_wrecks.py [min_links]
min_links (default 15): only wrecks with Wikipedia articles in at least this many languages. The hand-picked
wrecks in tools/wrecks_extra.py are always added. Raw results are cached in tools/downloads/wrecks/.

Wikidata records a wreck in two ways: an item for the wreck itself (instance of shipwreck), or the ship's own item
with its wreck position (coordinates, often with a "shipwreck" significant event). The query takes both. Check by
hand: a ship's coordinates are sometimes its home port, not the wreck; the script lists wrecks on land to check.
"""
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads" / "wrecks"
OUT = ROOT / "data" / "wrecks.json"
ENDPOINT = "https://query.wikidata.org/sparql"
UA = {"User-Agent": "GaiaQuestBuild/1.0 (map quiz data build; offline geography app)",
      "Accept": "application/sparql-results+json"}

SHIPWRECK = "Q852190"

# hand corrections after checking the output: id -> fields to overwrite (or {"drop": True})
FIXES = {  # checked 2026-11-18
    "Q25173": {"name": "RMS Titanic", "deaths": 1517, "found": 1985},
    "Q150857": {"deaths": 2200, "found": 1989},
    "Q190542": {"deaths": 32, "raised": "Refloated in 2014 and broken up in Genoa"},
    "Q220239": {"deaths": 1415, "found": 2001},
    "Q33209": {"drop": True},    # Mary Celeste: the 2001 identification is doubtful (wrecks_extra.py)
    "Q311245": {"deaths": 141, "found": 1998},
    "Q828458": {"deaths": 852, "found": 1994},
    "Q671602": {"deaths": 266, "raised": "Raised in 1911, then towed out and sunk in deep water off Havana"},
    "Q247567": {"found": 1996},
    "Q573852": {"found": 1982},
    "Q540580": {"drop": True},   # ARA General Belgrano: the wreck has never been found
    "Q1032042": {"deaths": 1017},
    "Q1607814": {"deaths": 193, "raised": "Refloated in 1987 and broken up"},
    "Q1753417": {"deaths": 1168, "found": 1982},
    "Q1789811": {"deaths": 800, "found": 1980},
    "Q3241668": {"drop": True},  # USS Texas (1892): a target hulk, not a famous wreck
    "Q605764": {"deaths": 130, "found": 2019},
    "Q1572476": {"deaths": 260, "found": 1985},
    "Q3589078": {"found": 1998},
    "Q7394233": {"deaths": 2},
}

QUERY = """
SELECT ?s ?sLabel ?sDescription ?links ?coord ?iso
       (MIN(?t) AS ?sank) (MAX(?d) AS ?deaths) (MIN(?f) AS ?found)
       (SAMPLE(?article) AS ?title) (SAMPLE(?battle) AS ?inBattle)
WHERE {
  %(pick)s
  ?s wikibase:sitelinks ?links ; wdt:P625 ?coord .
  OPTIONAL { ?s p:P793 ?ev . ?ev ps:P793 wd:%(wreck)s . OPTIONAL { ?ev pq:P585 ?evt . } }
  OPTIONAL { ?s wdt:P585 ?t1 . } OPTIONAL { ?s wdt:P576 ?t2 . } OPTIONAL { ?s wdt:P730 ?t3 . }
  BIND(COALESCE(?evt, ?t1, ?t2, ?t3) AS ?t)
  FILTER(BOUND(?t))
  OPTIONAL { ?s wdt:P1120 ?d . }
  OPTIONAL { ?s wdt:P575 ?f . }
  OPTIONAL { ?s wdt:P17 ?c . ?c wdt:P298 ?iso . }
  OPTIONAL { ?s wdt:P607 ?battle . }
  OPTIONAL { ?article schema:about ?s ; schema:isPartOf <https://en.wikipedia.org/> . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
GROUP BY ?s ?sLabel ?sDescription ?links ?coord ?iso
"""


_last = 0.0


def sparql(query, cache):
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    global _last
    for attempt in range(10):
        # the query service may allow only one query a minute (it did during an outage, 2026-11-18): keep to that
        wait = 62 - (time.time() - _last)
        if wait > 0:
            time.sleep(wait)
        _last = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
                data = json.load(r)
            cache.write_text(json.dumps(data), encoding="utf-8")
            return data
        except Exception as e:
            print("  query failed:", e, "- retrying")
    sys.exit("Wikidata query failed; try a higher min_links, or later")


def year(v):
    if not v:
        return None
    neg = v.startswith("-")
    y = int(v.lstrip("-").split("-")[0])
    return -(y + 1) if neg else y


def point(wkt):
    lon, lat = wkt[wkt.index("(") + 1:wkt.index(")")].split()
    return [round(float(lon), 4), round(float(lat), 4)]


def main():
    min_links = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    DL.mkdir(parents=True, exist_ok=True)
    print(f"querying Wikidata for shipwrecks with >= {min_links} Wikipedia languages ...")
    fame = ("{ ?s wdt:P31/wdt:P279* wd:%s . } UNION { ?s wdt:P793 wd:%s . } "
            "?s wikibase:sitelinks ?l0 . FILTER(?l0 >= %d)" % (SHIPWRECK, SHIPWRECK, min_links))
    rows = sparql(QUERY % {"pick": fame, "wreck": SHIPWRECK}, DL / f"wrecks_{min_links}.json")["results"]["bindings"]

    sys.path.insert(0, str(ROOT / "tools"))
    from wrecks_extra import EXTRA
    extra_titles = {t for ts in EXTRA.values() for t in ts}
    titles = sorted(extra_titles)
    for i in range(0, len(titles), 40):
        vals = " ".join("<https://en.wikipedia.org/wiki/%s>" % urllib.parse.quote(t.replace(" ", "_"), safe="")
                        for t in titles[i:i + 40])
        print(f"  hand-picked wrecks {i + 1}-{min(i + 40, len(titles))} ...")
        rows += sparql(QUERY % {"pick": "VALUES ?article { %s } ?article schema:about ?s ." % vals,
                                "wreck": SHIPWRECK}, DL / f"extra_{i // 40}.json")["results"]["bindings"]

    app_isos = {c["iso"] for c in json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf-8"))}
    wrecks = {}
    for r in rows:
        g = lambda k: r.get(k, {}).get("value")
        sid = g("s").rsplit("/", 1)[-1]
        if sid in wrecks:
            continue
        name = g("sLabel")
        if not name or (name.startswith("Q") and name[1:].isdigit()):
            continue
        iso = {"XKX": "UNK"}.get(g("iso"), g("iso"))
        title = urllib.parse.unquote(g("title").rsplit("/", 1)[-1]).replace("_", " ") if g("title") else None
        deaths = g("deaths")
        wrecks[sid] = {
            "id": sid, "name": name, "desc": g("sDescription") or "",
            "year": year(g("sank")), "ll": point(g("coord")), "iso": iso if iso in app_isos else None,
            "deaths": int(float(deaths)) if deaths else None, "found": year(g("found")),
            "raised": False, "war": bool(g("inBattle")),
            "links": int(g("links")), "picked": title in extra_titles, "title": title,
        }

    for sid, fix in FIXES.items():
        if sid in wrecks:
            if fix.get("drop"):
                del wrecks[sid]
            else:
                wrecks[sid].update(fix)

    # the hand-written wrecks (wrecks_extra.HAND), where Wikidata has no wreck position
    from wrecks_extra import HAND
    have = {w["title"] for w in wrecks.values()}
    for title, h in HAND.items():
        if title not in have:
            wid = "H-" + "".join(ch for ch in title if ch.isalnum())
            wrecks[wid] = {"id": wid, "iso": None, "deaths": None, "found": None, "raised": False, "war": False,
                           "links": 0, "picked": True, "title": title, **h}
    # war graves (protected by law, or treated as one by their navies): the card says so
    WAR_GRAVES = {"Bismarck", "HMS Hood", "USS Arizona", "USS Indianapolis", "Yamato", "MV Wilhelm Gustloff", "HMS Indefatigable",
                  "USS Yorktown", "USS Gambier Bay", "Moskva", "German cruiser Karlsruhe", "HMHS Britannic", "Kursk", "ARA San Juan"}
    for w in wrecks.values():
        if w["name"] in WAR_GRAVES:
            w["grave"] = True
    out = sorted(wrecks.values(), key=lambda w: -w["links"])
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    found = {w["title"] for w in out}
    missing = sorted(t for t in extra_titles if t not in found)
    print(f"{OUT.relative_to(ROOT)}: {len(out)} wrecks ({sum(w['picked'] for w in out)} hand-picked, "
          f"{sum(w['war'] for w in out)} sunk in war)")
    if missing:
        print(f"{len(missing)} hand-picked titles not found (wrong title, or no coordinates or sinking date in "
              "Wikidata); fix them in tools/wrecks_extra.py:", ", ".join(missing))
    on_land = [w["name"] for w in out if w["iso"]]
    if on_land:
        print(f"{len(on_land)} wrecks are inside a country (coastal waters, rivers, lakes, raised wrecks, or a home "
              "port given by mistake); check:", ", ".join(on_land[:50]))


if __name__ == "__main__":
    main()
