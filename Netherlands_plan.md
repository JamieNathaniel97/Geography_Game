# Netherlands – Plan

The brief for Netherlands's country map in Gaia Quest ([jobs/overnight_v2.md](jobs/overnight_v2.md)), in the pattern of the other country plans. Written 2026-11-26 from the decisions of 2026-11-18. **No open questions** (the judgement calls made while building are marked as such).

## What's on the map

- **12 provinces**; **Bonaire, Sint Eustatius and Saba are left off** (Natural Earth lists them; dropped). `unit`: **"Provinces"**. No circles.
- **The light map is cut to the shoreline too** (`FIT_LIGHT`): Natural Earth's provinces cover the IJsselmeer and the Markermeer, which hid Flevoland's polders.

## Wiring

`COUNTRY_MAPS.NLD`; projection: oblique stereographic on Amersfoort (5.39°E, 52.16°N), like the Dutch RD grid.

## Data

- Population: CBS open data (table 70072ned), 1 January 2025 (no traditional census; the population register), total 18,044,027.
- **Area (judgement call): land area** (the card says "Land area"), since the provinces' totals include the IJsselmeer, the Wadden Sea and the estuaries.

## Capitals

Assen, Lelystad, Leeuwarden, Arnhem, Groningen, Maastricht, 's-Hertogenbosch (Den Bosch), Haarlem, Zwolle, Utrecht, Middelburg, The Hague (Den Haag).

## Names matching

English and Dutch (North Holland / Noord-Holland, Friesland / Fryslân); North and South Holland never count for each other.

## Learning card

Name, kind, capital, population (CBS, 1 January 2025: 18,044,027), area and rank, flag. **More facts (18, chosen 2026-11-18):** name in Dutch; demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **land reclaimed from the sea, and how much lies below sea level**. Coast and borders come from the shapes. Facts not found are left out (`tools/nl_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-26 with the shared builder: `python tools/build_country.py nl` (config, parts and facts in `tools/nl_facts.py`; data in `data/nl-states.json`, `data/nl-parts.json`, `data/nl-detail/`, flags in `data/flags/nl/`). App: one row in `NEW_MAPS` (js/app.js), loader `GG.loadCountry`, card `showCountryCard`, projection style `netherlands` (js/mapview.js). Tests: `_bench_nm.html?d=nl&r=netherlands` (anchors, names, capitals, flags, card, tap test at three zooms with the detail level) all pass.
