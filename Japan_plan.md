# Japan – Plan

The brief for Japan's country map in Gaia Quest, in the same pattern as the built country maps (see [PLAN.md](PLAN.md)) and the build job ([jobs/build_countries.md](jobs/build_countries.md), with the checklist every build follows). Drafted 2026-11-18 from the decisions of 2026-11-17. **Open questions** are at the end.

## What's on the map

- **47 prefectures**: 1 metropolis (Tokyo, *-to*), 1 circuit (Hokkaido, *-dō*), 2 urban prefectures (Osaka, Kyoto, *-fu*) and 43 prefectures (*-ken*).
- **The 9 regions as a filter** (like the UK's England, Scotland…): Hokkaido, Tōhoku, Kantō, Chūbu, Kansai (Kinki), Chūgoku, Shikoku, Kyūshū, Okinawa.
- `unit` word: **"Prefectures"**. Grey context: Russia (Sakhalin and the Kurils), South Korea, North Korea, China, Taiwan.
- **The southern Kurils** (Japan's "Northern Territories", governed by Russia): the disputed-areas rule: grey, with a dotted line (Russia's map already shows them as Russian-administered with a dotted line on Japan's side).

## Wiring

`COUNTRY_MAPS.JPN`: `{ name: "Japan", focus: "Japan", cont: "Asia", unit: "Prefectures", data: "jp", region: "japan" }`. Loader `GG.loadJP`; `DATASETS.jp`; regions `japan` plus one per region. Projection: **Albers equal-area conic**, standard parallels 30°N and 44°N, centre 137°E (Japan is a long arc; the far southwest islands may need an inset: see open questions).

## Data build: `tools/build_jp.py`

- Shapes: Natural Earth admin-1 (47, complete); **detail level** from `tools/downloads/jp/coast_f.geojson` (thousands of islands: this is the high-resolution showcase).
- Population: the **2020 census**; check against the national total.
- Flags: all 47 prefectures have official flags (`tools/downloads/jp/flags/`).
- **Kanji names** on the cards: subset `tools/downloads/fonts/NotoSansJP.ttf` (downloaded) with `tools/build_fonts.py` to the characters used.

## Capitals

Most share their prefecture's name (Aomori, Akita, Kyoto, Osaka, Hiroshima…), which makes them easy, like Russia's oblasts. The ones to know: Sapporo (Hokkaido), Morioka (Iwate), Sendai (Miyagi), Mito (Ibaraki), Utsunomiya (Tochigi), Maebashi (Gunma), Saitama (Saitama), Yokohama (Kanagawa), Kanazawa (Ishikawa), Kōfu (Yamanashi), Nagoya (Aichi), Tsu (Mie), Ōtsu (Shiga), Kobe (Hyōgo), Matsue (Shimane), Takamatsu (Kagawa), Matsuyama (Ehime), Naha (Okinawa). Tokyo: the seat is in Shinjuku; accept Tokyo.

## Names matching

- Macrons optional and in any spelling: Hyōgo / Hyogo / Hyougo, Tōkyō / Tokyo, Ōita / Oita.
- The suffix is optional: "Aichi" or "Aichi Prefecture" or "Aichi-ken"; "Tokyo-to", "Osaka-fu", "Hokkaido".
- Capitals: Kobe / Kōbe, Kofu / Kōfu, Otsu / Ōtsu.

## Tiny parts

- **Island ovals** for Okinawa and the outlying islands that belong to other prefectures (the Izu and Ogasawara islands of Tokyo, Sado, the Oki islands, Tsushima, Iki, the Amami islands of Kagoshima).
- Small mainland prefectures (Kagawa, Osaka, Tokyo) are big enough on a phone when zoomed to Japan; check, and add circles if not.

## Flags (games 5 and 6)

Flag games for all 47 (the prefectural flags, many with a stylised emblem, *mon*).

## Learning card

Name in English and kanji, kind, region, capital, population (2020 census), area and rank of 47, flag. **More facts (18, chosen 2026-11-17):** name in kanji with its reading; region; famous food or meibutsu; famous festival; traditional craft; dialect; highest point; main river or lake; natural wonder; hot springs; prefectural flower, tree and bird; old province name; famous castle or temple; UNESCO World Heritage; name meaning; known for; mascot; largest city if it isn't the capital.

## Layers and timeline

- No layer.
- **Timeline: to discuss (morning agenda, 2026-11-18).** The idea: zoom out for the empire's expansion and collapse, ending with the atomic bombs (a radioactive symbol on Hiroshima and Nagasaki) and the surrender (a white flag), then the post-war tech boom.

## Build order

1. `tools/build_jp.py`, `tools/jp_facts.py`, the kanji font subset.
2. Map, loader, region filters, card, stats tab, "Focus on Japan".
3. Tests (the build job's checklist).
4. Timeline, once decided.

## Open questions for the user

- The timeline (morning agenda).
- **Okinawa and the far southwest islands:** in place (the map is then very wide and the main islands small), or an inset like Spain's Canaries? Proposed: an inset (most maps of Japan do this). Decided at the build if not answered, and recorded in the review.
