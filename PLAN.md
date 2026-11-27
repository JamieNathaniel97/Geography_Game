# World Geography Quiz App – Plan

A Sporcle-style Android app for learning every country's location and capital. This document is the brief for building it.

## Goal

Help the user learn all ~197 countries (UN members plus commonly included states such as Taiwan, Kosovo, Vatican City and Palestine) and their capitals through repeated, map-based quizzes on an Android phone.

## Platform and tech

- Target: Android (phone-first, portrait and landscape).
- Stack (decided): a web app using d3-geo for the 3D globe (orthographic projection) and the flat maps. It is installed as an offline PWA from GitHub Pages, the same way as the OOW oral trainer. It can be wrapped as an APK with Capacitor later if needed.
- Map: render country shapes from an open GeoJSON/TopoJSON world dataset (for example Natural Earth, 1:50m or 1:110m) as tappable SVG paths, so no network or map API key is needed.
- Fully offline. All data bundled with the app.
- Pinch-to-zoom and pan are essential, since many countries are tiny.

## Build 1: quiz modes (build these first)

### 1. Find the country (tap on map)

The app shows a country name and the user taps where it is on the map.

**Scope options**

- **Whole world:** any country in the world can come up. Shown on a 3D globe the user can spin and tap, with a toggle to switch to a flat world map instead.
- **Single continent:** the user picks a continent; the map zooms to that continent (flat map) and only countries from that region come up.

**Map display toggles** (available in-game and in settings)

- **Borders:** clear country borders, on or off.
- **Terrain:** shaded relief showing mountains and other physical features, on or off.
- **Satellite view:** shelved for now and may come back later. It can't be fully offline, because sharp imagery for tiny countries would take gigabytes. If it returns, it will be online-only. Wherever later sections say "satellite toggle", read it as shelved.

**Jump to:** quick buttons that move the map to Europe, Asia, Africa, North America, the Caribbean, South America or Oceania (plus back to the whole world). They are always visible in a bar at the very bottom of the quiz screen, in two rows of four, not hidden in settings.

**Answering**

- One tap per country.
- Correct: the country fills green (or another clear colour, to be tested).
- Wrong: the correct country is highlighted in red, and the country the user tapped flashes yellow once to confirm the tap registered. Then move on.
- Tapping the sea, or a country already answered correctly, does nothing.

**Tiny countries** (settled with the prototype in `prototype/`)

- **Deep zoom** is the main tool: the map zooms far enough to tap even Vatican City directly.
- **Island nations** get one dashed oval around all their islands, including the sea between them, squashed and tilted to follow island chains. Tapping anywhere inside counts as tapping the country, and the whole oval turns green or red. Kiribati is one sideways figure-8 shape (Gilbert Islands to the west, a larger lobe for the Phoenix and Line Islands to the east) that stays clear of Tuvalu and Nauru. The list: Fiji, Kiribati, Marshall Islands, Micronesia, Nauru, Palau, Samoa, Solomon Islands, Tonga, Tuvalu, Vanuatu, Antigua and Barbuda, Bahamas, Barbados, Dominica, Grenada, St Kitts and Nevis, St Lucia, St Vincent and the Grenadines, Trinidad and Tobago, Cape Verde, São Tomé and Príncipe, Comoros, Mauritius, Seychelles, Maldives, Malta, Singapore, Bahrain.
- **Minimum shape size** on screen is 8 px, except Samoa, Nauru, Cape Verde, Comoros, Mauritius and Seychelles (16 px), São Tomé and Príncipe (22 px) and the Maldives (14 px).
- **Small land countries** get a small 8 px ring that only shows the country is there. It can't be tapped and disappears once the country's own shape is visible. The list: Vatican City, San Marino, Monaco, Liechtenstein, Andorra, Qatar, Brunei, Timor-Leste.
- **Lesser Antilles** (Antigua and Barbuda, St Kitts and Nevis, Dominica, St Lucia, St Vincent and the Grenadines, Grenada, Barbados, Trinidad and Tobago) show as one numbered bubble when zoomed out. Tapping it zooms in, and it splits into the individual ovals early in the zoom.
- **Magnifier:** a button, then a tap anywhere, opens a zoomed-in inset there to tap a country in.
- The overseas parts of France and the Netherlands (Guadeloupe, Martinique, French Guiana, Réunion, Mayotte, Bonaire and so on), plus Tokelau and Ashmore Reef, are territories: grey and untappable.

