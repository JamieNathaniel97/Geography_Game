# Malaysia – Plan

The brief for Malaysia's country map in Gaia Quest ([jobs/overnight_v4.md](jobs/overnight_v4.md)). Written 2026-11-27 from the decisions of 2026-11-18. **No open questions** (judgement calls marked).

## What's on the map

- **13 states and 3 federal territories** (16). Circles: Kuala Lumpur, Putrajaya and Labuan. `unit`: **"States"**.
- **East Malaysia (Sabah, Sarawak, Labuan) is moved into a framed inset below the peninsula**, with Brunei and the Kalimantan coast moved with it (`context`), so both halves fit a tall phone screen at about twice the size. The frame is drawn (no tap area: it holds three parts); its scale bar sits top left, above the land.

## Wiring

`COUNTRY_MAPS.MYS` (Asia); projection: Mercator.

## Data

- Population: OpenDOSM, 1 January 2026 estimates (in thousands); they match DOSM's national figure within its rounding.
- Flags: all 16.

## Learning card

Name, kind, capital, population (DOSM estimates, 1 January 2026: 34,389,400), area and rank, and the flag. **More facts (chosen 2026-11-18):** name in Malay; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **ruler (sultan, raja, governor, or none); main ethnic groups; Peninsula or Borneo**. Facts not found are left out (`tools/my_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-27 with the shared builder: `python tools/build_country.py my` (config, parts and facts in `tools/my_facts.py`). App: one row in `NEW_MAPS`, `GG.loadCountry`, `showCountryCard`, projection style `malaysia`. Tests: `_bench_nm.html?d=my&r=malaysia` all pass.
