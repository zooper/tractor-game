# Backlot Loader

A low-poly 3D earthmoving and snow-plowing sandbox that runs in the browser. Open `index.html` in a modern browser; three.js (r160) loads from jsDelivr.

## Jobs

- **Dirt lot**: an articulated wheel loader and a tracked excavator. Load the dump truck, feed the hopper and conveyor, cut the staked pad to grade, and dig a trench so the pipe can be laid and backfilled.
- **Snow day · Paulus Hook, Jersey City**: plow the real streets around Liberty Towers. Streets, buildings, the Hudson-Bergen Light Rail and the neighbourhood's shops, cafés and restaurants come from OpenStreetMap; each shop gets a signed, lit storefront with a snowy awning on its real building. The shoreline (the Hudson, the Little Basin and the Morris Canal Basin) follows the OSM coastline, and the Colgate Clock stands on the point keeping real local time. Loader with plow blade or bucket, a salt spreader truck, a snow dump truck, parked cars, moving traffic, streetlights and day/dusk/night.

## Controls

| Keys | Action |
|---|---|
| W / S | drive |
| 1 / 2 / 3 / 4 | gear (each machine keeps its own) |
| A / D | steer / turn on tracks |
| I / K | raise / lower boom |
| J / L | curl / dump bucket, angle the plow, salt fan width |
| B | swap bucket / plow blade, salt spreader on/off |
| X | switch machine |
| Q / E, R / F | excavator swing, stick out / in |
| C | cab view (mirrors; Z / V to look left / right) |
| T | day / dusk / night |
| P | full map (a minimap is always in the corner) |
| G | grade / unplowed view |
| M | sound |
| O | graphics quality (high: ambient occlusion, bloom, sharper shadows · low: faster) |
| N N | new site |

## Your own vehicle models

Drop `.glb` models into `assets/models/` to replace the code-built vehicles, one at a time. Models only load when the folder is served (`python3 -m http.server`, then open http://localhost:8000); opened straight from the file, the game uses the code-built vehicles. See [docs/MODELS.md](docs/MODELS.md) for the format, the part names and pivots, the reference files in `assets/reference/`, and prompts for AI model generators.

Map data © OpenStreetMap contributors (ODbL).
