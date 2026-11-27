# South Africa – Plan

The brief for South Africa's country map in Gaia Quest ([jobs/overnight_v3.md](jobs/overnight_v3.md)), in the pattern of the other country plans. Written 2026-11-26 from the decisions of 2026-11-18. **No open questions** (the judgement calls made while building are marked as such).

## What's on the map

- **9 provinces**. `unit`: **"Provinces"**. The Prince Edward Islands are left off (`CLIP`).
- **Lesotho and Eswatini** are drawn as shapes in their flag colours (**Lesotho blue, Eswatini red**: a judgement call on the shades), tappable in Learning mode only (left out of the games, like Italy's enclaves), with a short card: capital, population, area, what it's known for, and "Its own map: coming soon". Their own maps (Lesotho's 10 districts, Eswatini's 4 regions) are a later job; a "Focus on" button comes with them.

## Wiring

`COUNTRY_MAPS.ZAF` (Africa); projection: Albers equal-area conic, parallels 24°S and 33°S, centre 25°E.

## Data

- Population: Census 2022. **Stats SA's provincial figures add up to 62,027,502, one less than its national total of 62,027,503** (rounding in the census weighting); the build allows that gap (`TOTAL_TOL`).
- **No games 5 and 6** (no official provincial flags), and no flags on the province cards.

## Names matching

English and Afrikaans or local names (Free State / Vrystaat, North West / Bokone Bophirima); Eastern and Western Cape never count for each other.

## Learning card

Name, kind, capital, population (Stats SA, Census 2022: 62,027,503), area and rank, and the flag where there is one. **More facts (20, chosen 2026-11-18):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **main home languages; Big Five reserve or famous wildlife; what it was before 1994**. Coast (on the sea, not lake shores) and borders come from the shapes. Facts not found are left out (`tools/za_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-26 with the shared builder: `python tools/build_country.py za` (config, parts and facts in `tools/za_facts.py`; data in `data/za-states.json`, `data/za-parts.json`, `data/za-detail/`). App: one row in `NEW_MAPS` (js/app.js), loader `GG.loadCountry`, card `showCountryCard`, projection style `southafrica` (js/mapview.js). Tests: `_bench_nm.html?d=za&r=southafrica` (anchors, names, capitals, flags, card, tap test at three zooms with the detail level) all pass.
