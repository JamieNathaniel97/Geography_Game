# Sweden – Plan

The brief for Sweden's country map in Gaia Quest ([jobs/overnight_v3.md](jobs/overnight_v3.md)), in the pattern of the other country plans. Written 2026-11-26 from the decisions of 2026-11-18. **No open questions** (the judgement calls made while building are marked as such).

## What's on the map

- **21 counties** (*län*), shown as "Stockholm County" and so on (the short name, "Stockholm län" and "Stockholms län" also count). `unit`: **"Counties"**. Gotland needs no oval.

## Wiring

`COUNTRY_MAPS.SWE` (Europe); projection: transverse Mercator on 15°E (SWEREF 99 TM).

## Data

- Shapes: Natural Earth admin-1 (21, complete). Detail level simplified to 0.0035° (`DETAIL_TOL`, a judgement call): the archipelagos made 8.5 MB of tiles at the usual 0.002°; now 6.3 MB.
- Population: SCB's population register, 31 December 2024 (its open API; the card says the year), total 10,587,710.
- **Games 5 and 6: coats of arms** (official county arms; "Find by coat of arms", "Name the coats of arms").

## Learning card

Name, kind, capital, population (Statistics Sweden, register, 31 December 2024: 10,587,710), area and rank, and the flag where there is one. **More facts (20, chosen 2026-11-18):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **historic land and province; Sámi area; a Swedish invention or brand from there**. Coast (on the sea, not lake shores) and borders come from the shapes. Facts not found are left out (`tools/se_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-26 with the shared builder: `python tools/build_country.py se` (config, parts and facts in `tools/se_facts.py`; data in `data/se-states.json`, `data/se-parts.json`, `data/se-detail/`). App: one row in `NEW_MAPS` (js/app.js), loader `GG.loadCountry`, card `showCountryCard`, projection style `sweden` (js/mapview.js). Tests: `_bench_nm.html?d=se&r=sweden` (anchors, names, capitals, flags, card, tap test at three zooms with the detail level) all pass.
