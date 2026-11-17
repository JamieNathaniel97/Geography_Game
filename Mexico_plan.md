# Mexico – Plan

The brief for Mexico's country map in Gaia Quest. It follows the same pattern as the built country maps (see [PLAN.md](PLAN.md) and their plans). Drafted 2026-11-17. Nothing is built yet. **Open questions** are at the end.

## What's on the map

**31 states and Mexico City (32 parts):** Aguascalientes, Baja California, Baja California Sur, Campeche, Chiapas, Chihuahua, Coahuila, Colima, Durango, Guanajuato, Guerrero, Hidalgo, Jalisco, State of Mexico, Michoacán, Morelos, Nayarit, Nuevo León, Oaxaca, Puebla, Querétaro, Quintana Roo, San Luis Potosí, Sinaloa, Sonora, Tabasco, Tamaulipas, Tlaxcala, Veracruz, Yucatán, Zacatecas, and **Mexico City** (a federal entity since 2016, no longer the "Federal District").

- Each part has a `kind` (State, or Capital city), shown on the Learning card.
- `unit` word: **"States"** (decided 2026-11-17).
- No disputed borders.

## Wiring it into the app

- `COUNTRY_MAPS`: `MEX: { name: "Mexico", focus: "Mexico", cont: "North America", unit: "States", data: "mx", region: "mexico" }`, next to the US and Canada.
- Loader in `geo.js` for `data/mx-states.json` + `data/mx-parts.json`. Bump `CACHE` in `sw.js`.
- **US Learning map tie-in (idea):** the US and Mexico maps share a border, so the grey Mexico on the US map could link to "Focus on Mexico" later.

## Data build: `tools/build_mx.py`

- Shapes: Natural Earth admin-1 (or INEGI's official boundaries, open data; credit them). Neighbours as grey context: the US, Guatemala, Belize.
- **Projection:** Lambert conformal conic, standard parallels 17.5°N and 29.5°N, central meridian 102°W (the projection INEGI uses).
- Population: **2020 census** (INEGI).
- **Coats of arms instead of flags (decided 2026-11-17):** most states have no official flag of their own (28 of 32 fly the coat of arms on white), so games 5 and 6 become **"Find by coat of arms"** and **"Name the coats of arms"**, using each state's coat of arms (Wikimedia Commons, `data/flags/mx/`). Mexico City uses its coat of arms too.

## Capitals

Confirm during the build. **Twelve states share their capital's name** (Aguascalientes, Campeche, Chihuahua, Colima, Durango, Guanajuato, Oaxaca, Puebla, Querétaro, San Luis Potosí, Tlaxcala, Zacatecas), so they're easy in the capitals games, like Russia's oblasts. Others to know: Toluca (State of Mexico), Guadalajara (Jalisco), Monterrey (Nuevo León), Mérida (Yucatán), Xalapa (Veracruz), Saltillo (Coahuila), Hermosillo (Sonora), Mexicali (Baja California), La Paz (Baja California Sur), Chetumal (Quintana Roo), Tuxtla Gutiérrez (Chiapas), Chilpancingo (Guerrero), Morelia (Michoacán), Cuernavaca (Morelos), Pachuca (Hidalgo), Tepic (Nayarit), Culiacán (Sinaloa), Ciudad Victoria (Tamaulipas), Villahermosa (Tabasco). Mexico City: its own name.

## Names matching

- Accents optional: Michoacan, Queretaro, Nuevo Leon, Yucatan, San Luis Potosi, Merida.
- Full official names accepted: Veracruz de Ignacio de la Llave, Coahuila de Zaragoza, Michoacán de Ocampo.
- **Baja California / Baja California Sur:** typing "Baja California" must only count for Baja California (like Mato Grosso in the Brazil plan).
- Mexico City: "CDMX", "Ciudad de México", "DF" (its old name, still common), "Mexico City".
- **State of Mexico:** typing just **"Mexico"** counts (decided 2026-11-17), as well as "Estado de México" and "State of Mexico".
- English forms: Mexico City, State of Mexico.

## Tiny parts

- **Adaptive circles:** Mexico City, Tlaxcala, Morelos (all small and packed together in the centre), and probably Aguascalientes and Colima. Check on the phone; if the centre is too crowded, use a numbered bubble like the Lesser Antilles.
- **Islands:** the Revillagigedo Islands (Colima) are far out in the Pacific; leave them off, like Australia's external territories.

## Learning card

Name, kind, region, capital, population (2020 census), area and rank of 32.

**More facts (all 18 chosen 2026-11-17):**

1. Region (Northwest, Northeast, Bajío, Central, Gulf, South, Yucatán Peninsula)
2. Main Indigenous peoples and languages
3. Famous dish (mole in Puebla and Oaxaca, cochinita pibil in Yucatán)
4. Famous drink (tequila in Jalisco, mezcal in Oaxaca)
5. Music or dance (mariachi in Jalisco, son jarocho in Veracruz)
6. Biggest festival or tradition (Day of the Dead, Guelaguetza)
7. Main river or water feature (Río Bravo, the Yucatán cenotes)
8. Climate type
9. Highest point (Pico de Orizaba)
10. Time zone(s)
11. A famous natural wonder (Copper Canyon, the monarch butterfly reserve)
12. A famous animal (axolotl, jaguar, grey whales in Baja)
13. Year it became a state
14. UNESCO World Heritage Sites (Chichén Itzá, Teotihuacan)
15. Ancient civilisation (Maya, Aztec, Olmec, Zapotec)
16. Name origin, often from Nahuatl
17. Main industry or crop (avocados in Michoacán, silver in Zacatecas)
18. Largest city, if it isn't the capital (Tijuana, Ciudad Juárez)

## Indigenous layer (decided 2026-11-17)

Learning mode only, like the other countries' Indigenous layers: where the main Indigenous peoples and languages are (Nahuatl, Maya, Zapotec, Mixtec, Otomí, Tzeltal and others). Source: **INALI** (National Institute of Indigenous Languages) or **INPI** (National Institute of Indigenous Peoples) data, or INEGI census counts by municipality. Check the licence before bundling and credit the source on the map. If only municipality counts are open, show the municipalities where most people speak an Indigenous language, coloured by language.

## Build order

1. `tools/build_mx.py`: shapes, parts data, capitals.
2. Map and loader.
3. Find and Name: States, Capitals, Coats of arms.
4. Tiny parts (central circles or bubble).
5. Learning card + "Focus on Mexico".
6. Indigenous layer.
7. Timeline: Mexico's expansion and decline (below).

## Timeline (decided 2026-11-17)

"Mexico's expansion and decline", like Russia's (built the same way: Natural Earth pieces with the years Mexico held them, approximate, today's borders): independence from Spain (1821), with the First Mexican Empire reaching into Central America; Central America leaves (1823); Texas breaks away (1836); the land lost to the US after the Mexican–American War (1848); the Gadsden Purchase (1853); then the states forming, up to Quintana Roo and Baja California Sur (1974). Sources downloaded in `tools/downloads/mx/wiki/`.

## Open questions for the user

None at the moment (all answered 2026-11-17).

**Indigenous layer colouring (decided 2026-11-17):** INEGI's open files give each municipality's number of Indigenous-language speakers but not which language (the by-language table is only in INEGI's SCINCE tool). So the layer shades each municipality by the **share of people who speak an Indigenous language** (2020 census ITER, INEGI; municipal boundaries from geoBoundaries, CC BY 4.0), and a tap names the municipality, its share, and its state's main Indigenous languages (INEGI tabulado "Etnicidad 4"). The by-language SCINCE table can be added later.
