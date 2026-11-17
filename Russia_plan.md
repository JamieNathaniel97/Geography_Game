# Russia – Plan

The brief for Russia's country map in Gaia Quest. It follows the same pattern as Canada, India and China (see [PLAN.md](PLAN.md), [India_plan.md](India_plan.md), [China_plan.md](China_plan.md)). Drafted 2026-11-17. Nothing is built yet. **Open questions** are at the end and need the user's decision before building.

## What's on the map

Russia's regions are called **federal subjects**. **83** of them are internationally recognised:

- **Republics (21):** Adygea, Altai Republic, Bashkortostan, Buryatia, Chechnya, Chuvashia, Dagestan, Ingushetia, Kabardino-Balkaria, Kalmykia, Karachay-Cherkessia, Karelia, Khakassia, Komi, Mari El, Mordovia, North Ossetia–Alania, Sakha (Yakutia), Tatarstan, Tuva, Udmurtia.
- **Krais (9):** Altai Krai, Kamchatka, Khabarovsk, Krasnodar, Krasnoyarsk, Perm, Primorsky, Stavropol, Zabaykalsky.
- **Oblasts (46)**, such as Moscow Oblast, Leningrad Oblast, Novosibirsk Oblast, Sverdlovsk Oblast, Kaliningrad Oblast.
- **Federal cities (2):** Moscow, Saint Petersburg.
- **Autonomous oblast (1):** Jewish Autonomous Oblast.
- **Autonomous okrugs (4):** Chukotka, Khanty-Mansi (Yugra), Nenets, Yamalo-Nenets.
- **Annexed parts of Ukraine:** Russia also counts Crimea, Sevastopol, and the Donetsk, Luhansk, Zaporizhzhia and Kherson regions (89 in all). Almost every country treats these as Ukraine. **Proposed:** use the same rule as India and China, so they're **grey, not part of Russia on this map, with dotted borders** (open question 1). Check that the world map draws Crimea the same way.
- Each part has a `kind` (Republic, Krai, Oblast, Federal city, Autonomous oblast, Autonomous okrug), shown on the Learning card.
- `unit` word: **"Regions"** (open question 2).

## Wiring it into the app

- `COUNTRY_MAPS`: `RUS: { name: "Russia", focus: "Russia", cont: "Europe", unit: "Regions", data: "ru", region: "russia" }`. Russia is in both Europe and Asia (PLAN.md), so list it under both headings in the Countries tab if COUNTRY_MAPS allows that; otherwise under Europe.
- `isCountryMap`, `geoFor`, region button ("Whole Russia"), stats tab label, Focus button: `"ru"` branches, or by then these should live in COUNTRY_MAPS.
- `geo.js` loader for `data/ru-regions.json` + `data/ru-parts.json`. Bump `CACHE` in `sw.js`.

## Data build: `tools/build_ru.py`

- `data/ru-regions.json`: the 83 shapes, with neighbours as grey context (Norway, Finland, the Baltic states, Belarus, Ukraine, Georgia, Azerbaijan, Kazakhstan, Mongolia, China, North Korea, Japan, and the US for Alaska), plus `borders`, `coast` and `disputed` lines.
- `data/ru-parts.json`: names, alternative names, capitals and Learning facts, hand-written.
- **Shape source:** Natural Earth 1:50m or 1:10m admin-1. Check it uses the 83 current regions, since several mergers happened in 2005–2008 (for example Perm Krai, Zabaykalsky Krai, Kamchatka Krai).
- **The 180° line:** Chukotka crosses the antimeridian, so its shape comes in two halves. Join them in the build script.
- **Kaliningrad** is an exclave between Poland and Lithuania, far to the west. It needs either an inset (like Alaska on the US map) or a map wide enough to include it (open question 3).
- **Projection:** Albers equal-area conic, standard parallels about 52°N and 68°N, central meridian 100°E, so the whole country from Kaliningrad to Chukotka fits without too much stretching.

## Disputed areas

Same rule as India and China: **disputed borders dotted, disputed areas grey and untappable.**

- **Crimea, Sevastopol, Donetsk, Luhansk, Zaporizhzhia, Kherson:** see above.
- **Kuril Islands:** governed by Russia, and Japan claims the four southernmost (its "Northern Territories"). **Proposed:** part of Sakhalin Oblast and tappable, since Russia governs them, but with a dotted line between them and Japan (open question 4).

## Capitals

Russia calls them "administrative centres".

- **Most oblasts are named after their centre** (Novosibirsk Oblast → Novosibirsk), which makes the capitals games very easy for those. **Proposed:** keep them all in, because the map side still teaches where they are, but think about this (open question 5).
- **Special cases**, to confirm during the build:
  - Moscow Oblast: no official centre in law. The government sits in **Krasnogorsk**, and **Moscow** is also accepted.
  - Leningrad Oblast: **Gatchina** officially since 2021, and Saint Petersburg is also accepted, since the government is still based there.
  - Moscow, Saint Petersburg: the city's own name, like China's municipalities.
  - Autonomous okrugs: Khanty-Mansiysk, Salekhard, Naryan-Mar, Anadyr.
  - Republics: Kazan (Tatarstan), Ufa (Bashkortostan), Grozny (Chechnya), Makhachkala (Dagestan), Yakutsk (Sakha), Magas (Ingushetia), Vladikavkaz (North Ossetia), and so on.

