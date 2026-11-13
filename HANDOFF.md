# Backlot Loader: handoff

Where the project stands and what comes next. Last updated after commit `d5e99df`.
For how to play see [README.md](README.md); the coding rules for agents are in [AGENTS.md](AGENTS.md).

## What it is

A low-poly 3D earthmoving and snow-plowing game in one web app, also packaged as an iOS app.

- **One codebase.** All game code is in `index.html` (about 7,500 lines: HTML, CSS and one big
  `<script>`). three.js r160 and the fonts are vendored in `vendor/`. The vehicle models are
  in `assets/models/`. There is no build step for the web.
- **iOS** (`ios/`) is a thin WKWebView shell that bundles those same files. Game code never goes into Swift.
- **Repo:** `git@github.com:zooper/tractor-game.git`, branch `main`. Commits use the author
  Tomas Jonsson <jonsson@spotify.com>, which is configured in the repo on the dev server.

## The three maps

| Map | Kind | Highlights |
|---|---|---|
| **Gravel pit** (Björkåsens grustag) | Business | Customers in tippers or a car and trailer order tonnes of a product or items. The loader and excavator do the work. Two plants: the **crusher** (bärlager, makadam 8–16) and the **screen** (sand, stenmjöl, makadam 16–32), both fed naturgrus dug from the pit face. Each morning you choose an open day or a production day; the evening is free, then End day. A stock card, a post-it of waiting customers, weather, and boulders from the face. |
| **Paulus Hook** (Jersey City) | Snow | Real OpenStreetMap streets, buildings, shops and shoreline. Light rail, traffic with signals, Liberty Towers and the Colgate Clock modelled by hand. |
| **Kvarnby** | Snow | A made-up Swedish village laid out in `villageData()`, in the same shape as the OSM data. Houses with driveways (a plogvall across one triggers a complaint), a church with a clock, a mill pond, an ice rink, a level crossing with barriers, snow poles. |

The snow maps share: plow, bucket and snow blower on the loader, a salt truck, a sidewalk blower,
a dump truck to the snow tip, and **shifts** (22:00–06:00 with snow that keeps falling, a summary
and pay at 06:00), or **free plow** as a setting.

## Systems

- **Start screen** (`showMenu`, outside `boot`): map cards, Continue / New game, Garage,
  Settings, Controls (with a live controller check). It works with touch, mouse and controller
  (spatial d-pad navigation).
- **Saves** (`SaveStore`, IndexedDB, one per map, only on the device): `makeSave()` /
  `stateCore()` decide what is saved and `start()` restores it. Autosave runs every 45 s, on
  hide, and on Menu. A save keeps its own grid size `N`. Pit saves carry `pitLayout: 2`; older
  pit saves start fresh.
- **Settings** (`loadSettings`, localStorage): graphics, performance mode, sound, day and
  shift length (pace), shifts or free plow, free-plow start time, tips.
- **Profile** (`loadProfile`, localStorage, shared by all maps): the account in kr, garage
  upgrades (`UPGRADES`, read through `UP(id)` at boot), and which tips have been seen. Money
  comes from shift pay and 30% of each pit day's takings.
- **Tips** (`TIPS` in `boot`): one line at a time, worded for keys, touch or controller, each
  shown once.
- **Mobile mode** (`MOBILE`): a coarser grid (400 / 360 instead of 560 / 520), cheaper
  graphics, fewer trees and lights, no mirrors. Auto on touch devices; `?mobile=1` / `?mobile=0`
  force it.
- **Touch:** two virtual joysticks (`stick`) with a response curve, a DIG mode for the
  excavator, pinch zoom, and app mode (`html.app`) for the iOS app or a home-screen launch.
- **Controllers:** the Gamepad API in a Farming Simulator–style layout (`padInput`). Raw,
  non-standard Xbox layouts are translated (`standardize`). The browser only exposes
  controllers on https or localhost.
- **Haptics:** `haptic()` posts to the iOS app's `haptic` message handler, or uses
  `navigator.vibrate` elsewhere.

## Running and testing

- **Serve the folder:** `python3 -m http.server`, or `tools/serve-https.py` for https with a
  self-signed certificate. Add `?fps` for a frame-rate readout.
