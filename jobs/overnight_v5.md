# Job: overnight v5, seven Nordic and Baltic country maps

Norway, Denmark, Finland, Iceland, Estonia, Latvia and Lithuania: first the downloads, then the builds. Decided with the user on 2026-11-27. **Nothing here is started yet.**

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
