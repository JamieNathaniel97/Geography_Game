# Austria – Plan

The brief for Austria's country map in Gaia Quest ([jobs/overnight_v2.md](jobs/overnight_v2.md)), in the pattern of the other country plans. Written 2026-11-26 from the decisions of 2026-11-18. **No open questions** (the judgement calls made while building are marked as such).

## What's on the map

- **9 states** (*Bundesländer*): Burgenland, Carinthia, Lower Austria, Upper Austria, Salzburg, Styria, Tyrol, Vorarlberg, Vienna. `kind`: State (Vienna: State and city). `unit`: **"States"**.
- Neighbours as grey context: Germany, Czechia, Slovakia, Hungary, Slovenia, Italy, Switzerland, Liechtenstein.
- **Circle:** Vienna (inside Lower Austria).

## Wiring

`COUNTRY_MAPS.AUT` (from `NEW_MAPS.at`); projection: Lambert conformal conic (MGI Austria Lambert: standard parallels 46°N and 49°N, centre 13.33°E).

## Data

- Shapes: Natural Earth admin-1 (9 states, complete); detail level from `tools/downloads/at/coast_f.geojson` (landlocked: lakes and borders).
- Population: Statistik Austria, 1 January 2025 (Wikidata); the states add up to 9,197,213.
- **Flags (judgement call):** the state flags with arms (`tools/downloads/at/flags_state/`), because Salzburg, Vienna and Vorarlberg share the same red-white civil flag, which would make Find by flag ambiguous.

## Capitals

Eisenstadt, Klagenfurt, St. Pölten, Linz, Salzburg, Graz, Innsbruck, Bregenz, Vienna (its own capital, like Berlin).

## Names matching

English and German: Carinthia / Kärnten, Lower Austria / Niederösterreich, Upper Austria / Oberösterreich, Styria / Steiermark, Tyrol / Tirol, Vienna / Wien; umlauts optional. Upper and Lower Austria never count for each other.

## Learning card

Name, kind, capital, population (Statistik Austria, 1 January 2025: 9,197,213), area and rank, flag. **More facts (18, chosen 2026-11-18):** name in German; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **ski resorts or Alpine peaks**. Coast and borders come from the shapes. Facts not found are left out (`tools/at_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-26 with the shared builder: `python tools/build_country.py at` (config, parts and facts in `tools/at_facts.py`; data in `data/at-states.json`, `data/at-parts.json`, `data/at-detail/`, flags in `data/flags/at/`). App: one row in `NEW_MAPS` (js/app.js), loader `GG.loadCountry`, card `showCountryCard`, projection style `austria` (js/mapview.js). Tests: `_bench_nm.html?d=at&r=austria` (anchors, names, capitals, flags, card, tap test at three zooms with the detail level) all pass.
