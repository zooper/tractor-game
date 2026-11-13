# Backlot Loader

A low-poly 3D earthmoving and snow-plowing sandbox that runs in the browser. Open `index.html` in a modern browser, or serve the folder (`python3 -m http.server`) to also get the vehicle models. three.js (r160) and the fonts are kept in `vendor/`, so it runs offline; a page opened straight from the file system still loads three.js from jsDelivr, since browsers won't import local modules from `file://`. The same game also ships as an iOS app (see below).

## Jobs

- **Gravel pit · Grustag**: a made-up Swedish gravel pit. Each morning you decide: **open the gate** (07:00–16:00, with a morning rush) or take a **production day** with the gate shut. Up to three customers at a time (tippers of three sizes, or a car and trailer) wait, as long as it takes, at the pile they want: load the right gravel to the right weight, or boulders and big bags from the yard with the pallet forks. Swap the bucket, a big light-material bucket and the forks at the tool rack (B). **Restocking**: dig naturgrus out of the pit face with the excavator and tip it into one of the two plants. The **crusher** (south) makes bärlager 0–32 and makadam 8–16, the **screen** (west) sand 0–8, stenmjöl 0–4 and makadam 16–32, each conveyor building its product's pile; the naturgrus pile by the face is heaped straight from the face. Digging the face turns up boulders now and then, for the forks to take to the stone yard; big bags are delivered overnight. After the last customer leaves, the evening is yours to tidy up and crush; **End day** (or H) brings the day's summary with the stock in every pile, and it comes by itself at 22:00. Weather drifts from clear to rain and snow showers; wet gravel weighs more, trucks slow down in it and for spilled gravel on the haul roads.
- **Snow day · Paulus Hook, Jersey City**: plow the real streets around Liberty Towers. Streets, buildings, the Hudson-Bergen Light Rail and the neighbourhood's shops, cafés and restaurants come from OpenStreetMap; each shop gets a signed, lit storefront with a snowy awning on its real building. The shoreline (the Hudson, the Little Basin and the Morris Canal Basin) follows the OSM coastline, and the Colgate Clock stands on the point keeping real local time. Loader with plow blade, bucket or a 2.9 m snow-blower attachment (J / L swing the chute), a salt spreader truck, a sidewalk snow blower (J / L swing its chute), a snow dump truck, parked cars, moving traffic that stops at working traffic lights, lane markings and zebra crossings that show as you plow down to the pavement, streetlights and day/dusk/night. Liberty Towers is modelled by hand: curved glass between the towers, sawtooth tan masonry outside, the podium with shops, garage and pool deck, and the lobby under its canopy on Morris Street.

- **Snow day · Kvarnby**: a made-up Swedish village, laid out by hand in code. Red, yellow and white wooden houses with snowy gable roofs and smoking chimneys line Storgatan and the lanes round them, each with its own driveway and mailbox. There is a white church with a clock in its tower (real local time) and a churchyard, a square with a lit Christmas tree, the village shop and its car park, a fire station, a school, a gas station, and a red mill with a turning waterwheel on Kvarndammen, the pond you can push snow into. Plow the streets, but don't leave a plogvall (windrow) across anyone's driveway: the family behind it will complain, and the HUD counts the driveways you've cleared. Clear the ice rink by the school for the kids. A red regional train stops at the station, and the barriers come down on Stationsvägen when one is coming. Orange snow poles mark the road edges under the snow. The machines start in the municipal depot, and the dump truck hauls loads out to the snow tip south of the village.

## Shifts, money and the garage

The snow maps run in **shifts** (the default; Settings can switch to **free plow**). A shift goes from 22:00 to 06:00, about 16 real minutes at the normal length, and snow keeps falling the whole time, sometimes light, sometimes heavy, so plowed streets fill in again. The HUD shows the clock, how hard it is snowing and how much of the **main streets** is passable (Storgatan, Kyrkvägen and Stationsvägen in Kvarnby; Hudson, Grand, Montgomery, Greene and Christopher Columbus in Paulus Hook). At 06:00 the shift ends with a summary and up to three stars: pay comes from how open the main streets were on average, how open all the streets were and the truckloads hauled, less 400 kr for each plogvall. The gravel pit pays 30% of each day's takings as profit.

Both go into one **account**, shared by every map, which buys upgrades in the **Garage** on the start screen: plow wings (a 4.3 m blade), a high-volume bucket, an engine tune, a big salt tank, a bigger dump body and LED work lights. Upgrades fit from the next time a map starts.

New players get **tips**: one short line at a time, worded for keys, touch or a controller, each gone once you've done it. Settings turns them off or shows them again. Bumps, a full truck, a plogvall and the end of a shift give a short buzz: native haptics in the iOS app, the vibration API on Android.

## Start screen and saving

The game opens on a start screen: pick a map, then **New game**, or **Continue** when that map has a saved game (the card shows when it was saved and how far along it is). **Garage** spends the account on upgrades; **Settings** has graphics (auto / high / low), performance mode (auto / lighter / full), sound, day and shift length (short / normal / long: about 9, 18 or 36 real minutes), shifts or free plow for the snow maps, the time of day free plow starts at, and tips on / off; **Controls** lists the keys, touch and controller controls. The game screen itself carries no instructions; **Menu** (bottom right) saves and goes back to the start screen.

