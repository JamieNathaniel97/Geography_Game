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

**Tiny countries**

- **Clusters** (for example the Caribbean islands, small Pacific nations): a box or circle marks the crowded area; tapping it opens a zoomed-in inset on an empty part of the map (such as open ocean) where those countries can be tapped individually.
- **Lone tiny countries** (for example Singapore, Vatican City, Maldives): an arrow points to the country, and tapping the arrow counts the same as tapping the country.

### 2. Name the countries (fill in the map)

The goal is to fill in the whole map by naming every country, in any order the user likes.

**How it plays**

- The user taps any country on the map, and a text box pops up.
- The user types the country's name. There is no submit button and no wrong answer: the box simply does not react until the correct name is typed.
- As soon as the correct name (or a close enough match) is typed, the country turns green and the box closes, Sporcle-style.
- Matching is forgiving of case, accents, minor typos and common alternative names (for example "Ivory Coast" / "Côte d'Ivoire", "Czechia" / "Czech Republic", "USA" / "United States").
- A counter shows progress, for example "45 / 197".

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

## Build 2: future games (do not build yet)

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

## Build 3: US states (do not build yet)

Build 3 adds US state games after build 2. All use a flat map of the US, with Alaska and Hawaii shown as insets, and the same borders, terrain and satellite toggles as game 1. Small states (for example Rhode Island, Delaware) get arrows, as tiny countries do.

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

## Build 4: British and Irish counties (do not build yet)

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
- Give up / skip button that shows the answer.

## Progress and learning

- Track per-country stats: times asked, times correct, last seen.
- "Weak spots" mode that prioritises countries the user often gets wrong (simple spaced repetition is ideal).
- End-of-quiz summary: score, time taken, and a map showing correct countries in green and missed ones in red.
- Personal best per mode and region.
- All progress stored locally on the device.

## Screens

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

## Nice-to-haves for later

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
