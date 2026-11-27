# Poland – Plan

The brief for Poland's country map in Gaia Quest ([jobs/overnight_v2.md](jobs/overnight_v2.md)), in the pattern of the other country plans. Written 2026-11-26 from the decisions of 2026-11-18. **No open questions** (the judgement calls made while building are marked as such).

## What's on the map

- **16 voivodeships**, named by their usual English adjective (Lower Silesian, Kuyavian-Pomeranian, Lublin, Lubusz, Łódź, Lesser Poland, Masovian, Opole, Subcarpathian, Podlaskie, Pomeranian, Silesian, Świętokrzyskie, Warmian-Masurian, Greater Poland, West Pomeranian). `unit`: **"Voivodeships"**. No circles.

## Wiring

`COUNTRY_MAPS.POL`; projection: transverse Mercator on 19°E (PUWG 1992's meridian).

## Data

- Shapes: Natural Earth admin-1 (16, complete).
- **Population (judgement call):** the job asked for the 2021 census, but no census table by voivodeship was in the downloads (and GUS's API didn't answer); used **GUS's 30 June 2025 figures** from "Voivodeships of Poland", total 37,401,692 (the table's sum).

## Capitals

Split capitals: **Kuyavian-Pomeranian** Bydgoszcz (governor) and Toruń (assembly); **Lubusz** Gorzów Wielkopolski (governor) and Zielona Góra (assembly). Both are accepted and both get a dot; the first is the one shown in Find by capital.

## Names matching

English adjective and noun forms (Lower Silesia, Masovia), "… Voivodeship", Polish names (dolnośląskie, Małopolska); accents optional (ł counts as l). Lesser / Greater Poland, Pomeranian / West Pomeranian, Silesian / Lower Silesian never count for each other.

## Learning card

Name, kind, capital, population (GUS, 30 June 2025: 37,401,692), area and rank, flag. **More facts (18, chosen 2026-11-18):** name in Polish; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **which partition it was in before 1918 (Prussian, Russian or Austrian), or that it was part of Germany until 1945**. Coast and borders come from the shapes. Facts not found are left out (`tools/pl_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-26 with the shared builder: `python tools/build_country.py pl` (config, parts and facts in `tools/pl_facts.py`; data in `data/pl-states.json`, `data/pl-parts.json`, `data/pl-detail/`, flags in `data/flags/pl/`). App: one row in `NEW_MAPS` (js/app.js), loader `GG.loadCountry`, card `showCountryCard`, projection style `poland` (js/mapview.js). Tests: `_bench_nm.html?d=pl&r=poland` (anchors, names, capitals, flags, card, tap test at three zooms with the detail level) all pass.
