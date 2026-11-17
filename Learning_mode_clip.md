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
| 9 | 12.5–13.5 s | **Tap Colorado** (decided 2026-11-17). It highlights and its state card appears. |
| 10 | 13.5–15.5 s | **Hold** on the state card. |
| 11 | 15.5–16.5 s | **Tap "‹ World map"** to go back. The card closes. |
| 12 | 16.5–19.5 s | **Smooth return to position 1.** The globe zooms out and turns back to Europe and Africa: the reverse of step 2. |
| 13 | 19.5–20.5 s | **Hold on position 1**, and the finger fades out. The last frame matches the first. |

**Going between the US map and the globe** (steps 8 and 11): the US map is flat and the world is a globe, so the switch is a change of view, not a zoom. Fade from one to the other over about 0.4 s, so it doesn't look like a cut.

## Where it goes in the menu (decided 2026-11-17)

- The clip sits on the **Learning mode tab of the New game menu**, in the space the Game tab uses for Find, Name, Region and Map (`#worldPanel` in `index.html`).
- This changes the tab: today, tapping "Learning mode" goes straight to the Learning globe. Instead it becomes a real tab: the clip **loops** in that space, with the menu's **Start** button underneath to open Learning mode.
- The real app keeps running behind the menu as normal. The clip is a video, not the live app, so it costs nothing while the menu is closed.

## Look

- **Size and shape:** match the space the clip replaces. The menu sheet is at most 440 px wide with 16 px padding, so the clip is about **408 px wide** on most phones. Measure the height of Find, Name, Region and Map on the phone (Game tab, with Find open and Region closed, the way it opens), and use that shape. The first guess is roughly **4:3 landscape** (about 408 × 306). Round it to a simple ratio so the box doesn't jump when the tab changes, and make the tab panel exactly that height (`aspect-ratio` in CSS, with the video set to `object-fit: cover`).
- **Recording size:** record at the same shape, but with a bigger page than the box, so the app has room: for example a **544 × 408** page at 2× pixel density (a **1088 × 816** video), shown at 408 px wide. The text in the clip then appears at three-quarters size, which should still be readable; test it, and if it's too small, use a smaller page (bigger text, less map).
- **Check the app's layout at that shape:** the Learning card is designed for a tall phone. In a short wide box it may cover most of the map. If so, the demo can place the card on one side, or zoom the map so the country stays visible above the card.
- **Loop** (decided): the clip loops forever while the tab is open. Position 1 at the start and end makes the loop seamless.
- **Pauses:** stop the video when the menu closes or another tab is picked, and when the phone asks for reduced motion (`prefers-reduced-motion`), show the still of position 1 with a play button instead.
- **Theme:** dark (the app's default on most phones), so it matches the splash.
- **Captions** (decided 2026-11-17: **test them**): short ones at the top, such as "Tap any country", "More facts", "Focus on a country", "Tap a state". The box is small, so keep them to three or four words, in a bar at the top that doesn't cover the map. Make a version with captions and one without, and the user picks after seeing both.
- No sound.

## Turning it into a video

Record the demo page at the clip's shape (see Look) with **Playwright** (headless Chrome, `recordVideo`), then convert with ffmpeg:

- `tools/record_clip.js`: opens `index.html?demo=learning` at the recording size (for example 544 × 408 at 2×), waits for the script to finish, saves the recording.
- Convert to **WebM** (for the app) and **MP4 (H.264)** (as a fallback, and for sharing), saved as `media/Learning_mode_clip.webm` and `.mp4`, plus a still of position 1 as the poster image. Add them to the offline list in `sw.js` and keep the WebM small (about 1 MB or less; the box is small, so this should be easy).
- Encode at 30 fps; if the globe looks jumpy, record at 60 fps and drop to 30.
- If the recording stutters on heavy frames, use a fixed clock instead: the script steps time forward one frame at a time and takes a screenshot of each, then ffmpeg joins them. It's slower to make but always smooth.

## Build order

1. `js/tutorial.js` with the finger, tap ripple, captions and storyboard, behind `?demo=learning`.
2. Measure the menu space on the phone and set the recording shape.
3. Check it in the browser at that shape: smoothness, timing, readable cards, card not covering the map.
4. `tools/record_clip.js` + ffmpeg: record with and without captions, save to `media/`.
5. Turn the Learning mode tab into a real tab with the looping clip and the Start button.
6. The user picks captions or no captions.

## More clips (possibly, 2026-11-17)

The same method can make a clip for each game, in the same place on the Game tab (for example the clip for the selected game playing above the Start button), named the same way: `Find_country_clip`, `Name_country_clip`, `Find_flag_clip` and so on. Build `js/tutorial.js` so each clip is just a list of steps (move the map, tap here, wait, show a caption), and new clips are a new list, not new code.

## Open questions for the user

None at the moment (all answered 2026-11-17). Captions are decided after the test.
