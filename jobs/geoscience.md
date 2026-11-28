# Job: Earth mode (geoscience), the build order plan

A non-human side of Gaia Quest: like Learning mode (tap anything, read its card), but for the Earth itself: plates, volcanoes, seas, currents, the ocean floor and, at the end, the continents rewound to Pangea. Decided with the user on 2026-11-28. **Nothing is built yet: this file is the plan.**

**Don't start a stage until the user says so.** Don't commit or push until the user says so.

## What's in it (approved 2026-11-28)

The user's own list, plus every extra idea except biomes (left out by the user):

| Feature | What you see | Tap it for |
| --- | --- | --- |
| Plate boundaries, named | the plates in soft colours, boundaries by type (ridge, trench, transform) | the plate's card: name, area, speed and direction, neighbours |
| Ocean ridges and trenches | ridges and trenches named along the boundaries | depth or height, length, spreading rate |
| Volcanoes | dots by type (stratovolcano, shield, caldera...) | type, height, last eruption, famous eruptions |
| Seas | the named seas and oceans (IHO areas) | area, depth, which ocean it's part of |
| Currents | warm (red) and cold (blue) currents with **animated arrows** showing the direction | warm or cold, speed, what it does to the climate nearby |
| Drain the ocean | the water fades away to show the seafloor (bathymetry) | the undersea features under the tap |
| Rewind to Pangea | a time slider: the continents drift back through 200 million years to Pangea | the period and what was happening |
| 1. Earthquakes | the largest historic quakes sized by magnitude; optionally the last 30 days (live) | magnitude, date, depth, the plates involved |
| 2. Hotspots | Hawaii, Iceland, Yellowstone, Réunion... with the island chains they left | how a hotspot works, the chain's ages |
| 3. Mountain ranges | named ranges, coloured by how they formed (collision, subduction, rifting) | height, age, how it formed |
| 4. The Ring of Fire | a highlight joining the Pacific's volcanoes, trenches and quakes | the story of the Ring of Fire |
| 5. Seafloor age | a colour layer: young crust at the ridges, the oldest near the trenches | the age under the tap |
| 6. Glaciers and ice sheets | today's ice; an **ice-age view** (the Last Glacial Maximum) with the ice sheets and the lower sea (Doggerland, the Bering land bridge) | the ice sheet or land bridge |
| 7. Sea-level slider | raise or lower the sea and watch the coast change | how much land floods or appears |
| 8. Climate zones | the Köppen zones | the zone's code, meaning and typical places |
| 10. Winds | trade winds, westerlies, polar easterlies and the jet stream, animated like the currents; Hadley, Ferrel and polar cells as an explainer card | the wind's name and why it blows that way |
| 11. Rivers and drainage basins | the big rivers and the areas they drain, and which ocean the water reaches | length, discharge, basin area |
| 12. Impact craters | Chicxulub, Vredefort, Sudbury, Meteor Crater... | size, age, what hit |
| 13. Geological wonders | the Grand Canyon, the Giant's Causeway, Uluru, Ha Long Bay... | how it formed |
| 14. Deep places and extremes | Challenger Deep, the Kola borehole, the Dead Sea shore, each continent's highest and lowest points | the record |
| 15. Fossil evidence for drift | Mesosaurus, Glossopteris, Lystrosaurus, Cynognathus on the coasts they share | why it shows the continents were joined; in the rewind, the dots line up as the continents close |

**Games: later** (kept in mind, not built in these stages; each stage's data is built so games can use it): Find the plate, volcano, sea, current or range; Name the feature; Which boundary type? (ridge, trench or transform); Warm or cold current?; Order the eruptions or Biggest quake; the Pangea puzzle (drag the continents back together).

## Decided with the user (2026-11-28)

1. **Its own tab:** a third tab in the menu beside Game and Learning, "Earth".
2. **The base map:** light coasts and no country borders, so the features stand out, with a switch to show the countries.
3. **Layers by checkboxes,** so several can be on at once. **Plates and volcanoes are separate checkboxes** (not one group). Ready-made groups can still tick several at once (for example the Ring of Fire: plates, trenches, volcanoes and quakes), but every layer has its own box.
4. **Globe and flat:** both, as now. The animated arrows and the drain effect are built for both.
5. **Live earthquakes: later in the app, but the code is written now.** `js/quakes-live.js` (done 2026-11-28, not loaded by index.html yet): it reads the USGS real-time feed (any range from the last hour to the last month, any lower magnitude), keeps the last good answer in localStorage for offline use (marked as old), and gives each quake's dot size (by magnitude) and depth band (shallow, intermediate, deep). Tested against the live feed: 485 quakes of M4.5+ in the last month; the cache, and the offline fallback, work. The service worker leaves the feed alone (it only caches the app's own files). Stage 3 adds the layer, the card and the "Live" checkbox; the historic list stays offline.

