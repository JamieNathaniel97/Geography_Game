# Peru – Plan

The brief for Peru's country map in Gaia Quest ([jobs/overnight_v4.md](jobs/overnight_v4.md)). Written 2026-11-27 from the decisions of 2026-11-18. **No open questions** (judgement calls marked).

## What's on the map

- **24 departments, Lima Province and Callao** (26). Natural Earth gives Lima Province the Lima Region's code; the build splits them (`NE_FIX`). Circles: Lima Province and Callao. `unit`: **"Departments"**.

## Wiring

`COUNTRY_MAPS.PER` (South America); projection: transverse Mercator on 75.5°W.

## Data

- **Population (judgement call):** INEI's 2025 estimates (Wikidata; the Lima Region and Callao from "Regions of Peru"). They add up to 34,170,116, **12,384 (0.04%) above the national 2025 figure** (sources round differently; allowed). The 2017 census would add up exactly; the user's rule is the latest figure.
- Flags: all 26.

## Capitals

Lima Province: Lima; the Lima Region: Huacho. "Lima Region" and "Lima Province" never count for each other.

## Learning card

Name, kind, capital, population (INEI estimates, 2025: 34,157,732), area and rank, and the flag. **More facts (chosen 2026-11-18):** name in Spanish; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **natural region (coast, Andes, Amazon); ancient civilisation; Quechua or Aymara speakers**. Facts not found are left out (`tools/pe_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-27 with the shared builder: `python tools/build_country.py pe` (config, parts and facts in `tools/pe_facts.py`). App: one row in `NEW_MAPS`, `GG.loadCountry`, `showCountryCard`, projection style `peru`. Tests: `_bench_nm.html?d=pe&r=peru` all pass.