### 2. Name the countries (fill in the map)

The goal is to fill in the whole map by naming every country, in any order the user likes.

**How it plays**

- The user taps any country on the map, and a text box pops up.
- The user types the country's name. There is no submit button and no wrong answer: the box simply does not react until the correct name is typed.
- As soon as the correct name (or a close enough match) is typed, the country turns green and the box closes, Sporcle-style.
- Matching is forgiving of case, accents, minor typos and common alternative names (for example "Ivory Coast" / "Côte d'Ivoire", "Czechia" / "Czech Republic", "USA" / "United States").
- A counter shows progress, for example "45 / 197".
- Decided 2026-11-15: the text box sits in the top bar, and the tapped country is highlighted on the map. Tapping a different country switches to it and clears the text. Already-named countries do nothing. Giving up turns the unnamed countries red, and tapping a red country shows its name. Accepted names are current names plus short forms and nicknames (UK, USA, UAE, DRC, Holland and so on), but not former names (Swaziland, Burma, Macedonia). Matching ignores capitals, accents, punctuation and a leading "the", treats "St" as "Saint" and "&" as "and", and allows one typo in names of six or more letters, but not just for a name that is still being typed.

**Scope and display**

- Same as game 1: whole world on a spinnable 3D globe (with a flat-map toggle), or a single continent such as Europe or Asia on a zoomed flat map, with the counter covering only that continent.
- Same borders, terrain and satellite toggles as game 1.
- Same tiny-country handling as game 1: insets for clusters, arrows for lone tiny countries; tapping either opens the text box.

### Learning mode

A separate practice mode with no scoring. Free tapping is only available here, never inside the quizzes.

- The user taps any country (or its island shape) on the map, the country highlights yellow, and a card shows its name, capital (all capitals where there are several), flag and continent.
- Same map as the quizzes: whole world on the globe or flat map, or a single continent or the Caribbean, with the same zoom, borders and terrain toggles, and the same tiny-country handling.
- Flag images are bundled for this mode in build 1 (an open-licence SVG set keyed by ISO code), and build 2's flag games reuse them.

### 3 and 4. Capitals

Games 3 and 4 mirror games 1 and 2, using capital cities instead of country names. Scope options (whole world on globe or flat map, single continent), display toggles (borders, terrain, satellite) and tiny-country handling (insets and arrows) are all the same.

- **Game 3, Find the country by its capital:** the app shows a capital city name; the user taps the country it belongs to. One tap: correct turns green, wrong highlights only the correct country in red.
- **Game 4, Name the capitals (fill in the map):** the user taps any country, a text box pops up, and the box reacts only once the correct capital is typed, turning the country green. No wrong answers; a counter tracks progress towards naming every capital.
- Same forgiving matching as game 2, with alternative spellings (for example "Kiev" / "Kyiv").
- Countries with more than one capital (for example South Africa, Bolivia) accept any of them.
- Built 2026-11-15. Game 3 shows the first listed capital and a miss says "Missed: Bamako is in Mali". Game 4 uses the same matching, spelling note and give-up behaviour as game 2. Capitals come from the country data, with corrections and accepted alternatives in `tools/build_data.py` (CAPITALS): for example Mbabane/Lobamba, Sucre/La Paz, Colombo/Sri Jayawardenepura Kotte, Kuala Lumpur/Putrajaya, Kyiv/Kiev, Bern/Berne, Washington/Washington DC.

## Build 2: flag games (built 2026-11-16)

