# Overnight run (night of 2026-11-18)

Started with `/loop work through jobs/OVERNIGHT.md`. Work down the queue in order; each item ends with its tests passing, the preview updated, and its entry in [OVERNIGHT_REVIEW.md](OVERNIGHT_REVIEW.md). When the queue is done (or nothing more can be done without the user), stop the loop.

## Rules (decided by the user, 2026-11-18)

1. **Don't push, and don't commit.** Leave every change in the working tree for the user to review in the morning. (Don't pull either: another session may push plans; note any new remote commits in the review, without merging them.)
2. **Keep the preview updated:** after each finished item, `python tools/make_preview.py <scratchpad>/preview` and republish the preview artifact (https://claude.ai/artifact/FozfGxc5xd1StWG7MZaAnf), uploading new data and media files with it.
3. **Make judgement calls.** When a plan doesn't answer something, choose what fits the app and the existing countries best, carry on, and record the choice in the review doc under that item ("Decisions to check"), with what the alternative was.
4. **Missing data doesn't stop a build.** Build everything that has its data; leave the missing part ready to drop in (the code path written, the data file absent or empty, the part sitting out the affected game), and list it under "Waiting for data" in the review doc and in [download_new_countries.md](download_new_countries.md). Known now: Colima's coat of arms (Mexico); the official census totals (check the parts against the census table in the downloaded list articles instead, and note the source); Spain's languages layer (no data source yet).
5. **Tests are the bar.** Each build follows the checklist in [build_countries.md](build_countries.md) and passes its tests (headless Chrome bench, phone size 390×844, light and dark). If a test can't be made to pass with reasonable effort, record it under "Problems" in the review and move on; don't leave the app broken: what was working before (the world map, every built country, the US and Russia timelines, the menu, Learning mode, the clip) must still work after each item.
6. **Stay in scope:** only the queue below. Not tonight: the History games, the airport game (shelved), Nigeria's seal games (shelved), timelines (morning agenda), Italy's provinces (morning agenda), Vatican City and San Marino, redoing the built maps with high-resolution coasts.
7. Housekeeping: kill only headless Chrome processes (`--headless` in the command line) and the test servers you start; temporary bench files (`_bench*`, `_shot*`) go when done.

## Queue

**Done, 2026-11-18 (about 03:40): all ten items. See [OVERNIGHT_REVIEW.md](OVERNIGHT_REVIEW.md).**

1. **Plans:** write `Germany_plan.md`, `Japan_plan.md`, `France_plan.md`, `Italy_plan.md`, `Spain_plan.md`, `Nigeria_plan.md`, `Argentina_plan.md` from [build_countries.md](build_countries.md) (decisions, card facts, standards), in the style of [Mexico_plan.md](../Mexico_plan.md) and [Russia_plan.md](../Russia_plan.md). Timelines: "to discuss" (morning agenda). Italy's provinces: "to confirm".
2. **Mexico** (build job "Mexico (ready)"), including the **detail-level coast machinery** (tiles, loader, switching at the zoom threshold) that every later build reuses, and its Indigenous layer. Its timeline was decided in its plan (expansion and decline, 1821–1974): build it if time allows after the games, cards and layer; otherwise list it for the morning.
3. **Brazil** (build job "Brazil (ready)"), with the island ovals and the FUNAI layer; its timeline likewise.
4. **Germany**, 5. **Japan** (with the Japanese font subset), 6. **France**, 7. **Italy** (regions; Vatican City and San Marino as coloured circles, their own Focus maps not tonight), 8. **Spain** (communities and provinces as two sets, the Canaries inset; the languages layer waits for data), 9. **Nigeria** (no games 5 and 6), 10. **Argentina** (no Falklands). No timelines for these.

After each item: update the review doc, update the job files (mark what's built), republish the preview, then take the next item.
