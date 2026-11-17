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

Run from the repo root:  python tools/build_people.py [min_links] [--images]
min_links (default 100): only people with Wikipedia articles in at least this many languages. Lower it for more
people. The raw query results are cached in tools/downloads/people/ so re-runs don't hit the server again; delete
that folder to refresh.
The hand-picked people in tools/people_extra.py are always added (marked "picked": true), whatever their fame.
--images also downloads a small portrait for each person whose Wikidata picture has a free licence (see
fetch_images), with its credit; people without a free picture get "img": null.

Check the output by hand before shipping: Wikidata sometimes has several birth or death places (the build takes
the first with coordinates and prints the people it had to choose for), and places that are a country or region
rather than a town (printed as warnings; fix them in FIXES below).
"""
import json
import re
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
       (SAMPLE(?image) AS ?img) (SAMPLE(?article) AS ?title)
WHERE {
  %(pick)s
  ?p wdt:P31 wd:Q5 ;
     wikibase:sitelinks ?links .
  ?p wdt:P569 ?born ; wdt:P570 ?died .
  ?p wdt:P19 ?bp . ?bp wdt:P625 ?bcoord .
  ?p wdt:P20 ?dp . ?dp wdt:P625 ?dcoord .
  OPTIONAL { ?bp wdt:P17 ?bc . ?bc wdt:P298 ?bcountryIso . }
  OPTIONAL { ?dp wdt:P17 ?dc . ?dc wdt:P298 ?dcountryIso . }
  OPTIONAL { ?p wdt:P106 ?occ . }
  OPTIONAL { ?p wdt:P18 ?image . }
  OPTIONAL { ?article schema:about ?p ; schema:isPartOf <https://en.wikipedia.org/> . }
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
    fame = "?p wikibase:sitelinks ?l0 . FILTER(?l0 >= %d)" % min_links
    rows = sparql(QUERY % {"pick": fame}, DL / f"people_{min_links}.json")["results"]["bindings"]

    # the hand-picked people (tools/people_extra.py), looked up by English Wikipedia title, 40 at a time
    sys.path.insert(0, str(ROOT / "tools"))
    from people_extra import EXTRA
    extra_titles = {t: region for region, ts in EXTRA.items() for t in ts}
    titles = list(extra_titles)
    for i in range(0, len(titles), 40):
        vals = " ".join('<https://en.wikipedia.org/wiki/%s>' % urllib.parse.quote(t.replace(" ", "_"), safe="")
                        for t in titles[i:i + 40])
        pick = "VALUES ?article { %s } ?article schema:about ?p ." % vals
        print(f"  hand-picked people {i + 1}-{min(i + 40, len(titles))} ...")
        rows += sparql(QUERY % {"pick": pick}, DL / f"extra_{i // 40}.json")["results"]["bindings"]

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
            "picked": False,
            "image": g("img"),  # a Wikimedia Commons file; see --images
            "title": urllib.parse.unquote(g("title").rsplit("/", 1)[-1]).replace("_", " ") if g("title") else None,
        }

    found = set()
    for p in people.values():
        if p["title"] in extra_titles:
            p["picked"] = True
            found.add(p["title"])
    missing = [t for t in titles if t not in found]
    if missing:
        print(f"{len(missing)} hand-picked titles not found (wrong title, alive, or no birth/death place with "
              "coordinates in Wikidata); fix them in tools/people_extra.py:", ", ".join(missing))

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
    if "--images" in sys.argv:
        fetch_images(out)
        OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    vague = [p["name"] for p in out if p["biso"] is None or p["diso"] is None]
    if vague:
        print(f"{len(vague)} people have a place with no modern country (at sea, ancient sites, territories); check:",
              ", ".join(vague[:40]))


# Licences that allow bundling the picture in the app (with credit where they need it)
FREE = ("public domain", "pd", "cc0", "cc by", "cc-by", "cc by-sa", "cc-by-sa")
IMG_DIR = ROOT / "data" / "people"
IMG_WIDTH = 240


def fetch_images(people):
    """Downloads a small portrait for each person whose Wikidata picture has a free licence (checked per file with the
    Commons API), to data/people/<id>.webp, and stores the credit in the record: "img": {"credit": ..., "licence": ...}.
    People whose picture isn't free (many 20th-century photos) get no picture."""
    from PIL import Image
    import io
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    kept = skipped = 0
    for p in people:
        f = p.pop("image", None)
        p["img"] = None
        if not f:
            continue
        name = urllib.parse.unquote(f.rsplit("/", 1)[-1])
        api = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
            "action": "query", "titles": "File:" + name, "prop": "imageinfo", "format": "json",
            "iiprop": "url|extmetadata", "iiurlwidth": IMG_WIDTH})
        try:
            with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": UA["User-Agent"]}),
                                        timeout=60) as r:
                info = next(iter(json.load(r)["query"]["pages"].values()))["imageinfo"][0]
            meta = info.get("extmetadata", {})
            lic = meta.get("LicenseShortName", {}).get("value", "")
            if not lic.lower().startswith(FREE):
                skipped += 1
                continue
            artist = meta.get("Artist", {}).get("value", "")
            artist = re.sub(r"<[^>]+>", "", artist).strip()  # the API gives HTML
            out = IMG_DIR / f"{p['id']}.webp"
            if not out.exists():
                with urllib.request.urlopen(urllib.request.Request(info["thumburl"],
                                            headers={"User-Agent": UA["User-Agent"]}), timeout=60) as r:
                    Image.open(io.BytesIO(r.read())).convert("RGB").save(out, "WEBP", quality=72)
                time.sleep(0.5)  # be polite to Commons
            p["img"] = {"credit": artist or "Wikimedia Commons", "licence": lic, "file": name}
            kept += 1
        except Exception as e:
            print("  picture failed for", p["name"], e)
    print(f"pictures: {kept} free ones saved in data/people/, {skipped} skipped (not a free licence)")


if __name__ == "__main__":
    main()
