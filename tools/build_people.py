"""Builds the historical figures data for the History games (History_games.md, idea H1):

  data/people.json  famous people who have died, with where and when they were born and died:
                    [{"id": "Q517", "name": "Napoleon", "desc": "French emperor and military commander",
                      "kind": "leader", "born": 1769, "died": 1821,
                      "bp": "Ajaccio", "bll": [8.7369, 41.9267], "biso": "FRA",
                      "dp": "Longwood", "dll": [-5.6833, -15.95], "diso": null,
                      "links": 250}, ...]
                    born/died: years, negative for BC (Wikidata gives 1 BC as year 0; converted here)
                    bll/dll: [longitude, latitude] of the birth and death places
                    biso/diso: the app's country code for the place today (from its Wikidata country), or null
                    kind: leader, scientist, artist, writer, composer, philosopher, explorer, religious, other
                    links: number of Wikipedia language editions with an article, used as the "how famous" score

Source: Wikidata (https://www.wikidata.org), CC0 (public domain). Queries the Wikidata Query Service, so it needs
network access; run it where query.wikidata.org is reachable (not from a locked-down sandbox).

Run from the repo root:  python tools/build_people.py [min_links]
min_links (default 100): only people with Wikipedia articles in at least this many languages. Lower it for more
people. The raw query results are cached in tools/downloads/people/ so re-runs don't hit the server again; delete
that folder to refresh.

Check the output by hand before shipping: Wikidata sometimes has several birth or death places (the build takes
the first with coordinates and prints the people it had to choose for), and places that are a country or region
rather than a town (printed as warnings; fix them in FIXES below).
"""
import json
import pathlib
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DL = ROOT / "tools" / "downloads" / "people"
OUT = ROOT / "data" / "people.json"
ENDPOINT = "https://query.wikidata.org/sparql"
UA = {"User-Agent": "GaiaQuestBuild/1.0 (map quiz data build; offline geography app)",
      "Accept": "application/sparql-results+json"}

# occupation (Wikidata item) -> kind. The first match in KIND_ORDER wins when a person has several.
OCCUPATIONS = {
    "leader": ["Q82955", "Q116", "Q2285706", "Q189290", "Q30461", "Q48352", "Q372436", "Q4991371"],
    # politician, monarch, head of state, military officer, president, head of government, statesperson, emperor
    "scientist": ["Q901", "Q169470", "Q593644", "Q170790", "Q11063", "Q864503", "Q39631", "Q205375", "Q81096"],
    # scientist, physicist, chemist, mathematician, astronomer, biologist, physician, inventor, engineer
    "artist": ["Q1028181", "Q1281618", "Q42973", "Q33231", "Q483501"],
    # painter, sculptor, architect, photographer, artist
    "writer": ["Q36180", "Q49757", "Q214917", "Q6625963", "Q1930187"],
    # writer, poet, playwright, novelist, journalist
    "composer": ["Q36834", "Q639669", "Q177220", "Q158852"],
    # composer, musician, singer, conductor
    "philosopher": ["Q4964182"],
    "explorer": ["Q11900058", "Q11631"],  # explorer, astronaut
    "religious": ["Q250867", "Q1234713", "Q432386"],  # Catholic priest, theologian, preacher
}
KIND_ORDER = ["leader", "scientist", "explorer", "philosopher", "composer", "artist", "writer", "religious"]

# hand corrections after checking the output: id -> fields to overwrite
FIXES = {
    # "Q517": {"dp": "Longwood, Saint Helena"},
}

