# Job: overnight v11, five South and Central Asian country maps

Bangladesh, Sri Lanka, Nepal, Kazakhstan and Uzbekistan: first the downloads, then the builds. Decided with the user on 2026-11-28. **The downloads are done (2026-11-28, see the log at the end); the builds aren't started.**

**Don't start this job until the user says so**, and don't change the other job files to make room for it. Don't commit or push until the user says so.

It works like [overnight_v4.md](overnight_v4.md): the shared builder (`tools/build_country.py`, `tools/<code>_facts.py`), one `NEW_MAPS` row and a projection style each (add the style first), the same tests. Where this file and the earlier ones differ, this file wins.

## The countries (decided 2026-11-28)

| Country | Code | Parts | Games 5 and 6 | Small parts |
| --- | --- | --- | --- | --- |
| Bangladesh | `bd` | **8 divisions** (bibhag) | none (no divisional flags) | – |
| Sri Lanka | `lk` | **9 provinces** | flags (provincial flags are official) | – |
| Nepal | `np` | 7 provinces (pradesh) | none expected (check: some provinces have adopted flags) | – |
| Kazakhstan | `kz` | 17 regions (oblystar) and 3 cities (Astana, Almaty, Shymkent): 20 | none expected (regions have emblems): check | circles for the 3 cities |
| Uzbekistan | `uz` | 12 regions (viloyatlar), the Republic of Karakalpakstan and Tashkent city: 14 | none expected (check Karakalpakstan's flag) | a circle for Tashkent city |

- **Bangladesh (decided 2026-11-28): build the 8 divisions.** Also download the 64 districts (shapes, names, capitals, populations) into `tools/downloads/bd/districts/` for a possible second set later. Don't build them now. Check Natural Earth has 8 (Mymensingh was split from Dhaka in 2015). Bengali names on the cards: **download Noto Sans Bengali** and subset it (`tools/build_fonts.py`).
- **Sri Lanka (decided 2026-11-28): build the 9 provinces.** Also download the 25 districts into `tools/downloads/lk/districts/` for later. Don't build them now. Sinhala and Tamil names on the cards: **download Noto Sans Sinhala and Noto Sans Tamil** and subset them. Adam's Bridge is geography for the card, not a dispute.
- **Nepal:** 7 provinces since 2015, with their names since 2018–2023 (Koshi, Madhesh, Bagmati, Gandaki, Lumbini, Karnali, Sudurpashchim): check Natural Earth has the new provinces, not the old 14 zones; use geoBoundaries ADM1 (credited) if not. **Kalapani, Lipulekh and Limpiyadhura** (India governs them; Nepal claims them and put them on its 2020 map) follow the disputes layer: check they're there, add them with a source if not. Nepali names in Devanagari: **download Noto Sans Devanagari** and subset it.
- **Kazakhstan:** the 2022 reform made 3 new regions (Abai, Jetisu, Ulytau): 17 regions and 3 cities. **Natural Earth may have the old 14:** use geoBoundaries ADM1 if it's current, or split the old regions with the district boundaries of the new ones; record which. Very wide: check it fits a tall phone screen at a usable size. Baikonur (leased to Russia) is a note on its region's card, not a part. Kazakh names in Cyrillic (the subset: check ә ғ қ ң ө ұ ү һ і) and Latin.
- **Uzbekistan:** 12 regions, Karakalpakstan (an autonomous republic, a large part in the west) and Tashkent city (separate from Tashkent Region: a circle). Uzbek names in Latin (oʻ, gʻ: check the subset) and Cyrillic.

Every country: Find and Name for the parts and capitals (games 5 and 6 where the table says), the Learning card, Focus on, a stats tab, the high-resolution coast. No timelines or layers.

## Part 1: downloads

1. Add the five to `tools/fetch_country_data.py` (local Wikipedia languages: bn, si (and ta), ne, kk (and ru), uz) and `COUNTRY_QID`.
2. `--extras` and `--census`, with searches for the facts below (for example "Rivers of Bangladesh", "Sundarbans", "Textile industry in Bangladesh", "Ceylon tea", "Ancient cities of Sri Lanka", "Sinhala language", "Mountains of Nepal", "Ethnic groups in Nepal", "Stupas in Nepal", "Kazakh Steppe", "Mining in Kazakhstan", "Baikonur Cosmodrome", "Silk Road", "Khanate of Khiva", "Suzani").
3. **Fonts:** Noto Sans Bengali, Noto Sans Sinhala, Noto Sans Tamil, Noto Sans Devanagari; check the Cyrillic and Latin subsets cover Kazakh and Uzbek letters.
4. **Shapes:** Natural Earth admin-1 where current; geoBoundaries ADM1 for Kazakhstan (20) and, if needed, Nepal (7). Check every count (8, 9, 7, 20, 14).
5. **Populations: the latest official figure by default:** BBS Bangladesh (the 2022 census), DCS Sri Lanka (the 2024 census if out, otherwise the latest estimate), NSO Nepal (the 2021 census), the Bureau of National Statistics of Kazakhstan (latest), the Statistics Agency of Uzbekistan (latest); each checked against the national total.
6. **Bangladesh's 64 districts and Sri Lanka's 25 districts:** data for later (see above).
7. Download log at the end of this file.

## Part 2: builds

Order: **Sri Lanka, Bangladesh, Nepal, Uzbekistan, Kazakhstan** (Kazakhstan last: the 2022 regions and its size).

1. Plans first: `Bangladesh_plan.md`, `Sri_Lanka_plan.md`, `Nepal_plan.md`, `Kazakhstan_plan.md`, `Uzbekistan_plan.md`, with no open questions.
2. Build, wire, test (all must pass), preview, PLAN.md, results and decisions to check at the end of this file.
3. **Tests also check:** Bengali, Sinhala, Tamil and Devanagari names show in light and dark themes; Kalapani's dispute card opens; Kazakhstan's 3 city circles and Tashkent city tap right.

## Learning card facts (the 17 approved by the user 2026-11-27; the three per country approved 2026-11-28)

Every card also has the name, kind, capital, population (latest figure), area and rank, and the flag where there is one. Leave out any fact that isn't found rather than guess.

**All five (17):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club (cricket where it's the bigger sport: Bangladesh, Sri Lanka, Nepal); main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital.

**Plus three for each country:**

- **Bangladesh:** big river (Padma, Jamuna, Meghna); textiles, jute or tea; mangroves, hills or beach.
- **Sri Lanka:** main language (Sinhala, Tamil); tea; ancient city or temple.
- **Nepal:** Himalayan peak; main ethnic group; temple or stupa.
- **Kazakhstan:** steppe, desert or mountains; mineral resource (oil, uranium...); nomadic heritage or space site.
- **Uzbekistan:** Silk Road city; craft (silk, ceramics, suzani); historic khanate or empire.

## Download log (2026-11-28)

Downloaded ahead of the run (the user asked for the data first). `python tools/fetch_country_data.py --extras --no-images <codes>`, then `--census`, `python tools/fetch_boundaries.py` (geoBoundaries, into `tools/downloads/<code>/geoboundaries/`, with each file's licence in its .json), then the flags and coats of arms at Commons' pace (no failures; Slovenia's 212 municipal arms skipped: not needed).

| Country | Wikidata divisions (current) | Natural Earth admin-1 | English articles | Local articles | List articles | Flags | Coats of arms | Coast | Census items | geoBoundaries |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Bangladesh | 72 (8 divisions, 64 districts) | 7 (want 8: no Mymensingh) | 72 | 72 (bn) | 6 | 0 | 0 | 0.8 MB | 73 | BGD_ADM1 (8), BGD_ADM2 (64) |
| Sri Lanka | 34 (9 provinces, 25 districts) | 25 districts (want 9 provinces) | 34 | 34 (si), 34 (ta) | 6 | 9 | 0 | 0.4 MB | 13 | LKA_ADM1 (9), LKA_ADM2 (25) |
| Nepal | 7 (Gandaki added by hand: it has no ISO code in Wikidata) | 14 old zones (want 7) | 7 | 7 (ne) | 6 | 0 | 0 | – | 8 | NPL_ADM1 (7) |
| Kazakhstan | 20 | 16 (want 20: before the 2022 reform) | 20 | 20 (kk), 20 (ru) | 6 | 6 | 18 | 1.0 MB | 21 | KAZ_ADM1 (16, old), KAZ_ADM2 |
| Uzbekistan | 14 | 14 (want 14) | 14 | 14 (uz) | 6 | 2 | 2 | 0.1 MB | 13 | UZB_ADM1 |

**Shapes to use** (checked 2026-11-28):

- **Bangladesh:** geoBoundaries BGD ADM1 (8 divisions, 2015, CC0); the 64 districts from BGD ADM2 (BBS/OCHA 2020, CC BY 3.0 IGO).
- **Sri Lanka:** dissolve Natural Earth's 25 districts into the 9 provinces (the table in `Provinces of Sri Lanka`); geoBoundaries LKA ADM1/ADM2 (OpenStreetMap, ODbL) only as a cross-check.
- **Nepal:** geoBoundaries NPL ADM1 (7 provinces, Survey Department of Nepal 2020, CC BY 3.0 IGO), credited.
- **Kazakhstan:** **OpenStreetMap** (the only source with the 2022 regions: Abai, Jetisu, Ulytau): `tools/downloads/kz/osm/admin4.geojson`, 20 units, from `python tools/fetch_osm_admin.py kz` (ODbL: "© OpenStreetMap contributors" on the map, as decided 2026-11-27).
- **Uzbekistan:** Natural Earth, current.
- **Fonts:** `tools/downloads/fonts/` NotoSansBengali, NotoSansSinhala, NotoSansTamil, NotoSansDevanagari.
- **Bangladesh's 64 and Sri Lanka's 25 districts:** in each country's wikidata.json, wiki/ and census.json (the districts have ISO codes), shapes in geoBoundaries ADM2 / Natural Earth.
- **Flags:** Sri Lanka 9 of 9 (games 5 and 6 on); Kazakhstan 6 flags, 18 coats of arms (regional emblems: none, as planned, unless all 20 are found).
