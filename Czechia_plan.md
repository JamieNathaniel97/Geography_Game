# Czechia – Plan

The brief for Czechia's country map in Gaia Quest ([jobs/overnight_v2.md](jobs/overnight_v2.md)), in the pattern of the other country plans. Written 2026-11-26 from the decisions of 2026-11-18. **No open questions** (the judgement calls made while building are marked as such).

## What's on the map

- **14 regions** (*kraje*): Prague, Central Bohemian, South Bohemian, Plzeň, Karlovy Vary, Ústí nad Labem, Liberec, Hradec Králové, Pardubice, Vysočina, South Moravian, Olomouc, Zlín, Moravian-Silesian. `kind`: Region (Prague: Capital city). `unit`: **"Regions"**.
- **Circle:** Prague (inside Central Bohemia).

## Wiring

`COUNTRY_MAPS.CZE`; projection: Lambert conformal conic, standard parallels 49°N and 50.5°N, centre 15.5°E.

## Data

- Shapes: Natural Earth admin-1 (14, complete; its old letter codes, flags named by the new ISO codes).
- **Population (judgement call):** the job asked for the 2021 census, but no census table by region was in the downloads; used the **Czech Statistical Office's 1 January 2026 figures** (the table in "Regions of the Czech Republic"), which add up to its national total of 10,915,839.

## Capitals

Regional capitals; **Central Bohemia sits out the capitals games**: its offices are in Prague, which isn't part of it (the card says so).

## Names matching

"Plzeň Region" or "Plzeň", Czech names (Středočeský kraj, Jihomoravský kraj…), accents optional.

## Learning card

Name, kind, capital, population (Czech Statistical Office, 1 January 2026: 10,915,839), area and rank, flag. **More facts (18, chosen 2026-11-18):** name in Czech; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **the historic land: Bohemia, Moravia or Czech Silesia**. Coast and borders come from the shapes. Facts not found are left out (`tools/cz_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-26 with the shared builder: `python tools/build_country.py cz` (config, parts and facts in `tools/cz_facts.py`; data in `data/cz-states.json`, `data/cz-parts.json`, `data/cz-detail/`, flags in `data/flags/cz/`). App: one row in `NEW_MAPS` (js/app.js), loader `GG.loadCountry`, card `showCountryCard`, projection style `czechia` (js/mapview.js). Tests: `_bench_nm.html?d=cz&r=czechia` (anchors, names, capitals, flags, card, tap test at three zooms with the detail level) all pass.
