# Egypt – Plan

The brief for Egypt's country map in Gaia Quest ([jobs/overnight_v4.md](jobs/overnight_v4.md)). Written 2026-11-27 from the decisions of 2026-11-18. **No open questions** (judgement calls marked).

## What's on the map

- **27 governorates**. Luxor gets a circle. `unit`: **"Governorates"**.
- **The Hala'ib Triangle** (governed by Egypt, claimed by Sudan): part of the Red Sea governorate, its edges dotted. **Bir Tawil** (claimed by neither): grey, untappable, dotted, labelled "Bir Tawil (unclaimed)" once zoomed in a little.
- Arabic names on the cards: a 10 KB subset of Noto Sans Arabic (`fonts/gq-arabic.woff`), laid out right to left.

## Wiring

`COUNTRY_MAPS.EGY` (Africa); projection: Lambert conic (24°N, 30°N, 30.5°E).

## Data

- Population: CAPMAS estimates for November 2023 (the newest by governorate), adding up to 106,668,704.
- **Games 5 and 6: "Find by flag or emblem" (a judgement call):** 25 governorates have flags on Commons; Cairo and Luxor have emblems instead (`FLAG_FALLBACK`). Every governorate has one, so the games run.

## Learning card

Name, kind, capital, population (CAPMAS estimates, November 2023: 106,668,704), area and rank, and the flag. **More facts (chosen 2026-11-18):** name in Arabic (right to left); demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **Upper or Lower Egypt, the Sinai or the desert; ancient sites**. Facts not found are left out (`tools/eg_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-27 with the shared builder: `python tools/build_country.py eg` (config, parts and facts in `tools/eg_facts.py`). App: one row in `NEW_MAPS`, `GG.loadCountry`, `showCountryCard`, projection style `egypt`. Tests: `_bench_nm.html?d=eg&r=egypt` all pass.
