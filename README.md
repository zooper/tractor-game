# Backlot Loader

A low-poly 3D earthmoving and snow-plowing sandbox that runs in the browser. Open `index.html` in a modern browser; three.js (r160) loads from jsDelivr.

## Jobs

- **Gravel pit · Grustag**: a made-up Swedish gravel pit, open 07:00–16:00 with a morning rush and a summary at closing. Up to three customers at a time (tippers of three sizes, or a car and trailer) wait, as long as it takes, at the pile they want: load the right gravel to the right weight, or boulders and big bags from the yard with the pallet forks. Swap the bucket, a big light-material bucket and the forks at the tool rack (B). Feed naturgrus to the crusher to refill bärlager and makadam. Weather drifts from clear to rain and snow showers; wet gravel weighs more, trucks slow down in it and for spilled gravel on the haul roads.
- **Snow day · Paulus Hook, Jersey City**: plow the real streets around Liberty Towers. Streets, buildings, the Hudson-Bergen Light Rail and the neighbourhood's shops, cafés and restaurants come from OpenStreetMap; each shop gets a signed, lit storefront with a snowy awning on its real building. The shoreline (the Hudson, the Little Basin and the Morris Canal Basin) follows the OSM coastline, and the Colgate Clock stands on the point keeping real local time. Loader with plow blade, bucket or a 2.9 m snow-blower attachment (J / L swing the chute), a salt spreader truck, a sidewalk snow blower (J / L swing its chute), a snow dump truck, parked cars, moving traffic that stops at working traffic lights, lane markings and zebra crossings that show as you plow down to the pavement, streetlights and day/dusk/night. Liberty Towers is modelled by hand: curved glass between the towers, sawtooth tan masonry outside, the podium with shops, garage and pool deck, and the lobby under its canopy on Morris Street.

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
| N N | new site |

## Xbox controller

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
