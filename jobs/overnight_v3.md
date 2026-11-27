# Job: overnight v3, six more country maps

Switzerland, Portugal, Sweden, South Africa, New Zealand and Colombia: first the downloads, then the builds. Decided with the user on 2026-11-18. **Done 2026-11-26 (started at the user's word): all six built and tested; see "Results" at the end. Not committed until the user says so.** The next five countries are in [overnight_v4.md](overnight_v4.md).

**Don't start this job until the user says so** (decided 2026-11-18), and don't change the other job files to make room for it. Push only when the user says so.

It works exactly like [overnight_v2.md](overnight_v2.md): the builds follow **"The checklist for every build"** in [build_countries.md](build_countries.md), and the downloads use the same scripts and folders as [download_new_countries.md](download_new_countries.md). Read all three first. The rules of the last overnight run ([OVERNIGHT.md](OVERNIGHT.md)) apply if this is run overnight: judgement calls allowed and recorded, missing data doesn't block a build, tests are the bar, and nothing that worked before may break. Where this file and the checklist differ, this file wins.

## The countries (decided 2026-11-18)

| Country | Code | Parts | Games 5 and 6 | Small parts |
| --- | --- | --- | --- | --- |
| Switzerland | `ch` | 26 cantons | flags | circles for the smallest (Basel-Stadt, Appenzell Innerrhoden, Zug; check others on the phone) |
| Portugal | `pt` | 18 districts and the 2 autonomous regions (Azores, Madeira): 20 | coats of arms, if every district has one (see below) | insets for the Azores and Madeira |
| Sweden | `se` | 21 counties | coats of arms | – |
| South Africa | `za` | 9 provinces | none (no official flags) | – |
| New Zealand | `nz` | 16 regions and the Chatham Islands: 17 | none (no official flags) | an oval for the Chatham Islands |
| Colombia | `co` | 32 departments and Bogotá: 33 | flags | a circle for Bogotá, an oval for San Andrés and Providencia |

- **Every one** gets the Find and Name games for its parts and capitals (and games 5 and 6 where the table says), the Learning card with the facts below, Focus on, a stats tab, and the high-resolution coast. No timelines or layers for now.
- **Switzerland:** cantons with several pieces (Fribourg, Bern, Solothurn and others have small exclaves): every piece belongs to its canton. Liechtenstein is grey context. Local names in German, French and Italian (`wiki/de/`, `wiki/fr/`, `wiki/it/`), and Romansh where it's official (Graubünden). Accept the English, German, French and Italian names (Geneva / Genève / Genf / Ginevra).
- **Portugal:** the districts' coats of arms are on Commons; if all 18 are found, games 5 and 6 are **coat-of-arms games** like Mexico's, with the Azores and Madeira using their flags. If some are missing, they sit out those games and are listed under "Waiting for data". Record the choice under "Decisions to check".
- **Sweden:** the county coats of arms are official; games 5 and 6 are coat-of-arms games. Gotland is big enough without an oval.
- **South Africa: Lesotho and Eswatini** (decided 2026-11-18) are treated like Vatican City and San Marino on the Italy map: **drawn in their flag colours, not grey** (proposed: **Lesotho blue**, **Eswatini red**; record under "Decisions to check"), tappable, each with its own **"Focus on Lesotho" / "Focus on Eswatini"** button. **Their own maps are a separate job, planned later** (Lesotho's 10 districts, Eswatini's 4 regions); until then the button can show "Coming soon". They're proper shapes, not circles. The Prince Edward Islands (part of the Western Cape, far in the Southern Ocean) are left off.
- **New Zealand:** the Chatham Islands aren't in any region; they're their own part (17). The other outlying islands (Kermadec, the subantarctic islands) are left off. Accept Māori names (Tāmaki Makaurau for Auckland's region where used, Te Tai Tokerau for Northland and so on, from the downloaded articles).
- **Colombia:** Bogotá is a Capital District inside Cundinamarca: a circle. San Andrés, Providencia and Santa Catalina are far off in the Caribbean: an oval (or an inset if the oval sits too far from the mainland on the phone).

## Part 1: downloads

As in overnight_v2, Part 1:

1. `python tools/fetch_country_data.py ch pt se za nz co`, with the local languages (de, fr, it for Switzerland; pt; sv; af and zu are optional for South Africa, English is enough; mi is optional for New Zealand; es for Colombia).
2. **Shapes:** Natural Earth admin-1. Check each country's count matches the table (26, 20, 21, 9, 17, 33). Portugal's Natural Earth list may be the districts plus the islands; New Zealand's may lack the Chatham Islands as a part (cut it out if so). If any is out of date, use geoBoundaries ADM1 (CC BY 4.0, credit it).
3. **Census totals** into `census.json` with source and year: Switzerland (FSO STATPOP, latest), Portugal (Census 2021), Sweden (SCB, latest register figure; say so on the card), South Africa (Census 2022), New Zealand (Census 2023), Colombia (DANE Census 2018).
4. **Fact sources:** `--extras` with searches for the country-specific facts below (for example "Cantons of Switzerland" for joining years, "Wine regions of Portugal", "Provinces of Sweden", "Sápmi", "Bantustan", "Iwi", "Natural regions of Colombia").
5. **Download log** at the end of this file.

## Part 2: builds

Order: **Sweden, South Africa, New Zealand, Portugal, Colombia, Switzerland** (simplest first; Switzerland last because of its many small cantons and exclaves).

1. **Plans first:** `Switzerland_plan.md`, `Portugal_plan.md`, `Sweden_plan.md`, `South_Africa_plan.md`, `New_Zealand_plan.md`, `Colombia_plan.md`, from this file, with no open questions.
2. **Build each one** with the checklist (`tools/build_<code>.py`, `tools/<code>_facts.py`, the app wiring with each in `COUNTRY_MAPS` under its continent, small parts, tests, preview, PLAN.md).
3. **Tests also check:** Switzerland's exclaves open their canton's card; Lesotho and Eswatini show in their colours, open their own cards and Focus buttons, and don't block taps on the provinces around them; the Chatham Islands, San Andrés and the Portuguese islands open their cards from the oval or inset.

## Learning card facts (chosen 2026-11-18)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag or coat of arms. Leave out any fact that isn't found rather than guess.

**All six (17):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage Sites; famous person from there; known for; famous company from there; largest city if it isn't the capital.

**Plus three for each country (20 in all):**

- **Switzerland:** main language (German, French, Italian or Romansh); year it joined the Confederation (1291 for Uri, Schwyz and Unterwalden, up to Jura in 1979); famous cheese or chocolate.
- **Portugal:** wine region (Douro, Alentejo, Vinho Verde); historic province (Minho, Beira, Algarve); famous explorer or Age of Discovery link.
- **Sweden:** historic land (Götaland, Svealand, Norrland) and province; Sámi area (yes or no, and which part); famous Swedish invention or brand from there.
- **South Africa:** main home languages (Zulu, Xhosa, Afrikaans, English and others); Big Five game reserve or famous wildlife; what it was before 1994 (Transvaal, Cape Province, Natal, Orange Free State, and the former homelands it took in).
- **New Zealand:** Māori name and the main iwi; North or South Island; famous film location (Lord of the Rings sites).
- **Colombia:** natural region (Andes, Caribbean, Pacific, Orinoquía, Amazon); famous coffee, fruit or crop; music style (vallenato, cumbia, salsa).

## Results (2026-11-26)

Built with the shared builder from overnight_v2 (`python tools/build_country.py <code>` and `tools/<code>_facts.py`), which gained what this batch needed:
- `INSETS`: parts moved (and scaled) into framed insets, with the shoreline moved the same way for the detail level (Portugal's Azores at half size and Madeira; Colombia's San Andrés moved closer); also New Zealand's Chatham Islands, moved 360° east across the date line without a frame.
- `ISLES`: tappable ovals (elliptical where needed) around far islands (the Azores, Madeira, San Andrés, the Chathams).
- `ENCLAVES`: independent countries drawn as shapes in their own colour (South Africa's Lesotho and Eswatini), Learning mode only, short card. The map's `fillFor` uses `info.fill`.
- `CLIP` (far islands left off), `NE_FIX` (Natural Earth's duplicate code for Bogotá), `DETAIL_TOL`, `TOTAL_TOL`, `LANDLOCKED`, coat-of-arms games (`emblems`), several card specials per country (`specials`).
- **Coast now means the sea:** a part is "coastal" only if it touches the outer edge of all the land on the map, so lake shores (the IJsselmeer, Lake Geneva) don't count. This also corrected overnight_v2's Netherlands (Drenthe, Overijssel and Utrecht were marked coastal) and Colombia's Amazonas and Putumayo.

Projections: Sweden transverse Mercator 15°E; South Africa Albers (24°S, 33°S, 25°E); New Zealand transverse Mercator 173°E; Portugal transverse Mercator 8.13°W; Colombia transverse Mercator 73°W; Switzerland Lambert conic (45.8°N, 47.8°N, 8.23°E). SW cache v77 (unchanged since overnight_v2: nothing is released yet).

### Download log

| Country | Divisions (Wikidata) | English articles | Local articles | List articles | Flags | Coats of arms | Coast |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Sweden | 21 | 21 | 21 (sv) | 8 | 20 | 21 | 17.0 MB |
| South Africa | 9 | 9 | – | 8 | 6 (unofficial, not used) | 1 | 735 KB |
| New Zealand | 19 | 19 | – | 7 | 4 | 0 | 2.9 MB |
| Portugal | 20 | 20 | 20 (pt) | 7 | 2 (Azores, Madeira) | 2 | 530 KB |
| Colombia | 33 | 33 | 33 (es) | 7 | 33 | 33 | 1.8 MB |
| Switzerland | 26 | 26 | 26 each (de, fr, it) | 8 | 26 | 26 | 102 KB |

Natural Earth's admin-1 matched (21, 9, 17 after dropping the outlying islands and Tokelau, 20, 33 after splitting Bogotá, 26); geoBoundaries wasn't needed.

### Populations (all checked against a national total)

- Sweden: SCB population register, 31 December 2024 (open API), 10,587,710.
- South Africa: Census 2022, 62,027,503 (the provinces add up to 1 less: Stats SA's rounding; allowed).
- New Zealand: Census 2023, 4,993,923 (the 16 regions and the Chathams are 18 short: other outlying islands and random rounding; allowed).
- Portugal: Census 2021, 10,343,066.
- Colombia: Census 2018 (DANE's adjusted total), 48,258,494.
- Switzerland: STATPOP, 31 December 2025 (FSO PxWeb API), 9,127,125.

### Decisions to check

1. **Portugal has no games 5 and 6.** The districts have no coats of arms of their own (their articles show the capital cities' arms), and only the Azores and Madeira have flags (2 of 20). Alternative: use the capital cities' arms, but that would be misleading.
2. **Lesotho and Eswatini's colours:** Lesotho a soft blue (#7fa4d6), Eswatini a soft red (#d98073). Their card says "Its own map: coming soon"; the "Focus on" button comes with their maps (as for Vatican City and San Marino).
3. **Sweden's detail level is simplified more (0.0035°)**: 6.3 MB instead of 8.5 MB because of the archipelagos.
4. **Insets:** the Azores at half size west of northern Portugal, Madeira west of Lisbon; San Andrés moved into a small frame north of the Panama border; the Chathams beside the mainland, unframed.
5. **Capitals outside the part:** Cundinamarca (Bogotá) sits out the capitals games. The Azores' three capitals are all accepted, each with a dot.
6. **South Africa's province cards show no flags** (the downloaded ones are unofficial).
7. **The coast rule changed** (above): enclosed lakes don't make a part coastal; Flevoland stays coastal, as does Santarém (it reaches the Tagus estuary).

### Tests

All pass (final run after the coast change, 2026-11-26). `_bench_nm.html?d=<code>&r=<region>` for all six and, again, the overnight_v2 maps: every part's anchor opens its card (Lesotho and Eswatini included); names, unaccented forms and capitals accepted, notTypo refused, no part accepting another's name; capital dots (the enclaves have none: they're not in the games); flags or coats of arms load; card facts; the tap test at whole-map, 2.5x and close zoom with the detail level on (100% everywhere; the zoomed test now takes its points from the detail shapes and zooms on the most populous part). `_bench_menu.html`: the Countries tab lists all eleven; in a South Africa game Lesotho and Eswatini are inactive, in Learning mode active; Sweden's game says "Find by coat of arms"; Belgium's and Spain's set switches, stats, Focus on Austria, and the US and Russia timelines still work; no script errors. Screenshots checked by eye (light and dark).

The Sweden run first showed the whole world: its projection style was missing from js/mapview.js (the anchor test caught it); fixed, along with Switzerland's card, whose "language" fact clashed with the card's own "lang" field.

### Review with the user (2026-11-26)

Approved: Austria's arms flags, Portugal without games 5 and 6, the soft enclave colours, the Netherlands' land area, Sweden's lighter detail, the sea-only coast rule, and the latest figures for Poland and Czechia (**the latest official figure is now the default for every country**: jobs/overnight_v4.md updated). Changed at the user's request:
- **Inset tap areas follow their square frames** (shaded, dashed outline; the solid frame line is gone): Portugal's Azores and Madeira, Colombia's San Andrés. `square: true` isles, drawn with straight lines (js/mapview.js `squareLine`).
- **A scale bar (trial)** on the main flat map, bottom left, in km and miles, measured where it's drawn (`drawScaleBar` in js/mapview.js). Not on the globe or the magnifier; inside a scaled inset (the half-size Azores) it doesn't apply.
- **Each framed inset has its own fixed scale bar** (km and miles, a round distance about a third of the frame wide, at the inset's own scale: 200 km for the half-size Azores). Made by `inset_scale_bars` in tools/build_country.py, stored as `scaleBars` in the states file, drawn by `drawScaleBar`; it's map geometry, so it zooms with the inset, and it hides while shorter than 12 px (San Andrés at whole-country zoom).
- **Inset frames are straight on the screen**: a lon/lat box leans under the projection, so the app draws each frame as the screen-aligned rectangle round its projected corners (Portugal's and Colombia's square tap areas in `shapeOf`; Spain's Canaries frame, now a `frames` entry drawn by `drawFrames` instead of a border line).
- **The Canaries have their own scale bar** (100 km / 100 mi, top left of the frame, clear of El Hierro): they're moved 6.5° north without scaling, so east–west they're drawn about 7% narrower than the mainland's scale (tools/build_es.py `canaries_scale_bars`). Inset bars are drawn level.
- Follow-ups (2026-11-27): inset scale bars put the miles bar a fixed 12 px under the km bar (Spain's crowded when zoomed out); the Countries tab's continents are collapsible (closed at first; the open ones are remembered in prefs `openConts`); the Learning card always opens collapsed (closing it resets "More facts").
- Fix (2026-11-27): no zooming while the Discover magnifying glass plays. A pinch on its overlay zoomed the whole page (which couldn't then be undone); the overlay now cancels wheel, touch and gesture events (`touch-action: none`), and the map's d3 zoom ignores all input while `main.locked` (set for the length of the animation).
