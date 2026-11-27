# Switzerland – Plan

The brief for Switzerland's country map in Gaia Quest ([jobs/overnight_v3.md](jobs/overnight_v3.md)), in the pattern of the other country plans. Written 2026-11-26 from the decisions of 2026-11-18. **No open questions** (the judgement calls made while building are marked as such).

## What's on the map

- **26 cantons**; every exclave stays with its canton. `unit`: **"Cantons"**. Liechtenstein is grey context.
- **Circles:** Basel-Stadt, Appenzell Innerrhoden and Zug.
- The light map is cut to the shoreline (`FIT_LIGHT`) so the lakes show; the cantons are marked landlocked (`LANDLOCKED`).

## Wiring

`COUNTRY_MAPS.CHE` (Europe); projection: Lambert conformal conic, parallels 45.8°N and 47.8°N, centre 8.23°E.

## Data

- Population: STATPOP (the FSO's PxWeb API), 31 December 2025, total 9,127,125. Flags: all 26 (flag games).

## Names matching

English, German, French and Italian names (Geneva / Genève / Genf / Ginevra; Graubünden / Grisons / Grigioni / Grischun); Obwalden / Nidwalden, the two Appenzells and the two Basels never count for each other.

## Learning card

Name, kind, capital, population (Statistics Switzerland, STATPOP, 31 December 2025: 9,127,125), area and rank, and the flag where there is one. **More facts (20, chosen 2026-11-18):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **official language; year it joined the Confederation; famous cheese or chocolate**. Coast (on the sea, not lake shores) and borders come from the shapes. Facts not found are left out (`tools/ch_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-26 with the shared builder: `python tools/build_country.py ch` (config, parts and facts in `tools/ch_facts.py`; data in `data/ch-states.json`, `data/ch-parts.json`, `data/ch-detail/`). App: one row in `NEW_MAPS` (js/app.js), loader `GG.loadCountry`, card `showCountryCard`, projection style `switzerland` (js/mapview.js). Tests: `_bench_nm.html?d=ch&r=switzerland` (anchors, names, capitals, flags, card, tap test at three zooms with the detail level) all pass.
