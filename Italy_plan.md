# Italy – Plan

The brief for Italy's country map in Gaia Quest, in the same pattern as the built country maps (see [PLAN.md](PLAN.md)) and the build job ([jobs/build_countries.md](jobs/build_countries.md), with the checklist every build follows). Drafted 2026-11-18 from the decisions of 2026-11-17. **Open questions** are at the end.

## What's on the map

- **20 regions**, 5 of them with special statute (Sardinia, Sicily, Trentino-Alto Adige/Südtirol, Aosta Valley, Friuli-Venezia Giulia).
- **The 107 provinces as a second set: to confirm** (morning agenda, 2026-11-18). Built only once confirmed; the build keeps the province data so it can follow quickly.
- **Vatican City and San Marino** (decided 2026-11-17): enclaves shown as **circles in their flag colours: Vatican City yellow, San Marino blue**, each with a **"Focus on Vatican City" / "Focus on San Marino"** button. Their own maps (buildings and streets, needing very high-resolution data) are a separate later job ([jobs/build_countries.md](jobs/build_countries.md), "Vatican City and San Marino"): until then the circles are shown and tappable for a short card, and the Focus buttons wait.
- `kind`: Region, or Autonomous region (special statute).
- `unit` word: **"Regions"**. Grey context: France, Switzerland, Austria, Slovenia, Croatia (across the Adriatic), Tunisia and Malta (south), Monaco.

## Wiring

`COUNTRY_MAPS.ITA`: `{ name: "Italy", focus: "Italy", cont: "Europe", unit: "Regions", data: "it", region: "italy" }`. Loader `GG.loadIT`; `DATASETS.it`. Projection: **Transverse Mercator**, centre 12.5°E (Italy runs north–south).

## Data build: `tools/build_it.py`

- Shapes: Natural Earth admin-1 lists the provinces with their region: **dissolve into the 20 regions** (keep the provinces for the second set). **Detail level** from `tools/downloads/it/coast_f.geojson` (Sicily, Sardinia, the smaller islands).
- Population: ISTAT's latest census; check against the national total.
- Flags: all 20 regions have flags (`tools/downloads/it/flags/`).

## Capitals

Turin, Aosta, Milan, Trento, Venice, Trieste, Genoa, Bologna, Florence, Perugia, Ancona, Rome, L'Aquila, Campobasso, Naples, Bari, Potenza, Catanzaro, Palermo, Cagliari. (Trentino-Alto Adige's capital is Trento; Bolzano is the other provincial capital.)

## Names matching

- English and Italian: Lombardy / Lombardia, Tuscany / Toscana, Piedmont / Piemonte, Sardinia / Sardegna, Sicily / Sicilia, Apulia / Puglia, Aosta Valley / Valle d'Aosta, Trentino-South Tyrol / Trentino-Alto Adige / Südtirol, Lazio / Latium.
- Capitals: Turin / Torino, Milan / Milano, Venice / Venezia, Genoa / Genova, Florence / Firenze, Naples / Napoli, Rome / Roma.
- Accents optional.

## Tiny parts

- Vatican City and San Marino: the coloured circles above.
- Aosta Valley and Molise are small but big enough; check on the phone.

## Flags (games 5 and 6)

Flag games for the 20 regions.

## Learning card

Name, kind, capital, population, area and rank of 20, flag. **More facts (18, chosen 2026-11-17):** name in Italian; demonym; dialect or minority language; famous dish; protected food (DOP/IGP); famous wine; biggest festival; special-statute region or not; highest point; main river or lake; volcano or natural wonder; coast or islands; before unification (which state); famous landmark; UNESCO World Heritage; famous person from there; known for; largest city if it isn't the capital.

## Layers and timeline

- No layer.
- Timeline: **shelved** (2026-11-17).

## Build order

1. `tools/build_it.py` (provinces dissolved into regions, detail level, parts, capitals, flags) and `tools/it_facts.py`.
2. Map, loader, card, Vatican City and San Marino circles, stats tab, "Focus on Italy".
3. Tests (the build job's checklist).
4. The provinces as a second set, once confirmed.

## Open questions for the user

- The 107 provinces as a second set (morning agenda).
- Vatican City and San Marino's own maps (a separate later job).
