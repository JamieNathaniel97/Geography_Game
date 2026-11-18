# Spain – Plan

The brief for Spain's country map in Gaia Quest, in the same pattern as the built country maps (see [PLAN.md](PLAN.md)) and the build job ([jobs/build_countries.md](jobs/build_countries.md), with the checklist every build follows). Drafted 2026-11-18 from the decisions of 2026-11-17. **Open questions** are at the end.

## What's on the map

**Two sets** (decided 2026-11-17), like the UK's historic and ceremonial counties:

- **Communities:** the 17 autonomous communities (Andalusia, Aragon, Asturias, Balearic Islands, Basque Country, Canary Islands, Cantabria, Castile and León, Castilla–La Mancha, Catalonia, Extremadura, Galicia, La Rioja, Madrid, Murcia, Navarre, Valencia) and the 2 autonomous cities (Ceuta, Melilla): 19 parts.
- **Provinces:** the 50 provinces (plus Ceuta and Melilla), the harder set.
- **The Canary Islands in an inset** (decided), as Spanish maps usually show them.
- `unit` word: **"Communities"** / **"Provinces"**. Grey context: Portugal, France, Andorra, Morocco (south), Gibraltar (UK, grey), Algeria.

## Wiring

`COUNTRY_MAPS.ESP`: `{ name: "Spain", focus: "Spain", cont: "Europe", unit: "Communities", data: "es", region: "spain" }`, with a set switch on its page like the UK's (Communities / Provinces). `DATASETS.es` (communities) and `DATASETS.esp` (provinces). Projection: **Lambert conformal conic**, standard parallels 36°N and 43°N, centre 3.5°W; the Canaries inset with its own frame.

## Data build: `tools/build_es.py`

- Shapes: Natural Earth admin-1 lists the 50 provinces (and the 2 cities) with their community: the provinces set as they are, the communities set dissolved from them. **Detail level** from `tools/downloads/es/coast_f.geojson` (including the Canaries window).
- Population: the 2021 census (INE), from the downloaded list articles; check against the national total.
- Flags: all 17 communities and the 2 cities have flags (`tools/downloads/es/flags/`); provinces don't get flag games.
- **The inset:** draw the Canaries in a box at the lower left of the map (like the US's Alaska and Hawaii insets on other maps), tappable, with their own detail level.

## Capitals

Communities: Seville, Zaragoza, Oviedo, Palma, Vitoria-Gasteiz, Santa Cruz de Tenerife and Las Palmas (the Canaries share their capital), Santander, Valladolid, Toledo, Barcelona, Mérida, Santiago de Compostela, Logroño, Madrid, Murcia, Pamplona, Valencia; Ceuta, Melilla. Provinces: each province's capital (usually its namesake).

## Names matching

- English, Spanish and the co-official names: Andalusia / Andalucía, Catalonia / Cataluña / Catalunya, Basque Country / País Vasco / Euskadi, Galicia, Valencia / Comunidad Valenciana / Valencian Community, Balearic Islands / Islas Baleares / Illes Balears, Navarre / Navarra / Nafarroa, Castile and León / Castilla y León, Castilla–La Mancha / Castile-La Mancha, Aragon / Aragón, Canary Islands / Canarias.
- Capitals: Seville / Sevilla, Saragossa / Zaragoza, Vitoria / Gasteiz, Pamplona / Iruña, Palma / Palma de Mallorca, A Coruña / La Coruña.
- Accents optional.

## Tiny parts

Circles for **Ceuta** and **Melilla**; the Balearics as island ovals if needed.

## Flags (games 5 and 6)

Flag games for the communities set (19 flags); none for the provinces set.

## Learning card

**Communities:** name, kind, capital, population (2021 census), area and rank, flag. **More facts (18, chosen 2026-11-17):** name in Spanish and in its own language; co-official language; demonym; famous dish; drink; biggest fiesta; music or dance; football: biggest club; highest point; main river; coast; natural wonder or national park; old kingdom; Moorish heritage; famous landmark; UNESCO World Heritage; known for; largest city if it isn't the capital.

**Provinces:** a shorter card: name, capital, population, community, a landmark.

## Layers and timeline

- **Languages layer** (decided 2026-11-17): Learning mode, where Catalan (and Valencian), Basque, Galician, Aranese and the others are spoken. **Waiting for data:** an open source for the areas is still to find (for example the Valencian-speaking area and Navarre's Basque zones, fixed in law, joined to municipal boundaries from geoBoundaries, CC BY 4.0). The language articles are downloaded.
- **Timeline: to discuss** (morning agenda, 2026-11-18).

## Build order

1. `tools/build_es.py` (both sets, the inset, detail level, parts, capitals, flags) and `tools/es_facts.py`.
2. Map with the inset, loader, set switch, cards, stats tabs, "Focus on Spain".
3. Tests (the build job's checklist).
4. The languages layer, once its data is found; the timeline, once decided.

## Open questions for the user

- The timeline (morning agenda).
- The languages layer's data source (to find).
