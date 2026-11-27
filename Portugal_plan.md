# Portugal – Plan

The brief for Portugal's country map in Gaia Quest ([jobs/overnight_v3.md](jobs/overnight_v3.md)), in the pattern of the other country plans. Written 2026-11-26 from the decisions of 2026-11-18. **No open questions** (the judgement calls made while building are marked as such).

## What's on the map

- **18 districts and the 2 autonomous regions** (20). `unit`: **"Districts"**.
- **Insets:** the Azores (scaled to half size) and Madeira, framed, off the west coast, each with a tappable oval; the Selvagens are left off.

## Wiring

`COUNTRY_MAPS.PRT` (Europe); projection: transverse Mercator on 8.13°W (PT-TM06).

## Data

- Population: Census 2021 (from "Districts of Portugal"), total 10,343,066.
- **Games 5 and 6: none (a judgement call).** The districts have no coats of arms of their own (their articles show the capital cities' arms) and only the Azores and Madeira have flags, so coat-of-arms games would have had 2 of 20. Like France, Portugal has no games 5 and 6; the Azores' and Madeira's flags show on their cards.

## Capitals

The Azores have three: Ponta Delgada (government), Horta (assembly), Angra do Heroísmo (courts); all accepted, each with a dot.

## Learning card

Name, kind, capital, population (INE, Census 2021: 10,343,066), area and rank, and the flag where there is one. **More facts (20, chosen 2026-11-18):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **wine region; historic province; an explorer or Age of Discovery link**. Coast (on the sea, not lake shores) and borders come from the shapes. Facts not found are left out (`tools/pt_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-26 with the shared builder: `python tools/build_country.py pt` (config, parts and facts in `tools/pt_facts.py`; data in `data/pt-states.json`, `data/pt-parts.json`, `data/pt-detail/`). App: one row in `NEW_MAPS` (js/app.js), loader `GG.loadCountry`, card `showCountryCard`, projection style `portugal` (js/mapview.js). Tests: `_bench_nm.html?d=pt&r=portugal` (anchors, names, capitals, flags, card, tap test at three zooms with the detail level) all pass.
