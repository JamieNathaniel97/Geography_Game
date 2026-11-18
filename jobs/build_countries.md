# Job: country builds

Building the new country maps (the Countries tab, and "Focus on <country>" in Learning mode). Started 2026-11-17. The data comes from [download_new_countries.md](download_new_countries.md). Each country's decisions are below; its plan file (where there is one) has the rest, and wins where the two differ.

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

## Standards for every new country (decided)

- **High-resolution coasts** (decided 2026-11-17; [PLAN.md](../PLAN.md), "High-resolution coasts"): the light file for loading and zoomed out, plus a detail level (coast and borders to about 100–200 m from `coast_f.geojson`) loaded in tiles only when zoomed in. Fit each region's edge to the new shoreline (`fit_to_land` in `tools/build_uk.py`). Mexico and Brazil get it too. The maps already built are **not** redone now (noted in PLAN.md for later).
- **Disputed areas:** disputed borders dotted, disputed areas grey and untappable (as for India, China and Russia).
- **Populations:** the latest census, checked against the national total the way Russia's and Brazil's were.
- **Learning cards:** about 17–18 facts per part, chosen by the user in each plan; the native-script names get a font subset (`tools/build_fonts.py`) where needed (Japanese).
- **Games:** Find and Name for the parts, their capitals, and their flags (or coats of arms where flags aren't official, as for Mexico); a part with no capital or flag sits out those games (like Jervis Bay).
- **Tiny parts:** adaptive circles, island ovals; no numbered bubbles (Russia's was removed 2026-11-17).
- **Timelines and layers:** proposed in each plan, decided by the user.

## Plans

Mexico and Brazil have their plans ([Mexico_plan.md](../Mexico_plan.md), [Brazil_plan.md](../Brazil_plan.md)). For the other seven, write `Germany_plan.md`, `Japan_plan.md`, `France_plan.md`, `Italy_plan.md`, `Spain_plan.md`, `Nigeria_plan.md`, `Argentina_plan.md` from the decisions and facts below, in the same style as the existing plans. Still open: Italy's provinces, and every timeline (see [README.md](README.md), "Morning agenda").

## The builds

**Ready now:** Mexico and Brazil (plans answered, data downloaded). **After their plans are answered:** the seven countries above. Build them in this order:

1. **Mexico** ([Mexico_plan.md](../Mexico_plan.md))
2. **Brazil** ([Brazil_plan.md](../Brazil_plan.md))
3. **Germany** (quickest of the new ones)
4. **Japan**
5. **France**, 6. **Italy**, 7. **Spain** (they share the two-level pattern: build the first, reuse for the others)
8. **Nigeria**, 9. **Argentina**

The first build (Mexico) also builds the **detail-level coast** machinery (tiles, loader, switching at the zoom threshold); every later build reuses it.

### The checklist for every build

Follow the country's plan; where the plan and this checklist differ, the plan wins. Model the code on the latest built country (`tools/build_ru.py`, `tools/build_au.py` and their app wiring).

1. **Data build, `tools/build_<code>.py`:**
   - shapes from Natural Earth admin-1 (`tools/downloads/ne10/`), dissolved to the plan's level (regions from departments or provinces via the `region` field); ids `"<CC>-<code>"` so stats can't clash with another country's codes
   - neighbours as grey context in a window wide enough for a tall phone screen (check that the grey reaches the screen edges); `coverage_clean` + `coverage_simplify`, `set_precision`; `borders`, `coast` and (if needed) `disputed` lines; a point inside each part as its anchor when the centroid falls outside (`anchorLL`)
   - **detail level:** fit the parts to `tools/downloads/<code>/coast_f.geojson` (`fit_to_land`), simplify to about 100–200 m, cut into tiles (`data/<code>-detail/`), each with its parts and lines
   - `data/<code>-parts.json`: name, other names and spellings, `notTypo` pairs, capitals (and spellings), `capLL` (`tools/capitals.py`, with manual coordinates for any it can't find), kind, region, population (latest census; **the parts must add up to the official national total**), area and rank, flag or coat of arms present, coastal and borders, facts
   - flags or coats of arms from `tools/downloads/<code>/flags/` or `coats/` into `data/flags/<code>/` (WebP)
2. **Facts, `tools/<code>_facts.py`:** the plan's chosen facts for every part, from the downloaded articles (`wiki/en/`, `wiki/<local>/`); leave a fact out rather than guess; native-script names get a font subset (`tools/build_fonts.py`) where the script isn't Latin.
3. **App wiring:** `DATASETS` entry (noun, nouns, unit, style, count, `noFlags` or coats of arms), `REGIONS` entry, `COUNTRY_MAPS` (drop `soon`), loader in `js/geo.js` (rings, clusters: none), projection style in `js/mapview.js` (the plan's), Learning card function, stats tab button and label, "Whole <country>" button text, `sw.js` (files and a `CACHE` bump), `tools/make_preview.py` (data files and the flag folder).
4. **Tiny parts:** adaptive circles for small parts, island ovals for islands the plan keeps; no numbered bubbles.
5. **Layers and timeline:** as the plan says (Indigenous layers like `tribal-<code>.json` with the source credited on the map; timelines like Australia's colony timeline or Russia's pieces).
6. **Tests (headless Chrome bench, all must pass before the build counts as done):**
   - every part opens its own card when its anchor is tapped at whole-map zoom, on a phone-sized window (390×844)
   - names: each part's other names and spellings are accepted; `notTypo` pairs are refused; capitals games and flag (or coat of arms) games leave out the parts the plan says
   - every capital has a dot position; every flag or coat of arms loads; the card shows its facts in light and dark themes
   - zoomed in, the detail level loads and taps still land on the right part
   - the layer loads and names an area on tap; the timeline's captions, arrows and taps work
   - the US timeline, Russia's timeline and the world map still work; no script errors
   - screenshots checked by eye: the map, the grey reaching the edges, the circles, the card
7. **Finish:** add the build to [PLAN.md](../PLAN.md) and mark the plan built; publish the preview; commit. Push only as the job queue or the user allows.

### Mexico (built overnight 2026-11-18, timeline not yet; see OVERNIGHT_REVIEW.md)

- 32 parts (31 states and Mexico City); the Revillagigedo Islands left off.
- Data in `tools/downloads/mx/`: `states.json` (capitals, largest cities, areas, **2020 census**, adding up to 126,014,024), Wikipedia articles (`wiki/states/` English, `wiki/states_local/` Spanish, `infobox.json`, `infobox_local.json`), `flags/`, `coats/` (Colima's coat of arms failed on a rate limit: fetch it again), `coast_f.geojson`, `indigenous/` (ITER census, geoBoundaries municipalities, top languages by state).
- **Games 5 and 6 are coat-of-arms games** ("Find by coat of arms", "Name the coats of arms"). Mexico City has no capital: it sits out the capitals games.
- Names: typing "Mexico" counts for the State of Mexico (so Mexico City needs "Mexico City", "CDMX", "Ciudad de México" or "DF"); Baja California and Baja California Sur never count for each other.
- Tiny parts: circles for Mexico City, Tlaxcala, Morelos (and Aguascalientes, Colima if needed).
- Indigenous layer: municipalities shaded by the share who speak an Indigenous language; a tap names the municipality, its share, and its state's main languages. Credit INEGI and geoBoundaries.
- Timeline: expansion and decline (1821 to 1974), built from pieces like Russia's.
- Projection: Lambert conformal conic, parallels 17.5°N and 29.5°N, centre 102°W.

### Brazil (built overnight 2026-11-18; see OVERNIGHT_REVIEW.md)

- 27 parts (26 states and the Federal District).
- Data in `tools/downloads/br/`: `states.json` (capitals, areas, years), `census2022.json` (IBGE, adding up to 203,080,756), Wikipedia articles (`wiki/states/` English, `wiki/states_local/` Portuguese, `infobox.json` with demonyms in `infobox_local.json`), `flags/` (all 27), `coast_f.geojson`, `funai/tis_poligonais.zip` (665 Indigenous territories).
- Tiny parts: a circle for the Federal District; **Fernando de Noronha and Trindade as tappable island ovals** (parts of Pernambuco and Espírito Santo).
- Names: Pará, Paraná and Paraíba never count for each other; "Mato Grosso" counts only for Mato Grosso; two-letter codes (RJ, SP, MG…) accepted.
- Indigenous lands layer: FUNAI's territories, named with their people on tap; credit FUNAI on the map; simplify the big Amazon shapes.
- Timeline: how today's states formed (1534 captaincies to 1988), reusing the US/Australia timeline code.
- Projection: Albers equal-area conic, parallels about 2°S and 22°S, centre 54°W.

### Germany, Japan, France, Italy, Spain, Nigeria, Argentina (decided 2026-11-17; Germany, Japan, France, Italy, Spain, Nigeria and Argentina built overnight 2026-11-18: all seven)

Each follows the checklist; their plan files (step 2) record these decisions and add the card facts. Every one has the six games (Find and Name for the parts, capitals, and flags or their stand-in), a ~18-fact card, Focus on, a stats tab, and the high-resolution coast.

- **Germany:** 16 states, all with official flags (flag games). Circles for Berlin and Bremen (Bremen's two pieces). No layer. **Timeline: to discuss in the morning** (see "Morning agenda").
- **Japan:** 47 prefectures, the 9 regions as a filter; every prefecture flag is official (flag games). Kanji names on the cards: **download a Japanese font** (Noto Sans JP) and subset it (`tools/build_fonts.py`). Island ovals for Okinawa and the outlying islands. The southern Kurils follow the disputed-areas rule. **Timeline: to discuss in the morning.**
- **France:** the **18 regions only** (no departments). **The overseas regions are left off** (too far away): the map is metropolitan France with Corsica, so **13 parts**. **No flag games.** Timeline idea (Napoleonic) **shelved for now**.
- **Italy:** 20 regions, all with flags (flag games); the **107 provinces as a second set: to confirm** (morning agenda). **Vatican City and San Marino as circles in their flag colours: Vatican yellow, San Marino blue**, each with its own **"Focus on Vatican City" / "Focus on San Marino"** button, which needs **very high-resolution data, possibly of buildings and streets** (a separate job: see "Vatican City and San Marino" below). Timeline **shelved for now**.
- **Spain:** **two levels as two sets**: 17 communities plus Ceuta and Melilla (circles), and the 50 provinces. Flags for the communities (flag games). **The Canary Islands in an inset.** **A languages layer** (Learning mode: where Catalan, Basque, Galician and the others are spoken; find an open source and credit it). **Timeline: to discuss in the morning.**
- **Nigeria:** 36 states and the FCT; the 2006 census (the last full count; say so on the card). State flags are mostly unofficial. **Seal games: shelved (2026-11-17).** The idea was "Find by seal" and "Name the seals" (like Mexico's coats of arms), but many state seals on Wikipedia aren't on Commons, which usually means they're **not freely licensed** (shown on Wikipedia as fair use), so they can't go in the app. Six were downloaded before the download was paused (Abia, Akwa Ibom, Bauchi, Benue, Borno, Edo; their licences still unchecked). **Build Nigeria without games 5 and 6 for now** (like France), and come back to it: check each seal's licence on Commons and decide whether enough states have a free one. **Timeline: to discuss in the morning** (the state splits 1967–1996 is the idea).
- **Argentina:** 23 provinces and the City of Buenos Aires (circle), all with flags (flag games). **No Falklands** (left off the map), no Antarctic claim. **Timeline: to discuss in the morning.**

### Learning card facts (chosen 2026-11-17)

Every card also has the name, kind, capital, population (latest census), area and rank, and the flag (or seal) where there is one. Leave out any fact that isn't found rather than guess.

- **Germany (17):** name in German; demonym; dialect; famous dish; beer or wine; biggest festival or tradition; football: biggest club; main river; highest point; coast (North Sea, Baltic, or landlocked); natural wonder or national park; former kingdom or duchy; East or West Germany before 1990; famous castle or landmark; UNESCO World Heritage; known for; famous company from there. (Borders: not chosen.)
- **Japan (18):** name in kanji with its reading; region; famous food or meibutsu; famous festival; traditional craft; dialect; highest point; main river or lake; natural wonder; hot springs; prefectural flower, tree and bird; old province name; famous castle or temple; UNESCO World Heritage; name meaning; known for; mascot; largest city if it isn't the capital.
- **France (18):** name in French; demonym; regional language; famous dish; famous cheese; famous wine or drink; biggest festival; highest point; main river; coast; natural wonder or national park; historic provinces it covers; formed (2016 merger, or unchanged); famous landmark; UNESCO World Heritage; famous person from there; known for; largest city if it isn't the capital.
- **Italy (18):** name in Italian; demonym; dialect or minority language; famous dish; protected food (DOP/IGP); famous wine; biggest festival; special-statute region or not; highest point; main river or lake; volcano or natural wonder; coast or islands; before unification (which state); famous landmark; UNESCO World Heritage; famous person from there; known for; largest city if it isn't the capital.
- **Spain (18, communities and the two cities):** name in Spanish and in its own language; co-official language; demonym; famous dish; drink; biggest fiesta; music or dance; football: biggest club; highest point; main river; coast; natural wonder or national park; old kingdom; Moorish heritage; famous landmark; UNESCO World Heritage; known for; largest city if it isn't the capital. **The 50 provinces** get a shorter card: name, capital, population, community, a landmark.
- **Nigeria (17):** nickname (the number-plate slogan); main ethnic groups; main languages; main religions; famous dish; biggest festival; traditional ruler; main river; climate or vegetation; highest point; natural wonder or park; created (year) and from which state; old kingdom or empire; UNESCO World Heritage; known for; largest city if it isn't the capital; famous person from there. (Geopolitical zone: not chosen.)
- **Argentina (18):** demonym; region; famous food; drink; music or dance; biggest festival; Indigenous peoples; football: biggest club; highest point; main river or lake; natural wonder or national park; climate; famous animal; became a province (1853 founder or former national territory); UNESCO World Heritage; famous person from there; known for; largest city if it isn't the capital.

### Vatican City and San Marino (a separate job, later)

Their own "Focus on" maps from the Italy map. They're tiny (Vatican City is about 0.5 km²), so the map would show buildings and streets, not regions: St Peter's Basilica, the Sistine Chapel, the gardens; San Marino's nine castelli (municipalities) and Mount Titano's three towers. Needs very high-resolution data: OpenStreetMap buildings (ODbL: share-alike, so check how that fits) or official sources. Plan it separately before building.