## Build order

Each stage ends like a country batch: build, test (light and dark themes, globe and flat, phone width), preview, decisions to check, and nothing committed until the user says so.

### Stage 1: the solid Earth (static layers)

Plates (named), ridges and trenches, volcanoes, seas, the Ring of Fire highlight, hotspots and their chains.

- The Earth tab, the base map, the layer checkboxes (decisions 1–3), the card layout (reusing Learning mode's card).
- Line labels that follow a boundary or ridge (new: today's labels sit at a point).
- Volcano dots sized by height and clustered at world zoom (there are about 1,300 Holocene volcanoes).
- **Data:** plates and boundaries: PB2002 (Bird 2003), in Hugo Ahlenius's GeoJSON version; check the licence (ODC-By is expected). Volcanoes: the Smithsonian Global Volcanism Program, free with a citation; check its terms. Seas: the IHO sea areas from Marine Regions (CC BY 4.0 expected). Ridges, trenches and undersea names: the GEBCO undersea feature gazetteer (SCUFN). Hotspots: Wikipedia's list cross-checked with a published hotspot catalogue.

### Stage 2: things that move (animation)

Currents and winds with animated arrows.

- **New: an animation layer** that draws moving arrows (or flowing dashes) along each path on the canvas, for globe and flat; paused when the tab is hidden and with reduced motion; light on a phone's battery.
- Currents: about 30 major surface currents (Gulf Stream, Kuroshio, Humboldt, Antarctic Circumpolar...), warm or cold. Drawn by hand as paths from standard ocean-circulation maps (NOAA and textbook sources, recorded); the shapes are general, not measured data.
- Winds: the global wind belts and the jet streams, drawn by hand the same way; the cells as an explainer card with a diagram.

### Stage 3: what the Earth records

Earthquakes, mountain ranges, seafloor age, impact craters, geological wonders, deep places and extremes, fossil evidence.

- Earthquakes: the USGS catalogue (public domain): the largest historic quakes (offline), and the live feed through `js/quakes-live.js` (written already: decision 5), behind its own checkbox.
- Mountain ranges: the GMBA Mountain Inventory v2 (CC BY 4.0 expected), with how each formed.
- Seafloor age: the EarthByte age grid (Seton et al. 2020, CC BY expected), as a colour layer; check its size for a phone (a coarse tile set).
- Impact craters: the Earth Impact Database (check its terms) or Wikipedia's list.
- Geological wonders and extremes: a hand-picked list (about 50) with Wikipedia articles for the cards, as the country cards' facts.
- Fossil evidence: the four classic fossils' areas, drawn from the standard maps.

### Stage 4: the ocean floor and the water

Drain the ocean, the sea-level slider, glaciers and the ice-age view, rivers and drainage basins, climate zones.

- **Drain the ocean:** GEBCO's global bathymetry grid as shaded relief tiles (a coarse world set plus finer tiles when zoomed in, like the country maps' detail tiles); the water fades out over a couple of seconds. Check the size: it's the biggest data in the app.
- **Sea level:** the same grid gives the coast at any level (-130 m for the ice age, up to +70 m if all the ice melted), drawn as a contour.
- **Glaciers:** today's ice from Natural Earth (public domain); the Last Glacial Maximum ice sheets from published reconstructions (Dalton et al. 2020 for North America, DATED for Eurasia; check the licences), with the sea at -120 m.
- **Rivers and basins:** Natural Earth rivers (public domain) and HydroBASINS (check the licence) for the big basins.
- **Climate zones:** the Köppen map from Beck et al. 2018 (CC BY 4.0 expected), simplified to the 30 zones.

### Stage 5: Rewind to Pangea (the hardest)

- A time slider from today back to 200 million years ago (Pangea), with play/pause, like the Russia and US timelines.
- The continents (and, where possible, the plates, the fossils and the mountain ranges) move with the published plate reconstructions: GPlates and EarthByte (the Müller et al. model; CC BY expected). The rotations are worked out at build time into a few dozen time steps the app blends between, so the phone doesn't run the model.
- Key moments on the slider: Pangea (~200 Ma), the Atlantic opening, India hitting Asia, today; each with a short card.
- The fossil dots line up as the continents close (idea 15).

## Licences and credits

As for the country maps: each source's licence is recorded with its download, credited on the map where it needs it (the map credit), and anything share-alike is avoided unless the user approves it. Hand-drawn layers (currents, winds, fossils) record the references they were drawn from.

## Stage 1: done (2026-11-28), not committed until the user says so

**What's in it:** a third tab in the menu, **Earth** (its own panel and Start; the map's Globe / Flat choice under Options, as Learning mode). On the map: coasts only (country borders off, a checkbox to show them), a **Layers** button (top right) with a checkbox for each layer and four ready-made groups (Plates, Ring of Fire, Volcanoes, Oceans; each ticks exactly its layers). The layers chosen are remembered on the phone. Tap anything for its card (the Learning card); the tapped thing is highlighted. The back button closes the Layers panel, then the card.