Built: game 5 (Find by flag: a large flag in the centred top bar) and game 6 (Name the flags: a grid of flags with a box under each; tapping the flag or the box starts typing; focus moves to the next unanswered flag). Flags have their own stats tab. All flags come from Flagpedia in their real proportions (Nepal's pennant, square Switzerland and Vatican City). Flags per row: the 3–7 picker stays as a setting (remembered between visits), rather than one fixed size.

Build 1 is games 1 to 4 only. Build 2 adds the games below once build 1 has been tested. Structure the code so new game modes can be added easily.

### 5. Find the country by its flag

- Identical to game 1, but instead of a country name, an image of the country's flag is shown; the user taps that country on the map.
- All the same features as game 1: whole world on a spinnable globe (with flat-map toggle) or a single continent, borders, terrain and satellite toggles, insets and arrows for tiny countries, one tap with green for correct and red highlighting the correct country when wrong.
- Flag images bundled with the app (for example from an open flag set), keyed by ISO code.

### 6. Name the flags (grid, no map)

- No map: a scrollable grid of flags, each with a text box beneath it.
- The user taps any flag and types the country's name. As in game 2, there is no wrong answer: the box reacts only once the correct name (or a close match) is typed.
- When correct, the flag gets a green tick or green highlight, and focus moves automatically to the next unanswered flag.
- The user can tap around freely, answering the flags they know first and coming back to the others.
- Scope: whole world, or a single continent.
- A counter tracks progress, for example "45 / 197".
- Same forgiving name matching as game 2.

## Build 3: US states (built 2026-11-16)

Build 3 adds US state games after build 2. All use a flat map of the US, with Alaska and Hawaii shown as insets, and the same borders, terrain and satellite toggles as game 1. Small states (for example Rhode Island, Delaware) get arrows, as tiny countries do.

Built (build 3): Find, Name, Find by capital, Name capitals, flags and Learning mode for the 50 states. Terrain on the US map is built once from the sharp relief tiles (inverse-projected through the Albers insets) and trimmed to the states. Capital dots: in the capitals games, a dark red dot marks each answered country's or state's capital (every official capital for countries with more than one).


US Learning (decided 2026-11-16):
- State card "More facts": largest city, nickname; area (km² and sq mi, rank of 50), highest point, time zones; year joined, where the name comes from; state bird and flower.
- Statehood timeline in US Learning mode: a slider from 1787 to 1959 with Play. States not yet in the Union are grey and the ones joining that year are highlighted. On trial in the US map only; it could become the history slider for the world map later.
- US states on the world Learning map: zoom into the US and the state borders fade in (dashed); tap a state for its card. Learning mode only, so world quizzes still treat the USA as one country.
- Turned down: colouring the map by topic, a neighbours list, big-city dots.
- Timeline (2026-11-16, later): no borders between areas that weren't states yet; that land is a sand colour ("unformed"); ‹ › arrows jump to the previous or next year a state joined.
- Lakes: the world map now draws the big lakes (Natural Earth 1:50m, 1,000 km² and up; tools/build_lakes.py). Without them the Great Lakes were land and the state borders looked broken there.
- Speed: zoomed in, both maps skip shapes and lines that are off screen (the globe zoomed into the US went from about 100 ms to 21 ms a frame); zoomed right out the flat map strokes the 1:110m lines and only the copies on screen.
- Reservations layer (Learning mode button), on the **US Learning map only** (too heavy for the world globe, 2026-11-16): US federal reservations and Oklahoma tribal areas (US Census, public domain, credited on the map), data/tribal-us.json from tools/build_tribal.py. Tapping one names it.
- **Focus:** tapping a country on the world Learning map shows a "Focus on <country> ›" button above the card that opens that country's own map in Learning mode. So far only the USA ("Focus on The U.S. ›": states, reservations, statehood timeline); a "World map" button goes back. The user wants this for **every country** in the future (FOCUS table in app.js, one entry per country map). Learning mode has no Magnifier and no "Whole US" button.
- **New game menu (2026-11-16):** a ⚙ cog next to Close opens Options (knowledge gaps, timer; a badge counts the ones on). Tabs: Game | Learning mode (Learning mode goes straight to the Learning globe; the old Learn group is gone). Game has World | Countries. Countries lists continent headings (the Caribbean is in North America) with a button per country map (COUNTRY_MAPS in app.js): United States now, Canada and the United Kingdom marked "soon". A country's page has Find: States, Capitals, Flags and Name: States, Capitals, Flags; "States" is the country's own word (Provinces for Canada, Counties for the UK).
- **Canada (built 2026-11-16):** the second country map. Games 1-6 (Find and Name: provinces and territories, capitals, flags), Learning mode with a province card (capital, population 2021, largest city, area, highest point, time zones, year it became part of Canada, name origin, bird, flower), "Focus on Canada" from the world Learning map, and a Reserves layer (Natural Resources Canada, OGL-Canada, credited). Map: Lambert conformal conic (parallels 49°N and 77°N), with the US and Greenland in grey. Data from tools/build_ca.py: data/ca-provinces.json (Natural Earth 1:50m), data/provinces.json, flags data/flags/ca/ (Wikimedia Commons). Prince Edward Island has an adaptive circle. Next country: the United Kingdom (counties).
- **Austria, Czechia, Poland, the Netherlands and Belgium (built 2026-11-26, jobs/overnight_v2.md):** five more country maps from one shared builder, `tools/build_country.py <code>` with each country's config, parts and 18-fact card in `tools/<code>_facts.py`; in the app one `NEW_MAPS` row each, `GG.loadCountry` and `showCountryCard`. Games 1-6 for all (Austria uses the state flags with arms), Focus on, stats tabs, high-resolution coasts. Circles for Vienna, Prague and Brussels. Belgium has two sets (11 provinces / 3 regions) behind the same Set switch as Spain (`SETS`). Plans: [Austria_plan.md](Austria_plan.md), [Czechia_plan.md](Czechia_plan.md), [Poland_plan.md](Poland_plan.md), [Netherlands_plan.md](Netherlands_plan.md), [Belgium_plan.md](Belgium_plan.md).
- **Sweden, South Africa, New Zealand, Portugal, Colombia and Switzerland (built 2026-11-26, jobs/overnight_v3.md):** six more from the shared builder, which gained insets (Portugal's Azores and Madeira; New Zealand's Chatham Islands moved across the date line), island ovals (`ISLES`), enclaves drawn in their own colours (South Africa's Lesotho and Eswatini, Learning mode only, own maps later), clip boxes for far islands, coat-of-arms games (Sweden) and a sea-only coast test (lake shores don't count). Games 5 and 6: Sweden coats of arms, Colombia and Switzerland flags; none for South Africa, New Zealand and Portugal. Plans: [Sweden_plan.md](Sweden_plan.md), [South_Africa_plan.md](South_Africa_plan.md), [New_Zealand_plan.md](New_Zealand_plan.md), [Portugal_plan.md](Portugal_plan.md), [Colombia_plan.md](Colombia_plan.md), [Switzerland_plan.md](Switzerland_plan.md).
- **Chile, Peru, South Korea, Malaysia and Egypt (built 2026-11-27, jobs/overnight_v4.md):** five more from the shared builder, which gained `part_box` insets (Easter Island, enlarged), `context` insets that move neighbours too (East Malaysia below the peninsula, with Brunei), `MERGE` (Gwangju and South Jeolla merged in July 2026, so South Korea has 16 parts), disputed areas (`DISPUTED`: Dokdo, the Hala'ib Triangle, Bir Tawil) with dotted lines and map labels, emblem fallbacks (Egypt's flags-and-emblems games) and Hangul and Arabic card fonts (right to left). Plans: [Chile_plan.md](Chile_plan.md), [Peru_plan.md](Peru_plan.md), [South_Korea_plan.md](South_Korea_plan.md), [Malaysia_plan.md](Malaysia_plan.md), [Egypt_plan.md](Egypt_plan.md).
- **Disputed territories (2026-11-27):** in Learning mode every disputed territory in Natural Earth's list (92: Kashmir, Crimea, Taiwan, Western Sahara, the Falklands, Dokdo, the Kurils, the Spratlys and more) has a dotted outline or ring and a small "Disputed" card (governed by, claimed by, since, why); whole-country cases (Taiwan, Kosovo, Palestine, Belize) get a section on their country card. `tools/build_disputes.py`, `tools/disputes_facts.py`, `data/disputes.json`.
- Still to decide: traditional Native territories. Native Land Digital needs permission to store its data (the app is offline), so the options are asking them, the 10 broad culture areas, or US land cessions (Royce) on the timeline.
Taps on the sea: the country (or grey land) with the nearest coastline wins, within 12 px of that coast, and only if it's still open. Before this, small countries reached about 20 px from their centre, so a tap just off Vietnam could pick Cambodia.

### 7. Find the state

- Like game 1: a state name pops up and the user taps that state. Correct turns green; wrong highlights only the correct state in red.

### 8. Name the states (fill in the map)

- Like game 2: the user taps any state, a text box pops up, and the state turns green once its correct name is typed. No wrong answers; a counter shows progress, for example "12 / 50".

### 9. Find the state by its capital

- Like game 3: a state capital pops up and the user taps the state it belongs to, with the same green and red feedback.

### 10. Name the state capitals (fill in the map)

- Like game 4: the user taps any state, types its capital, and the state turns green once the correct capital is typed. No wrong answers; a counter shows progress, for example "12 / 50".

### 11. Find the state by its flag

- Like game 5: a state flag pops up and the user taps that state, with the same green and red feedback.

### 12. Name the state flags (grid, no map)

- Like game 6: a grid of all 50 state flags, each with a text box beneath it. The user types the state's name; it goes green once correct and moves to the next flag. The user can skip around freely. A counter shows progress, for example "12 / 50".

## Build 4: British and Irish counties (built 2026-11-16)

**Built:** the Countries tab lists United Kingdom and Ireland (both open the "Britain & Ireland" page; Ireland starts on the Ireland region). The page chooses Historic or Ceremonial counties, the region (All, England, Scotland, Wales, Ireland) and the Crown Dependencies (whole map only, off by default), then Find or Name: Counties, County towns, Flags. Historic: 86 counties of Great Britain (Historic County Borders Project, Definition A: detached parts count as part of the county they lie in). Great Britain's coastline for both sets comes from GSHHG (the county sources draw land over estuaries). Ceremonial: 48 English ceremonial counties, 8 Welsh preserved counties and 35 Scottish lieutenancy areas (Ordnance Survey Boundary-Line). Both include Ireland's 32 traditional counties (townlands.ie, OpenStreetMap) and, when switched on, the Isle of Man, Jersey, Guernsey, Alderney and Sark. Flag games use only counties with a UK Flag Registry flag (56 historic; ceremonial areas use the flag of the historic county they're named after, 43) plus the Crown Dependencies. Learning mode (changed 2026-11-17): "Focus on the UK" / "Focus on Ireland" from the world map opens a countries view (England, Scotland, Wales, Northern Ireland, the Republic of Ireland and the Crown Dependencies; no county lines, bold country borders) with a card of facts for each country and "Focus on <country> ›", which opens that country's counties (county card: county town, area, nation, Irish name and province; a button switches county set; "‹ UK & Ireland" goes back). The national borders are also drawn bold on the county maps. County cards also show (user's picks, 2026-11-17): historic kingdom, Scottish clans, county flower (Plantlife 2002), county day and what locals are called, famous food and landmark, motto, what the registered flag shows, and for Irish counties the GAA colours and nickname. Facts live in tools/uk_facts.py (ceremonial areas carry over facts from their historic namesake); `python tools/build_uk.py facts` applies them. Map: transverse Mercator centred on 2°W. Small counties (City of London, Clackmannanshire, the Channel Islands...) get circles. Data: tools/build_uk.py. Sources are credited on the map and in the README.


Build 4 recreates the build 3 games for the counties of Great Britain and the whole island of Ireland. All use a flat map of Britain and Ireland, with the same borders, terrain and satellite toggles as game 1, and arrows or insets for very small counties (for example Rutland, Isle of Wight).

**County set toggle**, chosen before each game:

- **Historic counties** of England, Scotland and Wales.
- **Ceremonial counties** (modern lieutenancy areas) of England, Wales and Scotland, including metropolitan areas such as Greater London and Greater Manchester.
- Ireland always uses the traditional 32 counties, covering both the Republic of Ireland and Northern Ireland.
- Region filter: England, Scotland, Wales, Ireland, or all.
- **Crown Dependencies toggle** (off by default): include the Isle of Man, Jersey, Guernsey, Alderney and Sark as extra entries, with their capitals or main settlements (Douglas, St Helier, St Peter Port, St Anne, and La Seigneurie or simply "Sark" accepted for Sark) in the county town games, and their flags in the flag games.

**County towns replace capitals.** A county town is the county's traditional administrative centre (where its courts and council sat), not necessarily its largest town; for example Lancaster for Lancashire. Where a county's town is disputed or has changed, accept any commonly cited answer.

**Flags:** use flags from the UK Flag Registry (Flag Institute) where they exist. Counties with no registered flag are left out of the flag games, and the counter reflects that.

### 13. Find the county

- Like game 7: a county name pops up and the user taps it.

### 14. Name the counties (fill in the map)

- Like game 8: tap any county and type its name.

### 15. Find the county by its county town

- Like game 9: a county town pops up and the user taps its county.

### 16. Name the county towns (fill in the map)

- Like game 10: tap any county and type its county town.

### 17. Find the county by its flag

- Like game 11: a county flag pops up and the user taps the county.

### 18. Name the county flags (grid, no map)

- Like game 12: a grid of county flags, type each county's name.

## Quiz options

- Scope filter: whole world, or one of six continents: Europe, Asia, Africa, Oceania, North America, South America. There is also one sub-region scope, the Caribbean. It covers countries only, and they also stay in the North America quiz (see Data).
- Length: always every country in the chosen scope (the whole world means all 197). There are no fixed-length quizzes.
- Order: random each time.
- Optional countdown timer, Sporcle-style, or untimed practice mode.
- Back and forward arrows next to the prompt move instantly through the countries still to answer, with no penalty, so the user can answer in any order. There is no skip or pass button.
- Give up button that ends the quiz and shows the answers.

- **Marathon** (named 2026-11-17): the name for the option "every item in the chosen set" when a game offers a choice of lengths (first used in the History games, History_games.md: 10, 20, 50 or Marathon). Use the same name wherever another game gets a length choice.

## Progress and learning

- Track per-country stats: times asked, times correct, last seen.
- "Weak spots" mode that prioritises countries the user often gets wrong (simple spaced repetition is ideal).
- End-of-quiz summary: score, time taken, and a map showing correct countries in green and missed ones in red.
- Personal best per mode and region.
- All progress stored locally on the device.

## Screens

Decided 2026-11-15:
- **Games list:** the New game screen groups the games into three expandable groups. **Find** (tap the country): Countries, By capital, By flag. **Name** (type the answer): Countries, Capitals, Flags. **Learn** (no score): Free tap, Learning mode. Games not built yet show as "soon". Builds 3 and 4 (US states, counties) will add their own sets.
- **Learning mode** replaces Free tap in the Learn group. Its card shows the flag, name, continent, sub-region and areas, capital (with what each capital is for, where a country has several) and population. A "More facts" button adds three groups. **People:** languages, demonym, largest city (when it isn't the capital), currency. **Land:** area with world rank, coast or landlocked, highest point, time zones, driving side. **History and status:** former names, independence, government type, recognition status (for partly recognised states), income level and GDP per person. The figures are a snapshot (World Bank 2025 data). Hand-written facts live in `tools/facts.py`.
- **Sub-regions:** every country has one main sub-region (from the UN scheme, e.g. Southern Europe, Southeast Asia, Polynesia) plus any well-known areas it belongs to (Iberian Peninsula, Balkans, Scandinavia, Caucasus, Himalayas, Horn of Africa, Sahel, Maghreb, Levant, Greater/Lesser Antilles, Guianas, Andes and more). **Later:** make these playable as quiz regions, like the Caribbean.
- **Later idea for Learning mode:** a time slider to go back in time and watch country names and borders change, including empires.
- **Stats page:** opened from its own button in the top bar, not from the games list. It has Countries and Capitals tabs. It shows how well you know each region ("known" means right at least 3 times in 4), your 15 weakest countries, personal bests per game and region, and recent games, plus a reset button. Answers are recorded per country: Find counts right first time; Name counts each country once when the game ends. The end-of-game pop-up says "New personal best!" when a record is beaten.
- **New game screen layout:** two tabs. **Game** holds the game groups, a collapsible Region section (its header shows the choice, e.g. "Region: Europe · 47") and Map (World games only). **Options** holds Game mode and Timer; its tab label shows how many options are on.
- **Knowledge gaps** (called "weak spots" earlier; built 2026-11-15): an option for the Find games ("Game mode: Whole region / Knowledge gaps (20)"). It picks the 20 countries in the region most worth practising. Each country's score is its smoothed wrong rate, raised the longer since it was last seen (simple spaced repetition). Never-asked countries rank above well-known ones. These games count towards stats but not personal bests.
- **Timer** (built 2026-11-15): an optional countdown for all scored games. You choose the seconds per country (3, 5, 10, 15 or 20; defaults 5 for Find and 10 for Name, kept separately), and the total for the chosen region is shown. When it runs out the game ends with "Time's up!" and the rest are shown in red. Without the countdown, the clock shows elapsed time.
- **End of a game:** a pop-up shows the score (for example "38 / 47 right first time" or "named"), the percentage, the number missed and the time taken. It has three buttons: **Review** (close the pop-up and tap any country on the map to see its answer), **Play again** and **Games list**.

1. Home: choose mode.
2. Setup: choose region and timer.
3. Quiz: map plus prompt or text input, score and timer at the top.
4. Results: summary map and stats, with buttons to retry or practise missed countries.
5. Progress: overall mastery per region and list of weakest countries.
6. Settings: dark mode, plus default map toggles (borders, terrain). There's no autocomplete, because it would give answers away, and no "number of attempts" setting, because the find games are one tap per country.

## Data

- One bundled JSON file of countries: name, alternative names, ISO code, capital, alternative capital spellings, continent(s), and an optional sub-region (currently only "caribbean").
- Note countries with multiple capitals (for example South Africa, Bolivia) and accept any of them.
- Map shapes keyed by ISO code to join with the country data.
- **Non-country territories** (Greenland, Western Sahara, French Guiana and so on) are drawn in grey and can't be tapped. A separate territories quiz may come later, so the data should store territories as their own records (type: territory, with a sovereign state), not discard them.
- A country can belong to more than one continent, so continent is a list, not a single value.

### High-resolution coasts (decided 2026-11-17)

- **Standard for every new country map** (Mexico, Brazil, and the countries in [jobs/build_countries.md](jobs/build_countries.md)): two levels of detail. The light file (Natural Earth 1:10m, simplified about 1–3 km) stays the default for loading and zoomed-out drawing; a **detail level** (coast and borders to about 100–200 m) loads only when zoomed in past a threshold, in tiles, so only the part on screen is fetched (like the terrain relief). Taps use whichever level is drawn.
- **Coast source:** GSHHG 2.3.7 full resolution (level f, about 100 m; free to use), already downloaded (`tools/downloads/uk/gshhg-shp-2.3.7.zip`). `tools/fetch_country_data.py` clips it per country to `tools/downloads/<code>/coast_f.geojson` (land L1 and lakes L2). OpenStreetMap's coast is finer but share-alike (ODbL), so not used.
- **Region edges at the coast:** fit each region's shape to the new shoreline (trim or extend), as `fit_to_land` does in `tools/build_uk.py`.
- **Later, not now:** redo the maps already built (US, Canada, India, China, Russia, Australia; the UK already uses GSHHG for its coast) with the detail level. Decided 2026-11-17 to leave them as they are for now and come back to it another time.

### Continent assignments for borderline countries

- **Russia, Turkey:** both Europe and Asia.
- **Egypt:** Africa.
- **Cyprus:** Europe.
- **Georgia, Armenia, Azerbaijan:** Asia.
- **Kazakhstan:** Asia.
- **Panama, Central America and the Caribbean islands (including Trinidad and Tobago):** North America.
- **Caribbean sub-region:** the only sub-region. Caribbean countries and territories (Puerto Rico, Aruba, Curaçao, the Cayman Islands, Martinique and so on) are tagged `caribbean` in the data. Build 1 includes a Caribbean quiz scope with the 13 Caribbean countries only, no territories. These countries are also still part of North America. A later version will add the Caribbean territories to the Caribbean quiz.
- **Middle East** (Israel, Palestine, Lebanon, Syria, Jordan, Iraq, Iran, the Gulf states, Yemen): Asia.
- **Guyana, Suriname:** South America.
- **Indonesia, Timor-Leste:** Asia. **Papua New Guinea:** Oceania.
- **African island nations** (Cape Verde, São Tomé and Príncipe, Comoros, Madagascar, Mauritius, Seychelles): Africa.
- **Iceland, Malta:** Europe. **Maldives, Sri Lanka:** Asia.

## Polish for later (interest scored 1–5 by the user, 2026-11-15)

- 5: Remember the last game settings and map toggles between visits. **Done:** borders, terrain, globe/flat and the last game's settings. The Learning card resets each visit, as the user asked.
- 5: A proper app name and splash screen. **Done:** the app is called **Gaia Quest**, tagline "Learn your world". The splash shows a globe over Europe and Africa turning slowly while its countries light up green, with the name and tagline. It plays while the map loads, lasts at least about 3.4 seconds, and can be tapped away once the app is ready (`js/splash.js`).
- 3: Light/dark theme switch (the app currently follows the phone's setting).
- 2: A "How to play" page.
- 2: Improve the stats page.
- 1: Haptic feedback on right and wrong answers.

## Nice-to-haves for later

- State abbreviations quiz (two-letter codes such as TX), suggested 2026-11-16.
- Airport codes quiz (three-letter codes such as LHR, JFK), the user's idea from the abbreviations quiz, 2026-11-16.

- Haptic feedback on right and wrong answers.
- Daily challenge.
- Streaks.

## Build order

**Build 1 only for now.** Do not start builds 2 to 4 until build 1 has been tested and approved, but design the code so new game modes, map regions (US states, UK and Irish counties) and data sets can be added later without rework.

1. Map rendering with zoom, pan and tap detection, plus the 3D globe and flat-map toggle.
2. Borders and terrain toggles, then satellite view.
3. Game 1, Find the country, for the whole world.
4. Continent filter and zoom.
5. Tiny-country insets and arrows.
6. Game 2, Name the countries, with forgiving name matching and the progress counter.
7. Games 3 and 4, the capitals versions.
8. Results screen and local progress tracking.
8b. Learning mode (name, capital, flag and continent card).
9. Weak spots mode, timer, and polish.

After build 1 is approved: build 2 (games 5 and 6, flags), then build 3 (games 7 to 12, US states), then build 4 (games 13 to 18, British and Irish counties).
