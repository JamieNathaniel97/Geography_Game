# Job: overnight v5, seven Nordic and Baltic country maps

Norway, Denmark, Finland, Iceland, Estonia, Latvia and Lithuania: first the downloads, then the builds. Decided with the user on 2026-11-27. **The downloads are done (2026-11-27, see the log at the end); the builds aren't started.**

**Don't start this job until the user says so**, and don't change the other job files to make room for it. Don't commit or push until the user says so.

It works like [overnight_v4.md](overnight_v4.md): one shared builder, `python tools/build_country.py <code>`, with each country's config, part table and card facts in `tools/<code>_facts.py` (see that file's docstring for every option: insets, ovals, `MERGE`, `DISPUTED`, `CLIP`, `FIT_LIGHT`...). In the app each country is one `NEW_MAPS` row (js/app.js) and a projection style (js/mapview.js: **add the style first**, or the map silently shows the whole world). Tests: `_bench_nm.html?d=<code>&r=<style>` and `_bench_menu.html` (git-ignored; the scratchpad test server, see the project notes). Where this file and the earlier ones differ, this file wins.

## The countries (decided 2026-11-27)

| Country | Code | Parts | Games 5 and 6 | Small parts |
| --- | --- | --- | --- | --- |
| Norway | `no` | 15 counties (fylker, 2024 reform) | coats of arms (official county arms) | – |
| Denmark | `dk` | 5 regions | none expected (regions have logos, not arms): check | – |
| Finland | `fi` | 19 regions (maakunnat), Åland included | coats of arms | an oval for Åland if needed |
| Iceland | `is` | 8 regions (landshlutar) | none (no regional flags) | – |
| Estonia | `ee` | 15 counties (maakonnad) | flags (all official) | – |
| Latvia | `lv` | **5 planning regions** | none (no regional flags): check | – |
| Lithuania | `lt` | 10 counties (apskritys) | flags (all official) | – |

- **Norway:** the 2024 county reform (15 counties: Viken, Vestfold og Telemark and Troms og Finnmark were split again). Natural Earth may still have the 2020 map (11) or the old 19: check the count and use geoBoundaries ADM1 (CC BY 4.0, credited) or dissolve municipalities if it's out of date. Svalbard and Jan Mayen are left off (not counties). Sámi names accepted where official (Finnmárku, Romsa).
- **Denmark:** the Faroe Islands and Greenland are left off (not regions). Bornholm is part of the Capital Region: an inset like Spain's Canaries if it sits too far east for a tall phone screen (a framed inset with a square tap area and its own scale bar).
- **Finland:** Åland is a region (autonomous, Swedish-speaking): include it. Finnish and Swedish names both accepted (Uusimaa / Nyland).
- **Iceland:** 8 regions; Westman Islands belong to Suðurland.
- **Estonia, Latvia, Lithuania:** quick builds; local names with and without diacritics accepted (Pärnumaa / Parnumaa, Šiauliai / Siauliai).
- **Latvia: build the 5 planning regions** (Rīga, Vidzeme, Kurzeme, Zemgale, Latgale). **Also download the 43 municipalities** (geoBoundaries ADM1 or the official State Land Service data: shapes, names, centres, populations) into `tools/downloads/lv/municipalities/`, for a possible second set later. Don't build them now.

Every country: Find and Name for the parts and capitals (games 5 and 6 where the table says), the Learning card, Focus on, a stats tab, the high-resolution coast. No timelines or layers.

## Part 1: downloads

1. Add the seven to `tools/fetch_country_data.py` (`COUNTRIES`: name, ISO prefix, local Wikipedia language(s): no, da, fi (and sv for Åland), is, et, lv, lt; list articles; shoreline windows) and `COUNTRY_QID` for `--census`.
2. `python tools/fetch_country_data.py --extras no dk fi is ee lv lt`, then `--census`. Add searches to `EXTRAS` for the facts below (for example "Fjords of Norway", "Sámi people", "Viking ship", "Danish design", "Finnish sauna", "Sisu", "Volcanoes of Iceland", "Icelandic sagas", "Estonian Song Festival", "e-Estonia", "Dainas", "Ethnographic regions of Lithuania", "Hill forts in Lithuania").
3. **Shapes:** Natural Earth admin-1; check every count (15, 5, 19, 8, 15, 5, 10). Norway's and Latvia's divisions changed recently: use geoBoundaries or dissolve if Natural Earth is out of date, and say so in the log.
4. **Populations: the latest official figure by default** (decided by the user 2026-11-26), checked against the national total for the same date: Statistics Norway, Statistics Denmark, Statistics Finland, Statistics Iceland, Statistics Estonia, the Official Statistics Portal of Latvia, Statistics Lithuania. Most have open APIs (PxWeb): use them, as for Sweden and Switzerland.
5. **Latvia's 43 municipalities:** shapes and data for later (see above).
6. Download log at the end of this file.

## Part 2: builds

Order: **Estonia, Lithuania, Latvia, Iceland, Denmark, Finland, Norway** (quickest first; Norway last because of its coast and the 2024 reform).