| Layer | What's drawn | Its card |
| --- | --- | --- |
| Plates | the 52 PB2002 plates in 6 soft colours (neighbours never share one), names when there's room | name, kind, area, motion, neighbours, a note; More: its boundary lengths by type |
| Plate boundaries | every boundary: divergent (orange-red), convergent (blue), transform (green) | the two plates, the type, speed, length, average depth, ocean floor age (measured from PB2002's 5,824 steps) |
| Ridges & trenches | 42 named features, thicker, with names along the line (turned to follow it) | kind, plates, length, speed, deepest point, a note and facts |
| Volcanoes | 1,209 Holocene volcanoes as triangles (famous ones bigger); thinned to one per screen cell at world zoom (the famous, then the recently active, first); names zoomed in | type, country, height, last eruption, what it's known for; More: setting, rock, the Smithsonian's geological summary (loaded when the card opens, one small file per region) |
| Hotspots | 16 hotspots; the trails of Hawaii, Yellowstone, Réunion and Tristan dotted, with their ages (Ma) zoomed in | what it built, its trail, the oldest part |
| Ring of Fire | a soft orange band along the subduction zones round the Pacific (43,160 km in PB2002) | the story, its length, volcanoes and earthquakes |
| Seas & oceans | the names of 161 oceans, seas, gulfs and bays (fewer at world zoom; gulfs and bays once zoomed in) | kind, which ocean, area, deepest point (oceans) |

**Files:** `tools/fetch_earth.py` (downloads), `tools/earth_facts.py` (the hand-picked facts), `tools/build_earth.py` → `data/earth/` (2.2 MB, of which 1.2 MB is cached for offline use with the app; the volcano summaries are fetched when needed). `js/earth.js` (the layers, drawing, taps, cards, Layers panel); `js/mapview.js` has two hooks (draw the layers after the base map; Earth mode takes every tap). Credits: in the Layers panel and on the cards.

**Tests** (`_bench_earth.html`, git-ignored): the menu tab and Start; every plate and sea the right way round (the plates add up to exactly the whole sphere); taps on the globe and the flat map open the right card for a volcano (Etna, with its summary), a hotspot over a volcano (Hawaii), five named features, a plain boundary, the Ring of Fire, two seas, three plates, and nothing on empty sea; the Layers panel (a group, the borders checkbox, the back button); leaving Earth mode puts the map back (borders, markers, the Borders chip). Phone-width screenshots in light and dark. The earlier benches (menu, the four fixes, the back button) still pass.

### Decisions to check (stage 1)

1. **Seas come from Natural Earth's marine areas** (public domain), not Marine Regions' IHO areas as planned: smaller and simpler, with the same names for the main seas. The IHO set could replace it later.
2. **Ridges and trenches are picked out of PB2002** by plate pair, boundary type and a box (`tools/earth_facts.py`), not from GEBCO's undersea names: 42 named features, so each follows the plate boundary exactly. GEBCO's gazetteer could add the smaller ones later.
3. **The hand-written facts** (plate motions, trench depths, famous eruptions, hotspot trails' ages, the Ring of Fire's figures) are rounded, well-known figures from general reference knowledge; worth a read. Lengths, speeds, depths along boundaries and ocean floor ages are measured from PB2002.
4. **Plate kinds:** the 7 big plates are "major" and 13 named ones "minor" (the usual textbook lists); the rest are "minor" if over 1 million km², otherwise "microplate". The Africa plate's card says it's also called the Nubian plate.
5. **Ring of Fire:** the subduction zones touching a Pacific plate (Indonesia's Sunda Trench included, as most maps do; the Caribbean's, Scotia's and the Mediterranean's left out).
6. **Two famous volcanoes aren't in the Smithsonian's Holocene list** (it only has those active in the last 12,000 years): Kilimanjaro and Yellowstone. Yellowstone is on the map as a hotspot. Sakurajima and Parícutin are under their volcanic systems' names (Aira, Michoacán-Guanajuato).
7. **Subduction "teeth"** (the triangles on the overriding side of a trench, as in textbooks) aren't drawn yet: trenches are blue lines. They could come with a later stage.
8. **Country taps do nothing in Earth mode** (its layers take every tap); country borders are a checkbox in the Layers panel.

## Log

- 2026-11-28: stage 1 built and tested (see "Stage 1: done" above).
- 2026-11-28: plan written with the user (their list plus ideas 1–8 and 10–15; biomes left out; games later). The five questions answered the same day; `js/quakes-live.js` written and tested.
