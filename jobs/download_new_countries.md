# Job: downloads for the new country maps

Everything the builds in [build_countries.md](build_countries.md) need, downloaded into `tools/downloads/<code>/` (git-ignored). Started 2026-11-17. **The main downloads are done; the extra sources for the chosen card facts (below) are still to fetch.** Run from the repo root.

## The countries (decided 2026-11-17)

| Country | Code | Parts | Games 5 and 6 |
| --- | --- | --- | --- |
| Mexico | `mx` | 31 states and Mexico City | coats of arms |
| Brazil | `br` | 26 states and the Federal District | flags |
| Germany | `de` | 16 states | flags |
| Japan | `jp` | 47 prefectures (9 regions as a filter) | flags |
| France | `fr` | 13 metropolitan regions (overseas regions left off) | none |
| Italy | `it` | 20 regions (+ 107 provinces as a second set: to confirm) | flags |
| Spain | `es` | 17 communities, Ceuta and Melilla; and the 50 provinces as a second set | flags (communities) |
| Nigeria | `ng` | 36 states and the FCT | none for now (seal games shelved) |
| Argentina | `ar` | 23 provinces and the City of Buenos Aires | flags |

Later candidates: South Africa (9 provinces), Egypt (27 governorates), South Korea, New Zealand. Indonesia and Kenya need a source other than Natural Earth (its divisions are out of date).

## Done (2026-11-17)

`python tools/fetch_country_data.py jp de fr it es ng ar` (re-running skips what's already there). Everything goes into `tools/downloads/<code>/`, which git ignores:

- `wikidata.json`: every division with an ISO 3166-2 code, from Wikidata: its kinds (prefecture, state, region, department, province…), English and local Wikipedia titles, flag and coat of arms files, capital, and whether it's dissolved (old regions, merged provinces). Use `"dissolved": false` entries; the `kinds` tell the levels apart (France's regions from its departments, Spain's communities from its provinces, Italy's regions from its provinces).
- `wiki/en/` and `wiki/<local>/` (ja, de, fr, it, es; Nigeria is English only): each division's Wikipedia article as raw wikitext, the sources for the Learning card facts.
- `wiki/lists/`: the list articles (census figures, areas, capitals) as raw wikitext.
- `flags/`, `coats/`: flags and coats of arms from Wikimedia Commons, 640 px PNG, named by ISO code.
- `coast_f.geojson`: full-resolution shoreline (GSHHG, about 100 m), land and lakes, clipped to the country.
- **Shapes** come from Natural Earth admin-1 (`tools/downloads/ne10/`, already downloaded). All seven are complete there; France, Italy and Spain list their lower level (departments, provinces) with a `region` field to group them into the upper level.
- Also downloaded for **Mexico and Brazil** (not built yet): `tools/downloads/mx/coast_f.geojson` and `tools/downloads/br/coast_f.geojson`.

Download results: see "Download log" at the end.

Mexico and Brazil's other data was fetched earlier: see "Mexico (ready)" and "Brazil (ready)" in [build_countries.md](build_countries.md).

## Still to fetch (status 2026-11-17)

Re-running a script skips what's already there. **Images:** Wikimedia now only serves standard thumbnail widths (20, 40, 60, 120, 250, 330, 500, 960, 1280…) and rejects or throttles others, so `tools/fetch_country_data.py` asks for **500 px** (it asked for 640 before, which caused most of the failures). The older build scripts (`build_ca.py`, `build_ru.py`, `build_au.py`, `build_uk.py`) still say 640: change them to 500 if they're run again.

