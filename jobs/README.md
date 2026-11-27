# Jobs

Work queued for Gaia Quest, one file per job, in the order to do them. Each file says what's done and what's next.

1. [download_new_countries.md](download_new_countries.md): the data for the new country maps (main downloads done; the extra fact sources and census totals still to fetch).
2. [build_countries.md](build_countries.md): building Mexico and Brazil (ready), then Germany, Japan, France, Italy, Spain, Nigeria and Argentina; the checklist every build follows, each country's decisions, and its card facts.
3. [history_games.md](history_games.md): the History games H1 (historical figures), H2 (famous battles, including drawing the big-area shapes) and H3 (famous shipwrecks); their plan is answered.
4. [misc_games.md](misc_games.md): the airport codes games (idea_01). **Shelved (2026-11-17): don't build anything yet**; its questions are on the morning agenda.

Push only when the user says so, or as an overnight job list explicitly allows.

**Done 2026-11-26:** [overnight_v2.md](overnight_v2.md) (Austria, Czechia, Poland, the Netherlands, Belgium), with its decisions to check at the end (reviewed with the user and pushed 2026-11-27, 27fce79). **Also done 2026-11-26:** [overnight_v3.md](overnight_v3.md). Next batch: [overnight_v4.md](overnight_v4.md) (start only when the user says so).

**Overnight run:** [OVERNIGHT.md](OVERNIGHT.md) (the queue and rules: no push, no commit, judgement calls allowed, missing data doesn't block a build) and [OVERNIGHT_REVIEW.md](OVERNIGHT_REVIEW.md) (the report for the morning).

**Done 2026-11-17 (in the preview):** a New game menu change, plus a **"?" help button** next to the cog (a placeholder: "Help is coming soon"; the help function comes later). The Globe / Flat map choice becomes a **small switch toggle on the left**; on the right, a **"More games"** button opens a menu with two columns: **History** (the History games H1 people, H2 battles, H3 shipwrecks, each marked "soon" for now; [History_games.md](../History_games.md)) and **Misc** (the airport codes game, "soon"; [Misc_games.md](../Misc_games.md)). Also add the **upcoming countries** to the Countries list as "soon" (Germany, Japan, France, Italy, Spain, Nigeria, Argentina, next to Mexico and Brazil).

## Future improvements (not scheduled)

- **Shrink Mexico's coats of arms** (data/flags/mx/, 4.3 MB: about 140 KB each); the other flag folders could get the same treatment.
- **A whole-code efficiency review by Fable** (claude-fable-5-2): read the whole codebase (js/, tools/, sw.js) and make it leaner and faster, without changing what the app does.
- **Timelines:** discussed later (Germany, Japan, Nigeria, Spain, Argentina, Mexico).

## Morning agenda (2026-11-18)

1. **Review the overnight work** ([OVERNIGHT_REVIEW.md](OVERNIGHT_REVIEW.md)), then commit and push what's approved.
2. **Timelines** (next on the list after the review):
   - **Germany:** the unification of the German-speaking states (Prussia and the others, to the German Empire in 1871); then **zoom out** for Nazi Germany's expansion and collapse; then the division (**East red, West blue**) and reunification in 1990.
   - **Japan:** **zoom out** for the empire's expansion and collapse, ending with **the atomic bombs** (a radioactive symbol on Hiroshima and Nagasaki) and **the surrender** (a white flag), then the post-war **tech boom**.
   - **Spain, Nigeria, Argentina:** to discuss (Nigeria's state splits 1967–1996 is the idea).
   - France (Napoleonic) and Italy: shelved for now.
3. **Italy:** the 107 provinces as a second set, yes or no?
4. **Airport codes game** (shelved until then; [misc_games.md](misc_games.md)): which airport sets; Name games one prompt at a time, Sporcle-style or both; city codes (LON, NYC, TYO); Learning mode for airports now or later; close airports as numbered bubbles or separating circles.