QUERY = """
SELECT ?p ?pLabel ?pDescription ?links ?born ?died
       ?bp ?bpLabel ?bcoord ?bcountryIso ?dp ?dpLabel ?dcoord ?dcountryIso
       (GROUP_CONCAT(DISTINCT STRAFTER(STR(?occ), "entity/"); separator=" ") AS ?occs)
WHERE {
  ?p wdt:P31 wd:Q5 ;
     wikibase:sitelinks ?links .
  FILTER(?links >= %(min)d)
  ?p wdt:P569 ?born ; wdt:P570 ?died .
  ?p wdt:P19 ?bp . ?bp wdt:P625 ?bcoord .
  ?p wdt:P20 ?dp . ?dp wdt:P625 ?dcoord .
  OPTIONAL { ?bp wdt:P17 ?bc . ?bc wdt:P298 ?bcountryIso . }
  OPTIONAL { ?dp wdt:P17 ?dc . ?dc wdt:P298 ?dcountryIso . }
  OPTIONAL { ?p wdt:P106 ?occ . }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
GROUP BY ?p ?pLabel ?pDescription ?links ?born ?died
         ?bp ?bpLabel ?bcoord ?bcountryIso ?dp ?dpLabel ?dcoord ?dcountryIso
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
        except Exception as e:  # the service is busy at times: wait and retry
            print("  query failed:", e, "- retrying")
            time.sleep(20 * (attempt + 1))
    sys.exit("Wikidata query failed; try a higher min_links, or later")


def year(v):
    # "1769-08-15T00:00:00Z" or "-0383-01-01T00:00:00Z"; Wikidata's year 0 is 1 BC, -1 is 2 BC and so on
    if not v:
        return None
    neg = v.startswith("-")
    y = int(v.lstrip("-").split("-")[0])
    return -(y + 1) if neg else y


def point(wkt):
    # "Point(8.7369 41.9267)"
    lon, lat = wkt[wkt.index("(") + 1:wkt.index(")")].split()
    return [round(float(lon), 4), round(float(lat), 4)]


def main():
    min_links = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    DL.mkdir(parents=True, exist_ok=True)
    print(f"querying Wikidata for people with >= {min_links} Wikipedia languages ...")
    rows = sparql(QUERY % {"min": min_links}, DL / f"people_{min_links}.json")["results"]["bindings"]

    app_isos = {c["iso"] for c in json.loads((ROOT / "data" / "countries.json").read_text(encoding="utf-8"))}
    iso_fix = {"XKX": "UNK"}  # Kosovo
    occ_kind = {q: k for k, qs in OCCUPATIONS.items() for q in qs}

    people, seen_places = {}, {}
    for r in rows:
        g = lambda k: r.get(k, {}).get("value")
        pid = g("p").rsplit("/", 1)[-1]
        seen_places.setdefault(pid, set()).add((g("bpLabel"), g("dpLabel")))
        if pid in people:  # several places or countries: keep the first, report below
            continue
        kinds = {occ_kind[o] for o in (g("occs") or "").split() if o in occ_kind}
        kind = next((k for k in KIND_ORDER if k in kinds), "other")
        iso = lambda v: (lambda x: x if x in app_isos else None)(iso_fix.get(v, v)) if v else None
        name = g("pLabel")
        if name and name.startswith("Q") and name[1:].isdigit():
            continue  # no English label
        people[pid] = {
            "id": pid, "name": name, "desc": g("pDescription") or "", "kind": kind,
            "born": year(g("born")), "died": year(g("died")),
            "bp": g("bpLabel"), "bll": point(g("bcoord")), "biso": iso(g("bcountryIso")),
            "dp": g("dpLabel"), "dll": point(g("dcoord")), "diso": iso(g("dcountryIso")),
            "links": int(g("links")),
        }

    for pid, fix in FIXES.items():
        if pid in people:
            people[pid].update(fix)

    out = sorted(people.values(), key=lambda p: -p["links"])
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    many = [people[p]["name"] for p, s in seen_places.items() if p in people and len(s) > 1]
    print(f"{OUT.relative_to(ROOT)}: {len(out)} people")
    print("by kind:", {k: sum(p["kind"] == k for p in out) for k in KIND_ORDER + ["other"]})
    if many:
        print(f"{len(many)} people have more than one birth or death place in Wikidata; check:", ", ".join(many[:40]))
    vague = [p["name"] for p in out if p["biso"] is None or p["diso"] is None]
    if vague:
        print(f"{len(vague)} people have a place with no modern country (at sea, ancient sites, territories); check:",
              ", ".join(vague[:40]))


if __name__ == "__main__":
    main()
