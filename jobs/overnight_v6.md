# Job: overnight v6, five Southern and Eastern European country maps

Greece, Turkey, Ukraine, Romania and Hungary: first the downloads, then the builds. Decided with the user on 2026-11-27. **The downloads are done (2026-11-27, see the log at the end); the builds aren't started.**

**Don't start this job until the user says so**, and don't change the other job files to make room for it. Don't commit or push until the user says so.

It works like [overnight_v4.md](overnight_v4.md) and [overnight_v5.md](overnight_v5.md): the shared builder (`tools/build_country.py`, `tools/<code>_facts.py`), one `NEW_MAPS` row and a projection style each (add the style first), the same tests. Where this file and the earlier ones differ, this file wins.

## The countries (decided 2026-11-27)

| Country | Code | Parts | Games 5 and 6 | Small parts |
| --- | --- | --- | --- | --- |
| Greece | `gr` | 13 regions (periféries); Mount Athos (autonomous monastic state) as a circle | none (regions have no official flags): check | a circle for Mount Athos; island ovals if needed |
| Turkey | `tr` | **81 provinces** (iller); the 7 geographic regions as a filter | none expected (provinces have logos): check | circles for any too small to tap (Yalova, Kilis?) |
| Ukraine | `ua` | 24 oblasts, Kyiv city, the Autonomous Republic of Crimea and Sevastopol: 27 | flags (all official) | circles for Kyiv and Sevastopol |
| Romania | `ro` | 41 counties (județe) and Bucharest: 42 | none (most counties have only arms): use coats of arms if all 41 are on Commons | a circle for Bucharest (inside Ilfov) |
| Hungary | `hu` | 19 counties (megyék) and Budapest: 20 | coats of arms (official) | a circle for Budapest if needed |

- **Greece:** Mount Athos is self-governing under Greek sovereignty: a circle, tappable, its own short card (like Italy's Vatican City but part of the country; it sits in the games or not: judgement call, record it). The many islands: use island ovals where a region is mostly islands and too small (the Ionian Islands, the North and South Aegean).
- **Turkey: build all 81 provinces**, with the 7 geographic regions (Marmara, Aegean, Mediterranean, Black Sea, Central Anatolia, Eastern Anatolia, Southeastern Anatolia) as a region filter like Japan's. **Also download the 12 statistical regions (NUTS 1 / İBBS-1)** (membership table, names, populations) into `tools/downloads/tr/regions/`, for a possible second set later. Don't build them now. Turkey spans Europe and Asia: list it under both, like Russia.
- **Ukraine:** the internationally recognised borders, with Crimea and Sevastopol as parts. **The occupied areas use the disputes layer** (data/disputes.json: Crimea, and the occupied parts of Donetsk and Luhansk): a dotted outline, and the parts' own cards get the dispute added (the rule since 2026-11-27: a dispute over a part with its own card adds to that card). Check whether the disputes layer needs updating for the occupied parts of Zaporizhzhia and Kherson (Natural Earth's list may only have Crimea, Donetsk and Luhansk): if so, add them to `tools/disputes_facts.py` with a source, and record it. Names: Ukrainian and English forms (Kyiv / Kiev, Kharkiv / Kharkov, Odesa / Odessa), the Ukrainian spellings shown.
- **Romania:** Bucharest is a separate municipality inside Ilfov County: a circle.
- **Hungary:** Budapest is separate from Pest County: a circle if needed.

Every country: Find and Name for the parts and capitals (games 5 and 6 where the table says), the Learning card, Focus on, a stats tab, the high-resolution coast. No timelines or layers.

## Part 1: downloads

1. Add the five to `tools/fetch_country_data.py` (local Wikipedia languages: el, tr, uk, ro, hu) and `COUNTRY_QID`.
2. `--extras` and `--census`, with searches for the facts below (for example "Greek mythology", "Greek islands", "Geographical regions of Turkey", "Hittites", "Turkish cuisine", "Historical regions of Ukraine", "Ukrainian cuisine", "Historical regions of Romania", "Painted churches of northern Moldavia", "Wine regions of Hungary", "Thermal baths in Hungary").
3. **Fonts:** Greek and Cyrillic are already covered by the Noto Sans subset (`tools/build_fonts.py`: extend its Greek range if needed; Cyrillic exists).
4. **Shapes:** Natural Earth admin-1; check every count (13, 81, 27, 42, 20). Greece's regions came in 2011: check Natural Earth has them, not the old prefectures.
5. **Populations: the latest official figure by default:** ELSTAT, TurkStat (ADNKS, latest year), the State Statistics Service of Ukraine (**its last reliable figures are from 1 January 2022**: use those and say so on the cards), INS Romania, KSH Hungary; each checked against the national total.
6. **Turkey's 12 statistical regions:** data for later (see above).
7. Download log at the end of this file.

