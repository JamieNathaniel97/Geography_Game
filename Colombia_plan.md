# Colombia – Plan

The brief for Colombia's country map in Gaia Quest ([jobs/overnight_v3.md](jobs/overnight_v3.md)), in the pattern of the other country plans. Written 2026-11-26 from the decisions of 2026-11-18. **No open questions** (the judgement calls made while building are marked as such).

## What's on the map

- **32 departments and Bogotá** (33). `unit`: **"Departments"**. Natural Earth gives Bogotá and Cundinamarca the same code; the build splits them (`NE_FIX`).
- **Bogotá:** a circle. **San Andrés and Providencia:** moved closer into a small framed inset in the Caribbean, with an oval. Malpelo and the far cays are left off.

## Wiring

`COUNTRY_MAPS.COL` (South America); projection: transverse Mercator on 73°W.

## Data

- Population: Census 2018 (DANE's adjusted total), total 48,258,494. (The census article's first row is labelled "Cundinamarca" but is Bogotá.)
- Flags: all 33 (flag games).

## Capitals

**Cundinamarca sits out the capitals games**: its government is in Bogotá, which isn't part of it (the card says so).

## Names matching

Accents optional; Cauca and Valle del Cauca, Santander and Norte de Santander, Guainía and Guaviare never count for each other.

## Learning card

Name, kind, capital, population (DANE, Census 2018: 48,258,494), area and rank, and the flag where there is one. **More facts (20, chosen 2026-11-18):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **natural region; famous coffee, fruit or crop; music style**. Coast (on the sea, not lake shores) and borders come from the shapes. Facts not found are left out (`tools/co_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-26 with the shared builder: `python tools/build_country.py co` (config, parts and facts in `tools/co_facts.py`; data in `data/co-states.json`, `data/co-parts.json`, `data/co-detail/`). App: one row in `NEW_MAPS` (js/app.js), loader `GG.loadCountry`, card `showCountryCard`, projection style `colombia` (js/mapview.js). Tests: `_bench_nm.html?d=co&r=colombia` (anchors, names, capitals, flags, card, tap test at three zooms with the detail level) all pass.
