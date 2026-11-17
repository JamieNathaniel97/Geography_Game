# Brazil – Plan

The brief for Brazil's country map in Gaia Quest. It follows the same pattern as the built country maps (Canada, India, China, Russia, Australia; see [PLAN.md](PLAN.md) and their plans). Drafted 2026-11-17. Nothing is built yet. **Open questions** are at the end.

## What's on the map

**26 states and the Federal District (27 parts):**

- **North:** Acre, Amapá, Amazonas, Pará, Rondônia, Roraima, Tocantins.
- **Northeast:** Alagoas, Bahia, Ceará, Maranhão, Paraíba, Pernambuco, Piauí, Rio Grande do Norte, Sergipe.
- **Central-West:** Federal District, Goiás, Mato Grosso, Mato Grosso do Sul.
- **Southeast:** Espírito Santo, Minas Gerais, Rio de Janeiro, São Paulo.
- **South:** Paraná, Rio Grande do Sul, Santa Catarina.
- Each part has a `kind` (State, or Federal District), shown on the Learning card.
- `unit` word: **"States"** (decided 2026-11-17).
- No disputed borders.

## Wiring it into the app

- `COUNTRY_MAPS`: `BRA: { name: "Brazil", focus: "Brazil", cont: "South America", unit: "States", data: "br", region: "brazil" }`. It's the first map under South America.
- Loader in `geo.js` for `data/br-states.json` + `data/br-parts.json`. Bump `CACHE` in `sw.js`.

## Data build: `tools/build_br.py`

- Shapes: Natural Earth admin-1 (or IBGE's official state boundaries, which are open data; credit them). Neighbours as grey context: every South American country except Chile and Ecuador, plus French Guiana as a grey territory.
- **Projection:** Albers equal-area conic, standard parallels about 2°S and 22°S, central meridian 54°W.
- Flags: every state has an official flag (Wikimedia Commons, `data/flags/br/`).
- Population: **2022 census** (IBGE).

## Capitals

Confirm during the build. Two states share their capital's name (São Paulo, Rio de Janeiro). Brasília is the capital of the Federal District and of Brazil. The rest include Manaus, Belém, Salvador, Recife, Fortaleza, Belo Horizonte, Porto Alegre, Curitiba, Florianópolis, Goiânia, Cuiabá, Campo Grande, Palmas, Macapá, Boa Vista, Porto Velho, Rio Branco, São Luís, Teresina, Natal, João Pessoa, Maceió, Aracaju, Vitória.

## Names matching

- Accents optional: Sao Paulo, Para, Amapa, Ceara, Piaui, Maranhao, Goias, Parana, Paraiba, Rondonia.
- **Pará / Paraná / Paraíba** are close. The one-typo rule must not let one count for another (like Shanxi/Shaanxi in the China plan). Same for **Mato Grosso / Mato Grosso do Sul**: typing "Mato Grosso" must only count for Mato Grosso.
- "DF", "Distrito Federal", "Brasília" for the Federal District. Short forms: RJ, SP, MG, RS and so on (two-letter codes are widely used in Brazil).
- English spellings: Amazonas / Amazon State, Federal District.

## Tiny parts

- **Federal District:** an adaptive circle inside Goiás.
- **Sergipe, Alagoas:** check on the phone; probably fine.
- **Islands (decided 2026-11-17):** Fernando de Noronha (Pernambuco) and Trindade (Espírito Santo) are **tappable island ovals**, part of their states.

## Learning card

Name, kind, region, capital, population (2022 census), area and rank of 27, flag.

**More facts (all 17 chosen 2026-11-17):**

1. Region (North, Northeast, Central-West, Southeast, South)
2. Nickname for the people (Carioca, Paulista, Gaúcho)
3. Famous dish (feijoada, acarajé, pão de queijo)
4. Music or dance (samba, forró, frevo)
5. Biggest festival (Carnival, Festa Junina, Parintins)
6. Main river (Amazon, São Francisco, Paraná)
7. Biome (Amazon, Cerrado, Caatinga, Pantanal, Atlantic Forest)
8. Highest point
9. Time zone(s)
10. A famous natural wonder (Iguaçu Falls, Lençóis Maranhenses)
11. A famous animal (jaguar, macaw, pink river dolphin)
12. Year it became a state, and what it was before
13. UNESCO World Heritage Sites
14. Name origin
15. Main industry or crop (coffee, soy, oil)
16. Largest city, if it isn't the capital
17. Football: the biggest club

## Indigenous lands layer (decided 2026-11-17)

Learning mode only, like the US reservations and Australia's Aboriginal land layers: Brazil's official Indigenous territories (*terras indígenas*) from **FUNAI**, the government's Indigenous affairs agency. Check the data licence before bundling and credit FUNAI on the map. Tapping one names it and its people. The Amazon areas are huge, so simplify the shapes to keep the file small.

## Build order

1. `tools/build_br.py`: shapes, parts data, capitals, flags.
2. Map and loader.
3. Find and Name: States, Capitals, Flags.
4. Tiny parts (Federal District circle, Fernando de Noronha and Trindade ovals).
5. Learning card + "Focus on Brazil".
6. Indigenous lands layer.
7. Timeline (below).

## Timeline (decided 2026-11-17)

A timeline of how today's states formed, reusing the US/Australia timeline code: the colonial captaincies (1534), the provinces of the Empire (1822), provinces become states (1889), Acre bought from Bolivia (1903), the capital moves to Brasília (1960), Mato Grosso do Sul (1977), and Tocantins, Amapá and Roraima (1988). Wikipedia's table of how the captaincies became provinces and states is downloaded (`tools/downloads/br/wiki/Federative units of Brazil.wiki`).

## Open questions for the user

None at the moment (all answered 2026-11-17).