## Part 2: builds

Order: **Hungary, Romania, Greece, Ukraine, Turkey** (Turkey last: 81 provinces).

1. Plans first: `Greece_plan.md`, `Turkey_plan.md`, `Ukraine_plan.md`, `Romania_plan.md`, `Hungary_plan.md`, with no open questions.
2. Build, wire, test (all must pass), preview, PLAN.md, results and decisions to check at the end of this file.
3. **Tests also check:** the occupied areas of Ukraine show the dotted outline and add the dispute to the oblast cards; Mount Athos opens its own card; Turkey's region filter works.

## Learning card facts (approved by the user 2026-11-27)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag or coat of arms where there is one. Leave out any fact that isn't found rather than guess.

**All five (17):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital.

**Plus three for each country:**

- **Greece:** ancient site or myth; island group; olive oil, feta or wine.
- **Turkey:** geographic region; ancient civilisation (Hittite, Greek, Byzantine, Ottoman); famous kebab or sweet.
- **Ukraine:** historic region (Galicia, Volhynia, Sloboda Ukraine...); occupied area or not (from the disputes layer); famous dish (borscht, varenyky).
- **Romania:** historic province (Transylvania, Wallachia, Moldavia...); castle or painted monastery; Carpathians or Danube Delta.
- **Hungary:** historic region; wine region (Tokaj, Eger); thermal bath or spa.

## Download log (2026-11-27)

Downloaded ahead of the run (the user asked for the data first). `python tools/fetch_country_data.py --extras <codes>` (images afterwards at a gentle pace: Commons now rate-limits bursts, so `image()` waits as its Retry-After says), `--census`, and `python tools/fetch_boundaries.py` (geoBoundaries, into `tools/downloads/<code>/geoboundaries/`, with each file's licence in its .json).

| Country | Wikidata divisions (current) | Natural Earth admin-1 | English articles | Local articles | List articles | Flags | Coats of arms | Coast | Census items | geoBoundaries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Greece | 62 | 14 (want 13) | 61 | 59 (el) | 7 | 2 | 3 | 3.8 MB | 48 | – |
| Turkey | 81 | 81 (want 81) | 81 | 81 (tr) | 7 | 0 | 0 | 2.1 MB | 82 | TUR_ADM1 |
| Ukraine | 27 | 25 (want 27) | 27 | 27 (uk) | 7 | 27 | 27 | 1.5 MB | 28 | UKR_ADM1 |
| Romania | 42 | 42 (want 42) | 42 | 42 (ro) | 6 | 9 | 42 | 0.2 MB | 43 | – |
| Hungary | 43 | 43 (want 20) | 43 | 43 (hu) | 6 | 43 | 43 | 0.0 MB | 44 | HUN_ADM1 |

**Shapes to use** (checked 2026-11-27):

- **Greece:** Natural Earth: 13 regions + Mount Athos (the circle), current.
- **Turkey:** Natural Earth: 81, current (geoBoundaries TUR ADM1 is CC BY-SA: not needed).
- **Ukraine:** Natural Earth has 25: use geoBoundaries UKR ADM1 (27: the 24 oblasts, Kyiv, Crimea, Sevastopol; OpenStreetMap, **ODbL**) or add Kyiv/Sevastopol to Natural Earth's.
- **Romania:** Natural Earth: 41 counties + Bucharest, current.
- **Hungary:** Natural Earth has 19 counties + 23 cities with county rights + Budapest: `MERGE` each city into its county (20 parts).

- **Turkey's 12 statistical regions:** `tools/downloads/tr/regions/` ("NUTS statistical regions of Turkey", with each region's provinces).
- Greek and Cyrillic fonts: already in the Noto Sans subset (`tools/build_fonts.py`).

**Decided by the user (2026-11-27): use the OpenStreetMap-derived boundaries (ODbL) where they're the only up-to-date source (Finland, Ukraine, Morocco, Ethiopia), with "© OpenStreetMap contributors" shown on that map (as the UK map does for Ireland, via the map credit), and the derived boundary data offered under the ODbL.**

**Background:** some geoBoundaries files come from OpenStreetMap under the **ODbL** (share-alike: the app would have to credit OpenStreetMap and offer the derived boundary data under the same licence). Where a country has another source, prefer it; where it doesn't, credit "© OpenStreetMap contributors" on the map (as the UK map does for Ireland) and record it under "Decisions to check".
