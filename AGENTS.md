# Backlot Loader: notes for coding agents

- The game is one web app: `index.html` (all code), `vendor/` (three.js r160 and fonts, kept local so it runs offline) and `assets/models/`. There is no build step for the web version.
- The iOS app in `ios/` is only a full-screen WKWebView shell that bundles those same files (copied in by `ios/copy-web.sh` on every build). Never fork game code into Swift: every gameplay, graphics or UI change goes into `index.html` so it lands in the web version and the iOS app together.
- When you change something, keep both in mind:
  - Touch and phone play: the virtual joysticks, `MOBILE` (lighter settings on phones and tablets; `?mobile=1` / `?mobile=0` force it) and app mode (`html.app`, set by the iOS app via `window.__nativeApp`, by home-screen launch or `?app`).
  - New files the game loads must sit under `index.html`, `vendor/` or `assets/models/`, or be added to `ios/copy-web.sh`; the app serves nothing else. Don't load anything from the network: the app must work offline.
  - Only the native shell's own behaviour (scrolling, zoom, status bar, audio session, file serving) belongs in Swift. Edit `ios/project.yml`, never the generated `.xcodeproj` or `Info.plist`.
- Saved games: `makeSave()` / `stateCore()` in `boot()` decide what is saved (IndexedDB via `SaveStore`, local to the device, no server, no import/export) and `start()` restores it. When you add state that should survive a Continue, add it to both. Settings live in localStorage (`loadSettings` / `saveSettings`), and so does progression shared by all maps (`loadProfile` / `saveProfile`: account, garage upgrades in `UPGRADES` read through `UP(id)` at boot, tips seen). Write the profile with a fresh `loadProfile()` first, never a stale copy.
- Keep the game screen free of instructions: explanations belong on the start screen's Controls panel or in the one-at-a-time tips (`TIPS` in `boot()`, with key / touch / pad wording); in-game toasts are for short feedback.
- Where things stand and what is next: HANDOFF.md.
- Testing: serve the folder (`python3 -m http.server`) and open `index.html`; add `?fps` for a frame-rate readout.
