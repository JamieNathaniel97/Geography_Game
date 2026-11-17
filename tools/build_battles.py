"""Builds the famous battles data for the History games (History_games.md, H2):

  data/battles.json  battles with where and when they were fought:
                     [{"id": "Q48314", "name": "Battle of Waterloo", "desc": "...", "year": 1815, "end": 1815,
                       "ll": [4.4125, 50.68], "iso": "BEL", "naval": false, "siege": false,
                       "war": "War of the Seventh Coalition", "links": 120, "picked": true}, ...]
                     year/end: start and end years, negative for BC (Wikidata gives 1 BC as year 0; converted here)
                     ll: [longitude, latitude]; iso: the app's country code for the place today, or null (at sea)
                     naval: a naval battle (Wikidata type, or it's at sea); siege: a siege
                     war: the war it was part of, if Wikidata says
                     links: number of Wikipedia language editions with an article, the "how famous" score

Source: Wikidata (https://www.wikidata.org), CC0 (public domain). Needs network access to query.wikidata.org,
so run it in VS Code, not in a locked-down sandbox.

Run from the repo root:  python tools/build_battles.py [min_links]
min_links (default 40): only battles with Wikipedia articles in at least this many languages. The hand-picked
battles in tools/battles_extra.py are always added. Raw results are cached in tools/downloads/battles/.
Check the output by hand: battles over large areas (campaigns, the Battle of Britain) have one point in Wikidata,
which may be a poor answer; fix or drop them in FIXES.
"""
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads" / "battles"
OUT = ROOT / "data" / "battles.json"
ENDPOINT = "https://query.wikidata.org/sparql"
UA = {"User-Agent": "GaiaQuestBuild/1.0 (map quiz data build; offline geography app)",
      "Accept": "application/sparql-results+json"}

BATTLE, NAVAL, SIEGE = "Q178561", "Q1261499", "Q188055"

# hand corrections after checking the output: id -> fields to overwrite (or {"drop": True})
FIXES = {}

QUERY = """
SELECT ?b ?bLabel ?bDescription ?links ?coord ?iso ?warLabel
       (MIN(?t) AS ?start) (MAX(?e) AS ?finish)
       (GROUP_CONCAT(DISTINCT STRAFTER(STR(?type), "entity/"); separator=" ") AS ?types)
       (SAMPLE(?article) AS ?title)
WHERE {
  %(pick)s
  ?b wikibase:sitelinks ?links ; wdt:P625 ?coord .
  OPTIONAL { ?b wdt:P31 ?type . }
  OPTIONAL { ?b wdt:P585 ?t1 . } OPTIONAL { ?b wdt:P580 ?t2 . } OPTIONAL { ?b wdt:P582 ?t3 . }
  BIND(COALESCE(?t1, ?t2) AS ?t) BIND(COALESCE(?t3, ?t1, ?t2) AS ?e)
  FILTER(BOUND(?t))
  OPTIONAL { ?b wdt:P17 ?c . ?c wdt:P298 ?iso . }
  OPTIONAL { ?b wdt:P361 ?war . }
  OPTIONAL { ?article schema:about ?b ; schema:isPartOf <https://en.wikipedia.org/> . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
GROUP BY ?b ?bLabel ?bDescription ?links ?coord ?iso ?warLabel
"""


def sparql(query, cache):
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
                data = json.load(r)
            cache.write_text(json.dumps(data), encoding="utf-8")
            return data
        except Exception as e:
            print("  query failed:", e, "- retrying")
            time.sleep(20 * (attempt + 1))
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
    min_links = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    DL.mkdir(parents=True, exist_ok=True)
    print(f"querying Wikidata for battles with >= {min_links} Wikipedia languages ...")
    fame = ("VALUES ?kind { wd:%s wd:%s wd:%s } ?b wdt:P31 ?kind ; wikibase:sitelinks ?l0 . FILTER(?l0 >= %d)"
            % (BATTLE, NAVAL, SIEGE, min_links))
    rows = sparql(QUERY % {"pick": fame}, DL / f"battles_{min_links}.json")["results"]["bindings"]

    sys.path.insert(0, str(ROOT / "tools"))
    from battles_extra import EXTRA
    extra_titles = {t for ts in EXTRA.values() for t in ts}
    titles = sorted(extra_titles)
    for i in range(0, len(titles), 40):
        vals = " ".join("<https://en.wikipedia.org/wiki/%s>" % urllib.parse.quote(t.replace(" ", "_"), safe="")
                        for t in titles[i:i + 40])
        print(f"  hand-picked battles {i + 1}-{min(i + 40, len(titles))} ...")
        rows += sparql(QUERY % {"pick": "VALUES ?article { %s } ?article schema:about ?b ." % vals},
                       DL / f"extra_{i // 40}.json")["results"]["bindings"]

    app_isos = {c["iso"] for c in json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf-8"))}
    battles = {}
    for r in rows:
        g = lambda k: r.get(k, {}).get("value")
        bid = g("b").rsplit("/", 1)[-1]
        if bid in battles:
            continue
        name = g("bLabel")
        if not name or (name.startswith("Q") and name[1:].isdigit()):
            continue
        types = set((g("types") or "").split())
        iso = {"XKX": "UNK"}.get(g("iso"), g("iso"))
        title = urllib.parse.unquote(g("title").rsplit("/", 1)[-1]).replace("_", " ") if g("title") else None
        battles[bid] = {
            "id": bid, "name": name, "desc": g("bDescription") or "",
            "year": year(g("start")), "end": year(g("finish")), "ll": point(g("coord")),
            "iso": iso if iso in app_isos else None,
            "naval": NAVAL in types, "siege": SIEGE in types,
            "war": g("warLabel"), "links": int(g("links")),
            "picked": title in extra_titles, "title": title,
        }

    # a battle with no country is usually at sea: count it as naval, but list it to check
    at_sea = [b for b in battles.values() if b["iso"] is None and not b["naval"]]
    for b in at_sea:
        b["naval"] = True

    for bid, fix in FIXES.items():
        if bid in battles:
            if fix.get("drop"):
                del battles[bid]
            else:
                battles[bid].update(fix)

    out = sorted(battles.values(), key=lambda b: -b["links"])
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    found = {b["title"] for b in out}
    missing = sorted(t for t in extra_titles if t not in found)
    print(f"{OUT.relative_to(ROOT)}: {len(out)} battles ({sum(b['naval'] for b in out)} naval, "
          f"{sum(b['siege'] for b in out)} sieges, {sum(b['picked'] for b in out)} hand-picked)")
    eras = [("before 500", -9999, 499), ("500-1499", 500, 1499), ("1500-1799", 1500, 1799),
            ("1800s", 1800, 1899), ("1900-1945", 1900, 1945), ("after 1945", 1946, 9999)]
    print("by era:", {n: sum(a <= (b["year"] or 0) <= z for b in out) for n, a, z in eras})
    if missing:
        print(f"{len(missing)} hand-picked titles not found (wrong title, or no coordinates or date in Wikidata); "
              "fix them in tools/battles_extra.py:", ", ".join(missing))
    if at_sea:
        print(f"{len(at_sea)} battles with no country were counted as naval; check:",
              ", ".join(b["name"] for b in at_sea[:40]))


if __name__ == "__main__":
    main()
