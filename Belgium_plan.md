# Belgium – Plan

The brief for Belgium's country map in Gaia Quest ([jobs/overnight_v2.md](jobs/overnight_v2.md)), in the pattern of the other country plans. Written 2026-11-26 from the decisions of 2026-11-18. **No open questions** (the judgement calls made while building are marked as such).

## What's on the map

**Two sets** (like Spain's): the **10 provinces plus Brussels** (11, dataset `be`, "Provinces") and the **3 regions** (Flanders, Wallonia, Brussels-Capital; dataset `ber`, ids `BER-…` so its stats are separate, "Regions"). The regions are dissolved from the provinces. The Set switch on the country page and a set button in Learning mode switch between them (`SETS` in js/app.js, now shared with Spain). **Circle:** Brussels in both sets.

## Wiring

`COUNTRY_MAPS.BEL` (the regions set isn't listed separately); projection: Lambert conformal conic (Belgian Lambert 2008: 49.83°N and 51.17°N, centre 4.36°E).

## Data

- Population: Statbel, 1 January 2025 (Wikidata); both sets add up to 11,825,551.
- Flags: all 11 and the 3 regions (Flanders' lion, Wallonia's rooster, Brussels' iris).

## Capitals

Antwerp, Ghent, Leuven, Hasselt, Bruges, Mons, Liège, Arlon, Namur, Wavre, Brussels. Regions: Wallonia Namur, Brussels-Capital Brussels; **Flanders sits out the capitals games** (its government sits in Brussels, outside the region).

## Names matching

Dutch, French and German forms (Vlaams-Brabant / Brabant flamand, Liège / Luik / Lüttich, Bruges / Brugge). The two Brabants and the two Flanders never count for each other.

## Learning card

Name, kind, capital, population (Statbel, 1 January 2025: 11,825,551), area and rank, flag. **More facts (18, chosen 2026-11-18):** name in Dutch or French (per part); demonym; dialect or regional language; famous dish; famous drink; biggest festival or tradition; football: the biggest club; main river; highest point; natural wonder or national park; historic region or old kingdom; famous castle or landmark; UNESCO World Heritage; famous person from there; known for; famous company; largest city if it isn't the capital; and **the language community (Dutch-, French- or German-speaking)**. Coast and borders come from the shapes. Facts not found are left out (`tools/be_facts.py`).

## Layers and timeline

None for now (decided 2026-11-18).

## Build

Built 2026-11-26 with the shared builder: `python tools/build_country.py be` (config, parts and facts in `tools/be_facts.py`; data in `data/be-states.json`, `data/be-parts.json`, `data/be-detail/`, flags in `data/flags/be/`). App: one row in `NEW_MAPS` (js/app.js), loader `GG.loadCountry`, card `showCountryCard`, projection style `belgium` (js/mapview.js). Tests: `_bench_nm.html?d=be&r=belgium` (anchors, names, capitals, flags, card, tap test at three zooms with the detail level) all pass.
