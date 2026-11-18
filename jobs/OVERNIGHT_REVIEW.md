# Overnight review (night of 2026-11-18)

What the overnight run did, for the user to check in the morning. Nothing is committed or pushed: everything is in the working tree. The preview is up to date: https://claude.ai/artifact/FozfGxc5xd1StWG7MZaAnf

**How to read it:** each item has what was built, the tests and their results, **decisions to check** (judgement calls, with the alternative), **waiting for data** (parts ready to drop in), and **problems**. The morning agenda is in [README.md](README.md).

## Summary

**All ten items are done.** Seven plans were written, and nine countries were built, tested and put on the preview: Mexico, Brazil, Germany, Japan, France, Italy, Spain (two sets), Nigeria and Argentina. Nothing is committed or pushed.

**Final check:** every country map (US, Canada, Russia, Australia and the nine new ones; 14 in all) loads in headless Chrome, and every part taps right at its centre.

**Most worth a look:**
1. **Population sources differ from the plans in places, wherever the downloads had something newer or only something else:**
   - Germany: 31 Dec 2024 (on the 2022 census basis).
   - Italy: 1 Jan 2026.
   - Spain: 1 Jan 2025.
   - France: the 2019 legal population.
   - Nigeria: 2019 estimates, not the 2006 census.
   - Japan, Mexico, Brazil and Argentina: their censuses.
2. **Insets:**
   - Japan's Okinawa stays in place (no inset).
   - Spain's Canaries are a moved copy inside a frame. The app has no real inset maps yet.
3. **Natural Earth fix:** the Amami islands were in Okinawa; the build moves them back to Kagoshima.
4. **Card facts:** I wrote them from general knowledge for every country, leaving out what I wasn't sure of. Worth a skim.
5. **Preview limits (the preview only, the real app is unchanged):**
   - Shrunken flags, so the page fits its 16 MB cap.
   - No finest relief level, to stay under 512 files.
   - Merged coast tiles.

   Separately, Mexico's coats of arms are 4.3 MB in the real app; worth shrinking.
6. **Still to do:**
   - Mexico's timeline.
   - Spain's languages layer (no data).
   - Italy's provinces (to confirm).
   - A Learning-mode set button for Spain.
   - Japan's far-south detail gap.
   - The Vatican City and San Marino maps.
   - Every timeline on the morning agenda.

**New shared code:**
- tools/detail.py: the detail level, and `land_poly`/`name` for Spain.
- js/mapview.js: detail tiles, island ovals for a part's far islands, coloured circles (`ringColour`).
- app.js: one card function per country.
- tools/build_fonts.py: a `japanese` option.
- css/app.css: a wrapping button grid.
- tools/make_preview.py: the preview limits above.

## Done before the run (asked for at bedtime, 2026-11-18)

- **Clip captions** fixed at the height of the world map's Borders button (they no longer follow the button on the US map); both clips re-recorded.
- **Game / Region boxes:** a tap now opens one and closes the other in the same frame. Before, the browser toggled them one after the other, drawing a frame with both open (the Region box flashed at the bottom). Tested: never both open.
- **Magnifying glass:** the Learning map is now opened behind the cover with the lens closed, and the glass pops in only once it's drawn, so the globe no longer jumps inside the lens.
- **Help ("?")**: a short "How to play" pane (Games, Learning mode, The map, Countries, Options and stats), opened in place of the games like More games, with "‹ Back". Decision to check: the wording, and whether it should open on first launch.

## New remote commits seen (not merged)

- `c94f576` Add jobs/overnight_v2.md: downloads and builds for Austria, Netherlands, Poland, Czechia, Belgium
- `261c88c` overnight_v2: start only when the user says so

Not pulled (the rules say no merging overnight); it says to start only when you say so anyway.

## 1. Plans

**Done.** Seven plan files, written from [build_countries.md](build_countries.md) (the decisions and card facts from 2026-11-17), in the style of the existing plans: [Germany_plan.md](../Germany_plan.md), [Japan_plan.md](../Japan_plan.md), [France_plan.md](../France_plan.md), [Italy_plan.md](../Italy_plan.md), [Spain_plan.md](../Spain_plan.md), [Nigeria_plan.md](../Nigeria_plan.md), [Argentina_plan.md](../Argentina_plan.md). Each has what's on the map, wiring, data build, capitals, names matching, tiny parts, flags, the card facts, layers and timeline, build order and open questions.