1. ~~**The local-language articles**~~ **Done:** Japanese 46 of 47, German 16, French 123, Italian 124, Spanish 64, Argentine Spanish 24 (`wiki/<lang>/`). Find the one Japanese article missing (compare `wikidata.json` with `wiki/ja/`).
2. **Mexico:** Colima's coat of arms (`Escudooficialcolima.jpg`) is **still missing** (rate-limited twice); fetch it at 500 px into `tools/downloads/mx/coats/Colima.png`.
3. **Census totals:** the census articles are saved in `wiki/lists/` (Demographics of Japan, the 2022 German census, Demographics of France, the 2021 Italian census, Demographics of Spain, the Argentina census; Nigeria's 2006 census still to come, item 4). **Still to do:** read each country's official national total (and its census year) from them into `tools/downloads/<code>/census.json` with the source, and where possible check it against the statistics office's own figure. The build checks that the parts add up to it.
4. **Sources for the chosen card facts:** `python tools/fetch_country_data.py --extras <codes>` saves the list articles below into `wiki/lists/` (each found by search; `extras.json` records which article each search found; check it), plus Nigeria's seals and the Japanese font.
   - **Done:** Japan 9 of 9 (Demographics of Japan, Flags of Japanese prefectures, Yuru-kyara, Provinces of Japan, Onsen, Meibutsu, List of traditional crafts of Japan, Japanese dialects, List of castles in Japan; the prefectural flower, tree and bird come from each prefecture's own article); **the Japanese font** `tools/downloads/fonts/NotoSansJP.ttf` (9.4 MB; subset at build time); Germany 6 of 6; France 6 of 6 (the 2016 reform search found *Regions of France*, which covers it); Italy 6 of 6; Spain 9 of 9 (including the Valencian, Basque and Galician language articles); Argentina 5 of 5.
   - **Nigeria: the seals are shelved (2026-11-17).** The download was paused at Kaduna with 6 seals in `tools/downloads/ng/seals/` (Abia, Akwa Ibom, Bauchi, Benue, Borno, Edo). Several seal images (Abuja, Gombe, Kaduna) are only on English Wikipedia, not Commons, which usually means they're not freely licensed; check licences before using any. Still to fetch when this is picked up again: the rest of the seals (Kaduna to Zamfara), and 2 list articles (the 2006 census, traditional rulers: re-run `--extras ng`, the search now falls back to full text).
   - **Spain's languages layer:** the language articles are saved, but **an open data source for where each language is spoken is still to find** (for example the municipalities of the Valencian-speaking area and of Navarre's Basque zones, which are fixed in law, joined to municipal boundaries from geoBoundaries, CC BY 4.0). Check its licence and note the credit.
5. Keep the download log below up to date.

## Learning card facts (chosen 2026-11-17; for reference: the builds use them)

Every card also has the name, kind, capital, population (latest census), area and rank, and the flag (or seal) where there is one. Leave out any fact that isn't found rather than guess.

- **Germany (17):** name in German; demonym; dialect; famous dish; beer or wine; biggest festival or tradition; football: biggest club; main river; highest point; coast (North Sea, Baltic, or landlocked); natural wonder or national park; former kingdom or duchy; East or West Germany before 1990; famous castle or landmark; UNESCO World Heritage; known for; famous company from there. (Borders: not chosen.)
- **Japan (18):** name in kanji with its reading; region; famous food or meibutsu; famous festival; traditional craft; dialect; highest point; main river or lake; natural wonder; hot springs; prefectural flower, tree and bird; old province name; famous castle or temple; UNESCO World Heritage; name meaning; known for; mascot; largest city if it isn't the capital.
- **France (18):** name in French; demonym; regional language; famous dish; famous cheese; famous wine or drink; biggest festival; highest point; main river; coast; natural wonder or national park; historic provinces it covers; formed (2016 merger, or unchanged); famous landmark; UNESCO World Heritage; famous person from there; known for; largest city if it isn't the capital.
- **Italy (18):** name in Italian; demonym; dialect or minority language; famous dish; protected food (DOP/IGP); famous wine; biggest festival; special-statute region or not; highest point; main river or lake; volcano or natural wonder; coast or islands; before unification (which state); famous landmark; UNESCO World Heritage; famous person from there; known for; largest city if it isn't the capital.
- **Spain (18, communities and the two cities):** name in Spanish and in its own language; co-official language; demonym; famous dish; drink; biggest fiesta; music or dance; football: biggest club; highest point; main river; coast; natural wonder or national park; old kingdom; Moorish heritage; famous landmark; UNESCO World Heritage; known for; largest city if it isn't the capital. **The 50 provinces** get a shorter card: name, capital, population, community, a landmark.
- **Nigeria (17):** nickname (the number-plate slogan); main ethnic groups; main languages; main religions; famous dish; biggest festival; traditional ruler; main river; climate or vegetation; highest point; natural wonder or park; created (year) and from which state; old kingdom or empire; UNESCO World Heritage; known for; largest city if it isn't the capital; famous person from there. (Geopolitical zone: not chosen.)
- **Argentina (18):** demonym; region; famous food; drink; music or dance; biggest festival; Indigenous peoples; football: biggest club; highest point; main river or lake; natural wonder or national park; climate; famous animal; became a province (1853 founder or former national territory); UNESCO World Heritage; famous person from there; known for; largest city if it isn't the capital.

## Download log (2026-11-17)

| Country | Divisions (current) | English articles | Local articles | List articles | Flags | Coats of arms | Seals | Coast |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Japan | 47 | 47 | 46 (ja) | 12 | 47 | 47 | – | 9.7 MB |
| Germany | 16 | 16 | 16 (de) | 7 | 16 | 16 | – | 1.1 MB |
| France | 123 (regions and departments) | 123 | 123 (fr) | 8 | 114 | 112 | – | 2.4 MB |
| Italy | 124 (regions and provinces) | 124 | 124 (it) | 7 | 106 | 120 | – | 3.4 MB |
| Spain | 67 (communities, cities, provinces) | 62 | 64 (es) | 11 | 56 | 64 | – | 2.0 MB |
| Nigeria | 37 | 37 | – | 4 | 13 | 6 | 6 (paused, shelved) | 0.6 MB |
| Argentina | 24 | 24 | 24 (es) | 6 | 24 | 24 | – | 7.9 MB |
| Mexico | (earlier) | 32 | 32 | – | 32 | 31 (Colima missing) | – | 8.2 MB |
| Brazil | (earlier) | 27 | 27 | – | 27 | – | – | 6.9 MB |

- The flag counts include divisions that aren't used (France's departments, Italy's and Spain's provinces); every part that's used has its flag where it has one, except Spain's Girona province flag (not used).
- Nigeria's flags and coats of arms are thin, as expected: its seal games use `seals/`.
- Japanese font: `tools/downloads/fonts/NotoSansJP.ttf`.