1. Plans first: `Norway_plan.md`, `Denmark_plan.md`, `Finland_plan.md`, `Iceland_plan.md`, `Estonia_plan.md`, `Latvia_plan.md`, `Lithuania_plan.md`, from this file, with no open questions (judgement calls marked).
2. Build each with the shared builder; wire it in; tests (all must pass); the preview; a line in PLAN.md; results and decisions to check at the end of this file.
3. Norway's and Iceland's coasts are huge: use `DETAIL_TOL` (as Sweden and Chile) if the detail tiles pass about 6 MB.

## Learning card facts (approved by the user 2026-11-27)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag or coat of arms where there is one. Leave out any fact that isn't found rather than guess.

**All seven (17):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital.

**Plus three for each country:**

- **Norway:** fjord or glacier; Sámi area; oil and gas, fishing or hydropower.
- **Denmark:** islands it includes; Viking heritage site; famous Danish design or brand.
- **Finland:** lakes and forest share; Finnish/Swedish bilingual or not; sauna or sisu tradition.
- **Iceland:** volcano or glacier; geothermal or hot spring; saga or Viking-age story.
- **Estonia:** islands or manor; song festival tradition; tech or e-government link.
- **Latvia:** historic land (Kurzeme, Vidzeme, Latgale, Zemgale); amber or coast; folk song (dainas).
- **Lithuania:** ethnographic region (Samogitia, Aukštaitija, Dzūkija, Suvalkija); basketball club; hill fort or castle.

## Download log (2026-11-27)

Downloaded ahead of the run (the user asked for the data first). `python tools/fetch_country_data.py --extras <codes>` (images afterwards at a gentle pace: Commons now rate-limits bursts, so `image()` waits as its Retry-After says), `--census`, and `python tools/fetch_boundaries.py` (geoBoundaries, into `tools/downloads/<code>/geoboundaries/`, with each file's licence in its .json).

| Country | Wikidata divisions (current) | Natural Earth admin-1 | English articles | Local articles | List articles | Flags | Coats of arms | Coast | Census items | geoBoundaries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Norway | 16 | 21 (want 15) | 16 | 16 (no) | 6 | 16 | 14 | 25.5 MB | 17 | NOR_ADM1 |
| Denmark | 6 | 5 (want 5) | 6 | 6 (da) | 6 | 6 | 1 | 1.2 MB | 7 | – |
| Finland | 19 | 18 (want 19) | 19 | 19 (fi), 19 (sv) | 7 | 16 | 19 | 11.0 MB | 20 | FIN_ADM1 |
| Iceland | 50 | 9 (want 8) | 43 | 44 (is) | 6 | 2 | 2 | 1.7 MB | 50 | – |
| Estonia | 41 | 15 (want 15) | 40 | 41 (et) | 6 | 41 | 41 | 0.6 MB | 42 | – |
| Latvia | 19 | 119 (want 5) | 19 | 19 (lv) | 7 | 19 | 19 | 0.2 MB | 20 | LVA_ADM1 |
| Lithuania | 70 | 10 (want 10) | 66 | 70 (lt) | 6 | 45 | 69 | 0.1 MB | 70 | – |

**Shapes to use** (checked 2026-11-27):

- **Norway:** Natural Earth has the old 19 counties (+ Svalbard, Jan Mayen): dissolve to the 2024 15 with `MERGE` (Innlandet = Hedmark + Oppland, Agder = Aust- + Vest-Agder, Vestland = Hordaland + Sogn og Fjordane, Trøndelag = Sør- + Nord-Trøndelag); leave off Svalbard and Jan Mayen. (geoBoundaries has the 2022 map, 11: not used.)
- **Denmark:** Natural Earth: 5, current.
- **Finland:** Natural Earth has 18: use geoBoundaries FIN ADM1 (19, OpenStreetMap, **ODbL**: see the note below) or merge/split from Natural Earth.
- **Iceland:** Natural Earth has 8 regions + Reykjavík as an independent town: `MERGE` Reykjavík into the Capital Region (Höfuðborgarsvæðið).
- **Estonia:** Natural Earth: 15, current (14 counties + Tallinn as a municipality: check Tallinn is within Harju).
- **Latvia:** Natural Earth has the old 119 municipalities: dissolve geoBoundaries LVA ADM1 (the 43 municipalities of 2021, CC BY 4.0) into the 5 planning regions with the membership in `Planning regions of Latvia`.
- **Lithuania:** Natural Earth: 10, current.

- **Latvia's 43 municipalities:** `tools/downloads/lv/municipalities/` (geoBoundaries LVA ADM1, CC BY 4.0, and the list articles with each municipality's planning region and population).

**Decided by the user (2026-11-27): use the OpenStreetMap-derived boundaries (ODbL) where they're the only up-to-date source (Finland, Ukraine, Morocco, Ethiopia), with "© OpenStreetMap contributors" shown on that map (as the UK map does for Ireland, via the map credit), and the derived boundary data offered under the ODbL.**

**Background:** some geoBoundaries files come from OpenStreetMap under the **ODbL** (share-alike: the app would have to credit OpenStreetMap and offer the derived boundary data under the same licence). Where a country has another source, prefer it; where it doesn't, credit "© OpenStreetMap contributors" on the map (as the UK map does for Ireland) and record it under "Decisions to check".
