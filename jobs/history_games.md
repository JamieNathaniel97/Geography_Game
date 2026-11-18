# Job: History games (H1 people, H2 battles, H3 shipwrecks)

Building the three History games planned in [History_games.md](../History_games.md) (all its questions answered 2026-11-17; the plan wins where this file is shorter). Added 2026-11-17. **The shared engine is built (2026-11-18):** js/history.js: the setup (More games → History → a topic: game, kind, era, region, rounds, answer by), distance scoring (checked against the plan's table), Hint (zooms in and halves the round), the "Where?" taps (H1: green then red), the answer symbols (baby, skull, swords, anchor, castle, wreck) with lines and distances, the "Which one?" answers (typing or 4 choices of the same kind and era), the card, Give up, the end summary and personal bests. The map shows no country circles in these games (`main.noMarkers`), and the zoom is held still except for Hint. **The data is in (2026-11-18 evening), checked by hand:**
- **Shipwrecks:** 58 (`data/wrecks.json`). Wikidata had no wreck position for 36 of the hand-picked ones, so `tools/wrecks_extra.py` `HAND` writes them from published accounts (positions approximate, to a few km). Dropped: the Mary Celeste (doubtful identification), the ARA General Belgrano and SS Arctic (never found), the San José (position secret), the Doña Paz (not surveyed), and the old USS Texas (a target hulk). Lives lost and the year found were filled in for the famous ones (`FIXES`). Raised wrecks say where they are now; 14 war graves are marked.
- **Battles:** 214 (`data/battles.json`). The 18 big campaigns have hand-drawn areas (`tools/battle_areas.geojson`, approximate: worth a check). 25 land battles that had been counted as naval were corrected (`battles_extra.NOT_NAVAL`); Black January dropped (a massacre, not a battle); 9 hand-picked battles added by hand (`HAND`). **Winners are missing** for all (Wikidata rarely has them): the card shows the sides where known.
- **People:** 1,074 (`data/people.json`), 245 with a free portrait (`data/people/`; a few failed when Commons limited requests: re-run `python tools/build_people.py 100 --images` to fill them). 16 hand-picked people added by hand (Marie Curie, Frida Kahlo…); Mansa Musa and Nzinga left out (birthplaces uncertain). The kind is now taken from each person's description (`people_extra.kind_from_desc`): Wikidata's occupations had Verdi as a leader and actors as composers. Still to check: 56 people with several birth or death places, and some places that are a street or hospital rather than a town (Audrey Hepburn's "Rue Keyenveld").

## Where they go in the menu (changed 2026-11-17)

The plan's "Game | History | Learning mode" tabs are **replaced** by the user's newer instruction: a **"More games"** button on the New game menu opens a menu with **History** and **Misc** columns ([README.md](README.md), "Coming soon"). That menu change waits for the user's go-ahead; until each game is built, it shows there as "soon".

## Shared pieces (build once, used by all three)

- **Distance scoring:** each round is worth up to 100: `score = 100 − 99 × log(d / 20) / log(1000)`, rounded (100 within 20 km, 1 at 20,000 km). A 10-round game is out of 1,000. Personal bests use the total for 10, 20 and 50 rounds, and the average per round for **Marathon** (the whole chosen set).
- **Hint button** (H1a, H2a, H3a): no zooming in otherwise; Hint zooms to the area (the real place inside a generous, slightly random margin, at least about 1,500 km across) and **halves** the round's score; the round shows a "hint" mark.
- **The "Which one?" games** (H1b, H2b, H3b): answer by typing (forgiving matching) or from **4 choices**, a setting in Options; the choices are of the same kind and era.
- **Symbols** as small SVG icons (not emoji): baby and skull (H1), crossed swords, anchor for naval battles, castle for sieges (H2), a sunken ship (H3).
- **Choosing:** kind, era, region, length (10, 20, 50, Marathon), before each game, like the Region box.
- Taps on the sea count. Back and forward arrows, Give up, the timer, stats and personal bests as in the other games. End-of-game pop-up: total, average per round, average distance, best and worst guesses.
- Smooth zooms (turn and zoom together), like the Learning mode clip.

## H1: Historical figures

1. **Data:** `python tools/build_people.py 100 --images` (Wikidata, CC0; the fame cut-off is the number of Wikipedia languages; aim for about 500–1,500 people) → `data/people.json`, plus free-licence portraits (240 px WebP, credit and licence kept) in `data/people/`, loaded only when a card opens. The 174 hand-picked people (`tools/people_extra.py`) are always in.
2. **Check by hand** (the plan asks for this before building): fix the titles the script can't find; people with several birth or death places; places that are a country or region rather than a town; places with no modern country; the spread by region, era and kind (add to the hand-picked list where it's thin). Fixes go in the script's `FIXES`. List anything doubtful for the user.
3. **H1a, "Where were they born and where did they die?":** two taps (green dot: birth guess; red dot: death guess), then the baby and skull symbols at the real places with names and years, lines and distances; the round scores the average of the two places.
4. **H1b, "Who is it?":** the symbols shown, the map fits both; name the person (typing or 4 choices); the card with portrait and credit.
5. Kinds: leaders, scientists and inventors, artists and architects, writers and poets, composers and musicians, philosophers, explorers. Eras: ancient, medieval, early modern, 1800s, 1900s and later.

## H2: Famous battles

1. **Data:** `python tools/build_battles.py 40` → `data/battles.json` (name, years, position, country, naval or siege, war, sides and winners, fame). Fix the hand-picked titles it can't find.
2. **Draw the big-area shapes** (a build task: H2 isn't finished until none are missing): one simplified shape per battle in `AREAS` (`tools/battles_extra.py`), in `tools/battle_areas.geojson`, from historical maps of where the fighting happened (the Battle of Britain, Gallipoli, Normandy, Kursk, Midway and others). Re-run the script until it lists none missing. Mark the drawn shapes for the user to check.
3. **Sides and winners:** check them for the hand-picked battles; fill gaps in `FIXES`.
4. **H2a, "Where was it fought?":** one tap, then the symbol (or the highlighted area) with the distance; inside an area scores 100, outside uses the distance to its nearest edge.
5. **H2b, "Which battle was it?":** the symbol with its year ("⚔ 1815"); name it (typing or 4 choices).
6. Filters: kind (land, naval, siege), era, region, war; battles up to 1993 (the plan's cut-off).

## H3: Famous shipwrecks

1. **Data:** `python tools/build_wrecks.py 15` → `data/wrecks.json` (name, description, year sunk, wreck position, country, lives lost, year found, sunk in war, raised). The 53 hand-picked wrecks (`tools/wrecks_extra.py`, including the Edmund Fitzgerald and recent wrecks such as the Estonia and the Kursk) are always in.
2. **Check by hand:** only wrecks with a known, found position (drop any whose position is just where the ship was lost, or its home port); set `raised` for the Vasa, the Mary Rose, the Kursk, the Costa Concordia, the Sewol and others, so the card says where they are now; mark war graves.
3. **H3a, "Where did it sink?":** "RMS Titanic · 1912", one tap, then the sunken-ship symbol with the place, year and distance.
4. **H3b, "Which ship was it?":** the symbol and year; name the ship (typing or 4 choices; prefixes such as RMS, HMS, SS, USS, MV optional).
5. The card: name, year, description, what sank it, **lives lost** (always shown where known; "no lives lost" where none were), when the wreck was found, raised or not, war grave (said plainly and respectfully). Recent disasters: plain facts only.
6. Filters: kind (sunk in war, sunk in peace), era, region.

## Tests (all must pass)

- Each game plays a full 10-round game and Marathon; the scores match the formula (check a few distances by hand); Hint halves the round.
- Typing accepts the forgiving forms (surnames, short names, ship prefixes optional); the 4 choices are of the same kind and era.
- Every symbol and area draws; the cards show their facts, portraits and credits, in light and dark themes.
- The country games, Learning mode and the timelines still work; no script errors.
- Credit Wikidata (and each portrait's licence) in the app.

Push only when the user says so, or as an overnight job list explicitly allows.