**Decisions to check** (not in the decisions you gave; I chose them):
- **Projections:** Germany Lambert conformal conic (48.67°N/53.67°N, 10.5°E); Japan Albers (30°N/44°N, 137°E); France Lambert-93; Italy Transverse Mercator (12.5°E); Spain Lambert conformal conic (36°N/43°N, 3.5°W); Nigeria Lambert conformal conic (6°N/12°N, 8°E); Argentina Transverse Mercator (64°W).
- **Japan: Okinawa and the far southwest islands in an inset** (like Spain's Canaries), proposed in the plan as an open question; the build will use an inset unless you say otherwise.
- **Argentina:** typing "Buenos Aires" counts for the province; the city needs "City of Buenos Aires", "CABA", "Ciudad de Buenos Aires" or "Capital Federal".
- **Nigeria:** typing "Lagos" also counts for Lagos State's capital (Ikeja), since it's the city people know.
- **Germany:** "Saxony" counts only for Saxony (not Saxony-Anhalt or Lower Saxony); the city-states are their own capitals.
- **Spain:** the Canaries share their capital (Santa Cruz de Tenerife and Las Palmas both count).
- **Italy:** until their own maps exist, the Vatican City and San Marino circles open a short card, and their Focus buttons wait.

## 2. Mexico

**Built** (except the timeline: see below). In the preview: Countries → North America → Mexico, or "Focus on Mexico" from the globe.

- **Data:** [tools/build_mx.py](../tools/build_mx.py) → `data/mx-states.json`, `data/mx-parts.json`, coats of arms in `data/flags/mx/`. 32 parts; the Revillagigedo Islands left off; **2020 census adds up to 126,014,024 exactly**; all 31 capitals found.
- **Detail level (new, used by every later build):** [tools/detail.py](../tools/detail.py) fits the parts to the GSHHG full-resolution shoreline and cuts **tiles** (`data/mx-detail/`, 56 tiles, 2.8 MB, fetched only when zoomed in and cached offline as they're viewed). In the app ([js/mapview.js](../js/mapview.js), `detailReady`): zoomed in past the light map's detail (220 px per degree), once all the tiles on screen have loaded, they're drawn instead of the light shapes, and taps use them. Until then (or if the view reaches beyond the tiles' coverage) the light map shows.
- **Facts:** [tools/mx_facts.py](../tools/mx_facts.py) (all 18 chosen facts; the Indigenous languages and their share come from the INEGI census, the largest city and the year it became a state from the downloads).
- **Coat-of-arms games:** games 5 and 6 read "Find by coat of arms" / "Name the coats of arms", in the menu, the stats tab and the prompts. 31 coats of arms (Colima's is missing: it sits out those games).
- **Indigenous languages layer:** `data/tribal-mx.json`: 926 municipalities where 5% or more speak an Indigenous language, in four shades (5–15%, 15–40%, 40–70%, 70%+); a tap names it ("Chamula, Chiapas · 98% speak an Indigenous language (in Chiapas: Tseltal, Tsotsil, Ch'ol)"); credit on the map. The layer code now supports shaded bands.
- **Tests (all passed, phone size):** all 32 parts tap right at whole-map zoom; capitals games 31 (Mexico City sits out), coat games 31 (Colima sits out); names ("Mexico" → State of Mexico but not Mexico City; "CDMX"; "Michoacan" without the accent; "Baja California" doesn't count for Baja California Sur; the long official names); zoomed in, the detail tiles load and taps land right (Oaxaca); the layer loads with its four bands and names a municipality; the US and Russia timelines still work; no errors. Screenshots checked: the grey reaches the screen edges, the circles, the detailed coast at Los Cabos.

**Decisions to check:**
- Circles for Mexico City, Tlaxcala, Morelos, **Aguascalientes and Colima** (the plan said "probably" for the last two).
- The **detail threshold** (220 px per degree, about when the light map's 1 km simplification would show) and tile size (3°).
- The Indigenous layer leaves out municipalities under 5%, and **33 of 2,457 municipalities didn't match the census by name** (they're left off the layer).
- Mexico City's card says "City: the capital of Mexico itself" where other cards say "Capital".
- The card shows the share of people who speak an Indigenous language next to the state's top languages.

**Not done (for the morning):**
- **Mexico's timeline** (expansion and decline, 1821–1974, decided in its plan): left out to keep moving through the queue; it's a Russia-sized job (pieces for Central America, Texas, the land lost in 1848, the Gadsden Purchase, and the states forming).

**Waiting for data:** Colima's coat of arms.

## 3. Brazil

**Built:** 26 states and the Federal District (Natural Earth 1:10m), on an Albers equal-area map centred on 54°W.
- **Games:** all the usual games, plus the flag game with all 27 flags.
- **Cards:** facts from tools/br_facts.py.
- **Data:** 2022 census (IBGE).
- **Indigenous lands layer:** 665 FUNAI territories.
- **Detail level:** 153 tiles at 3°, fitted to the GSHHG full-resolution shore.
- **Timeline:** built, because it reuses the US and Australia code. It runs from the first captaincies in 1534 to the 1988 constitution, with 20 captioned stops.
- **Files:** tools/build_br.py, tools/br_facts.py, data/br-*.json, data/br-detail/, data/tribal-br.json, data/flags/br/.

**Tested in headless Chrome:**
- The population adds up to exactly 203,080,756.
- Every state taps correctly, including the two island ovals: Fernando de Noronha opens Pernambuco and Trindade opens Espírito Santo.
- The Federal District gets a tappable circle.
- The detail tiles draw and tap correctly around Rio.
- The layer and the timeline work.
- Australia, Mexico and the US timeline still work, with no console errors.

**Decisions to check:**
- **Map window:** 84°W–24°W, 42°S–13°N. It's wide enough to show the far islands and fill a tall phone screen. French Guiana appears as grey context.
- **Typed answers:** the two-letter state codes count, for example "SP" or "RJ". "Rio" counts for Rio de Janeiro, and "Brasília" counts for the Federal District.
- **Typo matching is off between Pará, Paraná and Paraíba**, so typing one never counts as a near-miss of another.
- **Island ovals:** 0.12° radius for Fernando de Noronha and 0.1° for Trindade.
- **Timeline captions are my own wording** (in the app as BR_TL), taken from the dates in Brazil_plan.md.
- Brazil has no "bordering countries" pairs for the borders game yet. Its cards list the neighbouring countries.

**Fixed along the way:**
- **Island ovals crashed on fitted maps:** they used the world map's projection. Fixed.
- **Flags and the DF circle went missing after a US visit:** the timeline year stayed at the US's 1959, which hid 7 flags and the DF circle. Each country now starts at its own last year.

**Preview change:** the preview can hold only 512 files. tools/make_preview.py now merges the detail tiles into 9° blocks for the preview only: Brazil has 23 files and Mexico 12. The repo keeps the 3° tiles.

## 4. Germany

**Built:** the 16 states on a Lambert conformal conic map (as the plan says).
- **Games:** all six games, including the flag games with all 16 flags.
- **Cards:** 17 facts each (tools/de_facts.py).
- **Detail level:** 19 tiles at 3°.
- **Circles:** Berlin and Bremen.
- **Files:** tools/build_de.py, tools/de_facts.py, tools/downloads/de/states.json, data/de-*.json, data/de-detail/, data/flags/de/.

**Tested in headless Chrome:**
- Every state taps correctly at its centre.
- The Berlin and Bremen circles show.
- The card fills in.
- The detail tiles draw and tap correctly at Hamburg and on Rügen (the Bodden lagoons show nicely).

**Decisions to check:**
- **Populations are from 31 December 2024, not the 2022 census itself.** They're Destatis's figures on the 2022 census basis and add up to 83,577,140. The downloaded "2022 census" article turned out to be the 2011 one, so I fetched the German Wikipedia table instead. Areas come from each state's English Wikipedia infobox, rounded.
- **"State since"** is the year today's state was formed: 1946 or 1947 for most western states, Saarland 1957, Baden-Württemberg 1952, the eastern states and Berlin 1990.
- **I wrote the card facts from general knowledge.** They're worth a skim: the dialects, dishes and "famous company" picks are my choices.
- **Typed answers:** German names count (Bayern, NRW, Thüringen, München, Hannover…). Typo matching is off between Saxony, Lower Saxony and Saxony-Anhalt.
- **Bavaria's flag** is the one downloaded from Wikidata: the striped flag, not the lozenge one the plan mentions.
- Hamburg and Saarland get no circle (as planned).

**Not done:** the timeline (morning agenda).

## 5. Japan

**Built:** the 47 prefectures on an Albers equal-area map (30°N/44°N, centred on 137°E).
- **Games:** all six games, including the flag games with all 47 flags.
- **Region filter:** the 9 regions as a filter on Japan's game page ("All 47", Hokkaido, Tōhoku … Okinawa). Each region game crops to that region.
- **Cards:** about 18 facts each, with the kanji name in a new font subset, fonts/gq-japanese.woff (75 characters, 15 KB, from Noto Sans JP).
- **Detail level:** 52 tiles at 3°.
- **Circles:** Osaka, Kagawa and Tokyo.
- **Island ovals (11):** Okinawa's main island, Miyako, Yaeyama, Daitō and Kerama; Tokyo's Izu and Ogasawara islands; Kagoshima's Amami, Tokunoshima/Okinoerabu and Tanegashima/Yakushima; Shimane's Oki islands.
- **Files:** tools/build_jp.py, tools/jp_facts.py, tools/downloads/jp/states.json, data/jp-*.json, data/jp-detail/, data/flags/jp/, fonts/gq-japanese.woff. tools/build_fonts.py gained a `japanese` option, and css/app.css gained `.native-ja` and a wrapping button grid (`.seg.wrap`).

**Tested in headless Chrome:**
- All 47 prefectures tap correctly at their centres, and so do all 11 island ovals.
- The detail tiles draw and tap correctly at Kyoto, among the Seto Inland Sea islands and at Naha.
- The Kansai game crops to Kansai.
- The kanji font loads on the card.
- The population is exactly 126,146,099 (2020 census).

**Decisions to check:**
- **Okinawa is in place, not in an inset.** The app can't draw insets yet (a second map projection would be needed). A tall phone screen fits the whole arc, and the far islands get ovals. An inset can be added later if you want it.
- **Natural Earth's error fixed:** it puts the Amami islands (Amami Ōshima to Yoron) in Okinawa. The build moves them back to Kagoshima.
- **Left off the map:** Minamitorishima and Okinotorishima (Tokyo's far Pacific islands) are outside the map window.
- **The southern Kurils** stay in Russia's grey, as Natural Earth has them. They don't have the dotted disputed line yet.
- **Card facts:** I wrote them from general knowledge and left out anything I wasn't sure of. A few highest points are missing (Akita, Miyagi, Niigata, Kōchi). The flower, tree and bird come from each prefecture's Wikipedia infobox.
- **Typed answers:** macrons are optional (Hyogo, Hyougo), and suffixes are optional ("Aichi Prefecture", "Aichi-ken", "Osaka-fu", "Tokyo-to"). Shinjuku counts for Tokyo's capital.
- **Capital pins added by hand:** Saitama, Chiba, Yamaguchi and Saga (the place list had no match for them).

**Not done:** the timeline (morning agenda).

## 6. France

**Built:** the 13 metropolitan regions on a Lambert-93 conformal conic map, dissolved from Natural Earth's 96 departments. The overseas regions are left off (as decided).
- **Games:** no flag games (`noFlags`, like India). The card hides the flag.
- **Cards:** about 18 facts each (tools/fr_facts.py).
- **Detail level:** 30 tiles at 3°.
- **Files:** tools/build_fr.py, tools/fr_facts.py, data/fr-*.json, data/fr-detail/.

**Tested in headless Chrome:**
- All 13 regions tap correctly at their centres.
- The card shows with no flag.
- The detail tiles draw and tap correctly at Paris, at Mont-Saint-Michel (Normandy) and in Corsica.

**Decisions to check:**
- **Populations are INSEE's 2019 legal populations**, summed from the department list in the downloads. They add up to 65,096,768 for metropolitan France, which I believe is INSEE's published 2019 total. The downloads had no total to check against. Areas are summed from the same list.
- **Bourgogne-Franche-Comté's capital is Dijon** (the prefecture, as the plan says). Besançon, where the regional council sits, also counts.
- **Typed answers:** French and English names count (Bretagne, Normandie, Corse, PACA, Provence, Occitania, New Aquitaine…). So do some old region names: "Alsace" for Grand Est, "Auvergne", "Burgundy", "Nord-Pas-de-Calais". Lyons and Marseilles count for the capitals.
- **I wrote the card facts from general knowledge.** I left out Brittany's cheese and Centre-Val de Loire's highest point because I wasn't sure of them.

**Preview changes:** the preview hit its 512-file limit again. It now leaves out the finest relief level (about 300 tiles), so relief is a little softer when zoomed right in. It also inlines the flags shrunk to 320 px wide, which takes the page from 13 MB to 4.5 MB (16 MB is the cap). The real app is unchanged.

**For the morning:** Mexico's coats of arms are 4.3 MB in data/flags/mx/ (about 140 KB each, 31 of them). That's heavy for a phone download, so they're worth shrinking in the real app too.

## 7. Italy

**Built:** the 20 regions on a transverse Mercator map (12.5°E), dissolved from Natural Earth's 110 provinces.
- **Games:** all six games, including the flag games with all 20 flags.
- **Cards:** about 18 facts each (tools/it_facts.py).
- **Detail level:** 22 tiles at 3°.
- **Vatican City and San Marino:** coloured circles, yellow and blue as decided. They show in Learning mode only and are left out of the games (they're separate countries). Tapping one opens a short card with its flag, population, area and a line about it; "Its own map" says "Coming soon".
- **Files:** tools/build_it.py, tools/it_facts.py, data/it-*.json, data/it-detail/, data/flags/it/. js/mapview.js now fills a circle when a part has `info.ringColour`.

**Tested in headless Chrome:**
- All 20 regions and both enclaves tap correctly.
- A Find game asks about exactly 20 parts.
- Both cards fill in.
- The detail tiles draw and tap correctly at Rome (the Vatican circle shows there), Venice and Naples.
- The population is exactly 58,942,828 (ISTAT's figure for 1 January 2026, from the downloaded "Regions of Italy" table).

**Decisions to check:**
- **Population date:** ISTAT's 1 January 2026 figures, not the 2021 census. They're the newest, and they add up exactly.
- **Focus on Vatican City / Focus on San Marino buttons are not built.** The plan says they wait for those countries' own maps, so the card says "Coming soon" instead.
- **Trentino-Alto Adige is shown as "Trentino-South Tyrol"**, with its official name as the name in Italian. Every form of the name counts when typed.
- **Typed answers:** Italian names count (Lombardia, Toscana, Puglia, Sardegna…), and so do Italian capital names (Torino, Milano, Firenze, Napoli, Roma…).
- **I wrote the card facts from general knowledge.** I left out Basilicata's highest point. Several highest points sit on a region's border, so I gave each region's own top.

**Not done:** the provinces as a second set (still to confirm).

## 8. Spain

**Built:** two sets on a Lambert conformal conic map (36°N/43°N, 3.5°W).
- **Communities:** the 17 communities and the 2 cities, with flags (19).
- **Provinces:** the 50 provinces and the 2 cities, with no flag games and a short card (capital, population, community, area, a landmark).
- **Set switch:** Spain's game page has a Communities/Provinces switch, and the game names follow it. The stats tab has "Spain" and "Spain (provinces)".
- **Circles:** Ceuta and Melilla.
- **The Canaries are in an inset** at the lower left, inside a frame. The build moves their shapes, capitals and detail level 5.5° east and 6.5° north. The Canary Islands card says they're really about 1,000 km south-west, off Africa.
- **Detail level:** each set has its own (25 tiles each). The Canaries' coast is in the inset too.
- **Files:** tools/build_es.py, tools/es_facts.py, data/es-*.json, data/esp-*.json, data/es-detail/, data/esp-detail/, data/flags/es/. tools/detail.py's build_detail now accepts `land_poly` and `name`. tools/downloads/es/wiki/lists/ has a newly fetched "Ranked lists of Spanish provinces" (population).

**Tested in headless Chrome:**
- All 19 communities and all 52 provinces tap correctly at their centres.
- The Ceuta and Melilla circles show.
- Both cards fill in.
- The detail tiles draw and tap correctly at Tenerife (in the inset), Mallorca and Ceuta.
- The set switch changes the game names, and Provinces hides the flag games.

**Decisions to check:**
- **Population:** INE's annual census for 1 January 2025, by province, with the communities summed from them. Both add up to 49,128,297. That isn't checked against an independent national total (the downloads had none).
- **The inset is a moved copy, not a second map.** The app has no inset support, and moving the islands made the inset work everywhere at once: taps, games, detail and capitals. The catch: anything that uses real coordinates for the Canaries (none yet) would need to know they're moved.
- **Typed answers:** Spanish and co-official names count (Andalucía, Catalunya, Euskadi, Nafarroa, Illes Balears, Comunitat Valenciana…). So do capital variants (Sevilla, Saragossa, Donostia, Vitoria, Iruña, Palma de Mallorca, La Coruña…). The Canaries' two capitals both count.
- **The Learning mode set:** Learning mode opens the communities. There's no button there yet to switch to the provinces (the UK has a set button for this), so the provinces are in the games only for now. Adding the same button for Spain is a small job.
- **I wrote the card facts from general knowledge.**

**Not done:**
- The languages layer (waiting for data).
- The timeline (morning agenda).

## 9. Nigeria

**Built:** the 36 states and the FCT on a Lambert conformal conic map (6°N/12°N, 8°E).
- **Games:** no flag games (`noFlags`, as decided). The card hides the flag.
- **Cards:** the number-plate nickname (from the downloaded list), geopolitical zone and largest city, plus about 15 facts (tools/ng_facts.py).
- **Detail level:** 19 tiles.
- **Circle:** Lagos gets an adaptive circle, which only shows when the state is small on screen.
- **Files:** tools/build_ng.py, tools/ng_facts.py, data/ng-*.json, data/ng-detail/.

**Tested in headless Chrome:**
- All 37 parts tap correctly at their centres.
- The card fills in.
- The detail tiles draw and tap correctly at Lagos and in the Niger Delta (Bayelsa).

**Decisions to check:**
- **Population is the 2019 estimates, not the 2006 census the plan named.** The downloaded "States of Nigeria" table has the National Bureau of Statistics' 2019 figures (total 199,839,058). The downloads have no state-by-state 2006 census, so the card says "2019 estimate".
- **No typo forgiveness between similar names:** Edo, Imo, Ondo and Oyo can't be mistaken for each other; nor can Ogun and Osun, or Gombe and Yobe. I worked these pairs out at build time, using names up to 2 letters apart.
- **Typed answers:** "State" is optional. "FCT" and "Abuja" count for the Federal Capital Territory. "Lagos" counts for Lagos State's capital (Ikeja), "Benin" for Benin City and "PH" for Port Harcourt.
- **Detail level fix:** the downloaded shoreline stops at 4.2°N. A view of the delta's coast reaches further south than that, so the detail level didn't switch on. The detail area now runs to 3°N (open sea). **Japan may have the same gap** around its southernmost islands (Yaeyama, about 24.3°N); worth a look.
- **I wrote the card facts from general knowledge**, leaving out what I wasn't sure of: several highest points and traditional rulers are missing. Delta State has no nickname in the downloaded list.

**Not done:** the timeline (morning agenda); the seal games (shelved).

## 10. Argentina

**Built:** the 23 provinces and the City of Buenos Aires on a transverse Mercator map (64°W).
- **Games:** all six games, including the flag games with all 24 flags.
- **Cards:** about 18 facts each (tools/ar_facts.py).
- **Detail level:** 67 tiles. Patagonia's fjords and Tierra del Fuego make up most of it.
- **Circle:** the City of Buenos Aires.
- **No Falklands, South Georgia or Antarctica**, not even as grey context, as decided.
- **Files:** tools/build_ar.py, tools/ar_facts.py, data/ar-*.json, data/ar-detail/, data/flags/ar/.

**Tested in headless Chrome:**
- All 24 parts tap correctly.
- The card fills in.
- The detail tiles draw and tap correctly at Ushuaia, Buenos Aires and Península Valdés.
- Then every country map was loaded in turn, and every part taps right.

**Decisions to check:**
- **"Buenos Aires" counts for the province.** The city needs "City of Buenos Aires", "CABA", "Ciudad de Buenos Aires" or "Capital Federal", as the plan proposed.
- **Short capital names count:** Catamarca, Jujuy, Tucumán, Santiago.
- **Population:** the 2022 census from the downloaded table, 45,892,204. INDEC's headline total is a little higher (about 46.0 million, which also counts people outside households), so this may be the household count.
- **I wrote the card facts from general knowledge.**

**Not done:** the timeline (morning agenda).

## Waiting for data (all items)

- Mexico: Colima's coat of arms.
- Germany: the 2022 census figures themselves (31 Dec 2024 figures used).
- Every country: the official census totals (checked against Wikipedia's census tables instead).
- Spain: the languages layer (no open data source yet).