Progress saves automatically, one save per map: every 45 seconds of play, when the page or app goes to the background, and on the way back to the menu. Saves stay on the device, in the browser's (or the iOS app's) IndexedDB; nothing is sent anywhere, and there is no import or export. A saved game keeps the snow or dirt grid exactly as it was, the machines' positions, the counters and the job's progress (the gravel pit's day, clock, earnings and weather; Kvarnby's driveways and rink). It starts the traffic, the train and the pit's waiting customers afresh, and the pit's loader starts with the bucket on and the other tools back at the rack. Settings and progression (the account, upgrades and which tips you've seen) are kept in localStorage. Delete saves and progress, in Settings, clears it all.

## Controls

| Keys | Action |
|---|---|
| W / S | drive |
| 1 / 2 / 3 / 4 | gear (each machine keeps its own) |
| A / D | steer / turn on tracks |
| I / K | raise / lower boom |
| J / L | curl / dump bucket, angle the plow, salt fan width |
| B | plow blade / bucket / snow blower, salt spreader or sidewalk blower on/off, unhook / hook a tool at the gravel pit |
| X | switch machine (snow: loader, salt truck, snow blower) |
| Q / E, R / F | excavator swing, stick out / in |
| C | cab view (mirrors; Z / V to look left / right) |
| T | day / dusk / night |
| P | full map (a minimap is always in the corner) |
| G | show the ordered gravel (pit) / unplowed snow |
| H | send the truck off early (gravel pit) |
| M | sound |
| O | graphics quality (high: ambient occlusion, bloom, sharper shadows · low: faster) |
| N N | start the map over |

## Touch screens

On a phone or tablet two virtual joysticks sit on the game screen. The left one drives (up / down throttle and reverse, left / right steer, both proportional); the right one works the hydraulics (up / down raise and lower the boom, left / right curl and dump the bucket, angle the plow, swing a blower chute or widen the salt fan). On the excavator a DIG button turns the left stick into swing (left / right) and stick out / in (up / down). Drag anywhere else on the screen to orbit the camera, pinch to zoom. The buttons under the screen switch machine, change tool, gear, camera, map, time and sound.

Phones and tablets also get a lighter **mobile performance mode**: a coarser snow and dirt grid (400 instead of 560 cells across in the snow jobs, 360 instead of 520 in the pit), the cheap graphics setting (no ambient occlusion or bloom, pixel ratio 1, smaller shadow maps), fewer trees, snowflakes, grass and traffic, no wash light from the beacons, no mirror views and a minimap that redraws half as often. Add `?mobile=1` or `?mobile=0` to the URL to force it on or off, and `?fps` for a frame-rate readout (frames per second, simulation and draw time per frame).

## Xbox controller

Browsers only give controllers to secure pages: `https://`, or `http://localhost`. On a plain `http://` network address (say `http://192.168.0.21:8000` from another computer) the controller is silently ignored; the start screen and its Controls panel say so. Serve it with `python3 tools/serve-https.py` (a self-signed certificate is made on first run; accept the browser's warning once) and open `https://<machine>:8443`, or reach it as localhost through an SSH tunnel (`ssh -L 8000:<server address>:8000 <machine>`, then `http://localhost:8000`).

Plug in or pair an Xbox (or any standard) controller and press a button; Chrome, Edge and Firefox pick it up. The layout follows Farming Simulator's controller defaults. Sticks and triggers are analog.

| Control | Wheel loader / salt truck | Excavator |
|---|---|---|
| RT / LT | forward / brake and reverse | tracks forward / reverse |
| Left stick | steer | turn on the tracks |
| Right stick | camera: orbit the machine, or look around in the cab | same |
| LB held + right stick | arm up (pull back) / down, bucket curl / dump (left / right); salt truck: fan width | boom and bucket |
| RB held + right stick | same as LB | stick out / in (up / down), swing (left / right) |
| A | attach / detach a tool (gravel pit), blade / spreader (snow), Next day | same |
| Y | switch machine | same |
| Right stick click | cab / chase camera | same |
| X | send the vehicle off (pit), unplowed view (snow) | same |
| B | material view, close the map | same |
| Left stick click | horn | same |
| D-pad up / down, left / right | gear up / down, zoom in / out | same |
| View / Menu | map / time of day | same |

## Your own vehicle models

Drop `.glb` models into `assets/models/` to replace the code-built vehicles, one at a time. Models only load when the folder is served (`python3 -m http.server`, then open http://localhost:8000); opened straight from the file, the game uses the code-built vehicles. See [docs/MODELS.md](docs/MODELS.md) for the format, the part names and pivots, the reference files in `assets/reference/`, and prompts for AI model generators.

Map data © OpenStreetMap contributors (ODbL).

## iOS app

`ios/` holds a small native iOS app that runs the game full screen. It is a `WKWebView` that serves the very same `index.html`, `vendor/` and `assets/models/` from the app bundle over a private `app://` scheme, so there is one game and every change shows up in both the web version and the app on the next build. A build step (`ios/copy-web.sh`) copies the current files into the app each time.

In the app (and when the page is added to the home screen, or opened with `?app`) the page switches to app mode: just the game screen with the joysticks and a strip of buttons, nothing to scroll or zoom. The app also turns off the web view's own scrolling and pinch zoom.

To build it on a Mac with Xcode 15 or later:

```sh
brew install xcodegen
cd ios && xcodegen generate
open BacklotLoader.xcodeproj
```

Pick your team under Signing & Capabilities (and change the bundle ID `com.example.backlotloader` to your own), then run it on an iPhone or iPad. In debug builds Safari's Develop menu can inspect the game while it runs in the app. `ios/BacklotLoader.xcodeproj` and `ios/BacklotLoader/Info.plist` are generated from `ios/project.yml`; edit that file, not the generated ones.