## Names matching

- The kind word is optional: "Novosibirsk" counts for Novosibirsk Oblast, and "Krasnodar" for Krasnodar Krai. "Oblast" and "Region" both work.
- Accept other spellings from transliteration: Yakutia / Sakha, Bashkiria / Bashkortostan, Chuvashia / Chuvash Republic, Yugra / Khanty-Mansi, Alania / North Ossetia, Primorye / Primorsky, Zabaikalsky / Trans-Baikal, Kemerovo / Kuzbass.
- City spellings: Yekaterinburg / Ekaterinburg, Nizhny / Nizhniy Novgorod, Rostov-on-Don / Rostov-na-Donu.
- **Former Soviet names:** Sverdlovsk (Yekaterinburg), Gorky (Nizhny Novgorod), Kuybyshev (Samara), Leningrad (Saint Petersburg). Some oblasts still have the old name (Sverdlovsk Oblast, Leningrad Oblast) though their city was renamed. That trips people up, so it's worth a spelling note in the capitals games.

## Tiny parts

- **North Caucasus cluster:** Adygea, Ingushetia, North Ossetia, Kabardino-Balkaria, Karachay-Cherkessia and Chechnya are small and packed together. **Proposed:** a numbered bubble like the Lesser Antilles, which splits as you zoom in.
- **Adaptive circles:** Moscow and Saint Petersburg (cities inside their own oblasts). Moscow Oblast surrounds Moscow, and Leningrad Oblast surrounds Saint Petersburg, so the circle sits inside the bigger shape.
- **Island ovals:** check Sakhalin Oblast (Sakhalin plus the Kurils) once it's drawn.
- Some parts are enormous (Sakha is bigger than India). Labels must shrink and grow well.

## Flags (games 5 and 6)

**Every federal subject has an official flag**, so the flag games work, like the US and Canada. Flags from Wikimedia Commons, built to `data/flags/ru/` by the build script, in their real proportions.

## Learning card

- Name in English and **Russian (Cyrillic)**: Новосибирская область. Bundle a Cyrillic font subset for offline use (small).
- Kind, **federal district** (Central, Northwestern, Southern, North Caucasian, Volga, Ural, Siberian, Far Eastern), capital, population (**2021 census**), area and rank of 83.
- **More facts:** choose from the ideas below (open question 6).

## Fact ideas for the user to choose from

**People and culture**
1. Main ethnic groups (Tatars in Tatarstan, Chechens in Chechnya, Yakuts in Sakha)
2. Main languages besides Russian (Tatar, Bashkir, Chechen, Yakut, Buryat)
3. Main religions (Orthodox Christian, Muslim, Buddhist in Buryatia, Kalmykia and Tuva)
4. A famous dish or food (pelmeni, Tatar chak-chak)
5. A famous traditional craft (Gzhel pottery, Khokhloma painting, Matryoshka dolls)

**Land and nature**
6. Main river (Volga, Ob, Yenisei, Lena, Amur)
7. Climate type (tundra, taiga, steppe, subtropical on the Black Sea)
8. Highest point (Elbrus, Europe's highest, in Kabardino-Balkaria)
9. Time zone(s): Russia has 11 time zones
10. A famous national park, nature reserve or natural wonder (Lake Baikal, Kamchatka's volcanoes)
11. A famous animal (Siberian tiger in Primorsky, polar bear in Chukotka)
12. Coldest place or record temperature (Oymyakon in Sakha)

**History and landmarks**
13. Year it joined Russia, or year it took its present form
14. UNESCO World Heritage Sites (Kazan Kremlin, Lake Baikal, Kizhi)
15. Old Soviet name, where it was renamed
16. The Trans-Siberian Railway: does it pass through?

**Economy**
17. Main industry or resource (oil and gas in Yamalo-Nenets and Khanty-Mansi, diamonds in Sakha)
18. Largest city, if it isn't the capital (Sochi, Tolyatti, Magnitogorsk)

## Build order

1. `tools/build_ru.py`: shapes (Chukotka joined, the annexed areas split off as grey), parts data, capitals, flags, disputed lines.
2. Map and loader (Albers projection, grey neighbours, Kaliningrad, lakes, Lake Baikal).
3. Find and Name: Regions, then Capitals, then Flags.
4. Tiny parts (North Caucasus bubble, Moscow and Saint Petersburg circles).
5. Learning card with Cyrillic names + "Focus on Russia".
6. Stats and personal bests.

## Open questions for the user

1. **Annexed parts of Ukraine** (Crimea, Sevastopol, Donetsk, Luhansk, Zaporizhzhia, Kherson): grey and not part of Russia, with dotted borders?
2. **Unit word:** "Regions", or "Federal subjects"?
3. **Kaliningrad:** an inset box, or a wider map that includes it?
4. **Kuril Islands:** part of Sakhalin Oblast and tappable, with the Japan border dotted?
5. **Capitals:** keep all 83, even the ones named after their capital?
6. **Facts:** which of the 18 ideas go on the card?
7. **Toggle:** one for the 6 small kinds (2 federal cities, the autonomous oblast and 4 autonomous okrugs)? The okrugs are huge, though (Yamalo-Nenets, Khanty-Mansi, Chukotka), so hiding them leaves holes, like China. **Proposed:** no toggle.
