# Learning_mode_clip – Instructions

A short tutorial clip (about 20 seconds) that shows how Learning mode works, by playing the real app with a pretend finger. Drafted 2026-11-17. Nothing is built yet. **Open questions** are at the end.

## The idea

The clip uses **the app itself**, not a separate drawing: a script drives the real map, card and buttons, and a pretend finger shows each tap. That way the clip always matches the app, and it can be re-recorded whenever the app changes.

- A demo script, `js/tutorial.js`, started with a URL flag: `index.html?demo=learning`. With the flag, the splash is skipped, the normal controls ignore real touches, and the script plays the storyboard below.
- **The finger:** a semi-transparent round fingertip (about 44 px), with a short ripple ring on each tap, and a slight press (shrink) as it taps. It glides between taps on a gentle curve, never jumping.
- Every tap calls the same code a real tap would (`showLearnCard`, the "More facts" button, `focusBtn`, and so on), so what you see is exactly what a user gets.
- Motion is eased (ease-in-out) throughout; no sudden cuts.

## Position 1 (start and end)

The same view the splash ends on: the **3D globe centred over Europe and Africa** (`rotate([-18, -22])` in `js/splash.js`, so about 18°E, 22°N), at the splash's globe size, with borders on and the normal Learning-mode colours. Starting and ending here lets the clip loop cleanly, and it links the tutorial to the splash.

## Storyboard

Timings are a guide; adjust them so it feels calm, not rushed.

| # | Time | What happens |
| --- | --- | --- |
| 1 | 0.0–1.0 s | **Hold on position 1.** The finger fades in near the bottom of the screen. |
| 2 | 1.0–4.0 s | **Smooth zoom to the US.** The globe turns west and tilts north while zooming in, ending with the USA filling most of the screen. One continuous move: turn and zoom together (d3 `interpolate` on rotation and scale), not one after the other. |
| 3 | 4.0–5.0 s | **Tap the USA.** The finger glides to the middle of the country (around Kansas) and taps. The USA highlights yellow and the Learning card slides up. |
| 4 | 5.0–7.0 s | **Hold**, so the viewer can read the name, capital, flag and continent. |
| 5 | 7.0–8.0 s | **Tap "More facts".** The card expands to show People, Land, and History and status. |
| 6 | 8.0–10.0 s | **Hold**, then scroll the card gently a little if the facts are taller than the screen. |
| 7 | 10.0–11.0 s | **Tap "Fewer facts".** The card collapses back. |
| 8 | 11.0–12.5 s | **Tap "Focus on The U.S. ›"** above the card. The map changes to the US states map (the normal Focus transition). |
| 9 | 12.5–13.5 s | **Tap a state** (see open question 2). It highlights and its state card appears. |
| 10 | 13.5–15.5 s | **Hold** on the state card. |
| 11 | 15.5–16.5 s | **Tap "‹ World map"** to go back. The card closes. |
| 12 | 16.5–19.5 s | **Smooth return to position 1.** The globe zooms out and turns back to Europe and Africa: the reverse of step 2. |
| 13 | 19.5–20.5 s | **Hold on position 1**, and the finger fades out. The last frame matches the first. |

**Going between the US map and the globe** (steps 8 and 11): the US map is flat and the world is a globe, so the switch is a change of view, not a zoom. Fade from one to the other over about 0.4 s, so it doesn't look like a cut.

## Look

- **Screen size:** a phone in portrait, 1080 × 1920 (9:16).
- **Theme:** dark (the app's default on most phones), so it matches the splash.
- **Captions** (open question 3): short ones at the top, such as "Tap any country", "More facts", "Focus on a country", "Tap a state".
- No sound.

## Turning it into a video

Record the demo page at phone size with **Playwright** (headless Chrome, `recordVideo`), then convert with ffmpeg:

- `tools/record_clip.js`: opens `index.html?demo=learning` at 1080 × 1920, waits for the script to finish, saves the recording.
- Convert to **MP4 (H.264)** for sharing and **WebM** for the web, and save as `media/Learning_mode_clip.mp4` and `.webm`. Also save a still of position 1 as a poster image.
- Encode at 30 fps; if the globe looks jumpy, record at 60 fps and drop to 30.
- If the recording stutters on heavy frames, use a fixed clock instead: the script steps time forward one frame at a time and takes a screenshot of each, then ffmpeg joins them. It's slower to make but always smooth.

## Where it's used (open question 1)

- In the app: a "How to play" page (already on PLAN.md's "Polish for later" list) or a "Watch how" link on the Learning mode tab, playing the WebM. If it's bundled in the app, add it to the offline list in `sw.js` and keep it small (under about 2 MB).
- Outside the app: the MP4 for sharing, the README or the GitHub Pages page.

## Build order

1. `js/tutorial.js` with the finger, tap ripple and storyboard, behind `?demo=learning`.
2. Check it on a phone in the browser: smoothness, timing, readable cards.
3. `tools/record_clip.js` + ffmpeg, then save to `media/`.
4. Hook it into the app, if chosen.

## Open questions for the user

1. **Where will the clip be shown?** In the app (a How to play page, or a link on the Learning mode tab), as a video file for sharing, or both?
2. **Which state** gets tapped? Suggestion: **Texas** (big, easy to see, well known) or **Colorado** (a neat rectangle in the middle).
3. **Captions:** short text captions at the top, or no words at all?
4. **Loop:** should it loop forever when shown in the app, or play once?
5. Later clips: the same method could make one for each game (for example "Find_country_clip"). Want those too?
