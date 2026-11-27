# South Korea – Plan

The brief for South Korea's country map in Gaia Quest ([jobs/overnight_v4.md](jobs/overnight_v4.md)). Written 2026-11-27 from the decisions of 2026-11-18. **No open questions** (judgement calls marked).

## What's on the map

- **16 divisions, not 17: Gwangju and South Jeolla merged on 1 July 2026** into the **Jeonnam-Gwangju Integrated Special City** (전남광주통합특별시). Natural Earth still has them apart; the build dissolves them (`MERGE`, id `KR-JG`, no ISO code yet). Its flag isn't on Commons yet, so it sits out the flag games. `unit`: **"Provinces & cities"**.
- **Dokdo** (governed by South Korea, claimed by Japan): joined to North Gyeongsang, with a dotted ring.
- Gangwon State (2023) and Jeonbuk State (2024) by their new names; the old ones are accepted.
- Hangul names on the cards: a 6 KB subset of Noto Sans KR (`fonts/gq-hangul.woff`).

## Wiring

`COUNTRY_MAPS.KOR` (Asia); projection: transverse Mercator on 127.5°E.

## Data

- Population: the Ministry of the Interior and Safety's resident registration at the end of October 2026 (jumin.mois.go.kr; it already lists the merged city); the 16 add up to 51,075,282. Areas: Korean Wikipedia.
- **Known gap:** Natural Earth's shapes predate Daegu absorbing Gunwi County from North Gyeongsang (2023).
- **Japan's map doesn't show Dokdo** (it's sea there, no dotted line): a mismatch to fix in tools/build_jp.py.

## Learning card

Name, kind, capital, population (MOIS resident registration, October 2026: 51,075,282), area and rank, and the flag. **More facts (chosen 2026-11-18):** name in Korean (Hangul, with its romanisation); demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **famous food; historic kingdom**. Facts not found are left out (`tools/kr_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-27 with the shared builder: `python tools/build_country.py kr` (config, parts and facts in `tools/kr_facts.py`). App: one row in `NEW_MAPS`, `GG.loadCountry`, `showCountryCard`, projection style `southkorea`. Tests: `_bench_nm.html?d=kr&r=southkorea` all pass.