- **On the dev server** (galaxy), two plain http servers run on port 8000, bound to
  192.168.0.21 and 192.168.5.21. Chrome there did not show the Xbox pad even over https;
  Safari does.
- **Testing so far** has been in headless Chromium through Playwright, with a venv in
  `/tmp/pwenv`, so it would need recreating:
  - The Chromium software renderer runs at 1–5 fps. Drive the simulation by calling `tick()`
    in a loop from a debug hook, not in real time.
  - The debug hooks (`window.__dbg`, `__camHold`) were added to a throwaway copy in `/tmp`,
    never to the repo.
  - Controllers were tested by overriding `navigator.getGamepads` with a fake pad.
  - Shots of the game canvas use `preserveDrawingBuffer` and `toDataURL`.
- **Nothing has been tested on a real device or GPU,** except Tomas trying the web version on
  his iPhone and in Safari on desktop.

## iOS app status

Set up, never built. Tomas has a Mac with Xcode and a developer account. To build:

```sh
git clone git@github.com:zooper/tractor-game.git && cd tractor-game/ios
brew install xcodegen && xcodegen generate && open BacklotLoader.xcodeproj
```

Then set the team and bundle ID in Signing & Capabilities and run on the phone.
`xcodegen generate` overwrites them, so they should go into `ios/project.yml`: `DEVELOPMENT_TEAM`
and `PRODUCT_BUNDLE_IDENTIFIER` (placeholder `com.example.backlotloader`). We are waiting for
Tomas's Team ID and chosen bundle ID.

Unverified on a device: that it builds first time, IndexedDB saves on the `app://` scheme,
controllers in WKWebView, haptics, audio, and performance compared with Safari.

## Known limitations

- **Balance is guessed:** snowfall rate, shift pay, upgrade prices, pit profit share and pile
  sizes have not been play-tested. A good pit day probably pays more than a shift.
- **Not saved:** traffic, the train, the pit's waiting customers and items, tyre tracks and salt
  on the road start fresh on Continue. The pit loader starts with the bucket on.
- **Plants** accept anything tipped in and split it in fixed shares; you can't choose the output.
- **Naturgrus customers** count the pit face as stock.
- **Kvarnby's rink** fills with snow again during shifts, but only celebrates once.
- **Phone layout** of the stock card may overlap the right joystick in portrait; it can be hidden.
- **Saving on the iPhone web version:** Safari may clear site storage after 7 days without use,
  unless the game is added to the Home Screen.
- **Size:** `index.html` is large; most of the code lives inside `boot()`.

## Next plans

1. **First iOS build on Tomas's Mac.** Fix build errors, put the team and bundle ID in
   `project.yml`, then check saves, controllers, haptics, audio and performance in the app.
2. **Play-test and tune balance:** snowfall, shift pay, garage prices, the pit day length and
   customer rate, pile sizes and plant output rates.
3. **Gravel pit depth:** let a plant's program be chosen, turn the boulder trade and big-bag
   filling into jobs, and possibly customers who give up after a long wait (wait times were
   removed from the post-it because the game clock made them look odd).
4. **Snow shifts:** events (a bus stuck, a complaint call, an emergency route), the rink
   refilling, and a priority-street overlay on the map.
5. **Feel:** joystick and camera tuning on a phone, and sound polish (scrape by snow depth).
6. **App Store:** a real icon and screenshots, a privacy statement (no data leaves the device),
   TestFlight.
7. **Later:** more maps, and splitting `index.html` into modules if it keeps growing (still
   with no build step, for the iOS bundle).

## Conventions

These are also in AGENTS.md.

- Keep game code in `index.html` so the web and iOS versions stay the same game. Only native
  shell behaviour goes in Swift.
- Any new file the game loads must be under `index.html`, `vendor/` or `assets/models/`, or
  be added to `ios/copy-web.sh`. Nothing may load from the network.
- State that should survive Continue goes in both `stateCore()` / `makeSave()` and `start()`.
- No instructions on the game screen: explanations go in Controls or in the tips.
- Comments explain the why in plain sentences, and commit messages are descriptive.
