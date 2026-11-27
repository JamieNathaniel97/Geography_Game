# New Zealand – Plan

The brief for New Zealand's country map in Gaia Quest ([jobs/overnight_v3.md](jobs/overnight_v3.md)), in the pattern of the other country plans. Written 2026-11-26 from the decisions of 2026-11-18. **No open questions** (the judgement calls made while building are marked as such).

## What's on the map

- **16 regions and the Chatham Islands** (17). `unit`: **"Regions"**. The other outlying islands (Kermadec, Three Kings, the subantarctic islands) and Tokelau are left off.
- **The Chatham Islands** lie east of the date line: moved 360° east so they sit beside the mainland (no frame), with a tappable oval.

## Wiring

`COUNTRY_MAPS.NZL` (Oceania); projection: transverse Mercator on 173°E (NZTM2000).

## Data

- Population: Census 2023. The 16 regions and the Chathams (612) are 18 short of the national 4,993,923 (the other outlying islands and Stats NZ's random rounding); allowed (`TOTAL_TOL`).
- **No games 5 and 6** (no official regional flags).

## Names matching

Māori names accepted (Tāmaki Makaurau, Te Taitokerau, Waitaha, Ōtākou, Murihiku, Rēkohu…), macrons optional.

## Learning card

Name, kind, capital, population (Stats NZ, Census 2023: 4,993,923), area and rank, and the flag where there is one. **More facts (20, chosen 2026-11-18):** name in the local language; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **Māori name and main iwi; North or South Island; famous film location**. Coast (on the sea, not lake shores) and borders come from the shapes. Facts not found are left out (`tools/nz_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-26 with the shared builder: `python tools/build_country.py nz` (config, parts and facts in `tools/nz_facts.py`; data in `data/nz-states.json`, `data/nz-parts.json`, `data/nz-detail/`). App: one row in `NEW_MAPS` (js/app.js), loader `GG.loadCountry`, card `showCountryCard`, projection style `newzealand` (js/mapview.js). Tests: `_bench_nm.html?d=nz&r=newzealand` (anchors, names, capitals, flags, card, tap test at three zooms with the detail level) all pass.
