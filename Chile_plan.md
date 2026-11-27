# Chile – Plan

The brief for Chile's country map in Gaia Quest ([jobs/overnight_v4.md](jobs/overnight_v4.md)). Written 2026-11-27 from the decisions of 2026-11-18. **No open questions** (judgement calls marked).

## What's on the map

- **16 regions** (Ñuble, 2018, included). `unit`: **"Regions"**. No Antarctic claim; the Desventuradas islets are left off (`CLIP`).
- **Insets** (Valparaíso's islands, `part_box`: only the islands move): **Easter Island enlarged three times** (it was 6 px wide) and the **Juan Fernández Islands** framed at their own place; square tap areas and their own scale bars.

## Wiring

`COUNTRY_MAPS.CHL` (South America); projection: transverse Mercator on 71°W. Detail level simplified to 0.0035° (the fjords).

## Data

- Population: **Census 2024**. The list article's Arica y Parinacota figure (224,569) is a typo for 244,569 (its own article and the table's density agree); with that, the 16 add up to the national 18,480,432.
- Flags: all 16.

## Learning card

Name, kind, capital, population (INE, Census 2024: 18,480,432), area and rank, and the flag. **More facts (chosen 2026-11-18):** name in Spanish; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **climate zone; famous wine valley or mine; Indigenous peoples**. Facts not found are left out (`tools/cl_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-27 with the shared builder: `python tools/build_country.py cl` (config, parts and facts in `tools/cl_facts.py`). App: one row in `NEW_MAPS`, `GG.loadCountry`, `showCountryCard`, projection style `chile`. Tests: `_bench_nm.html?d=cl&r=chile` all pass.
