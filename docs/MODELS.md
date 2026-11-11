# Vehicle models

You can replace the code-built vehicles with your own 3D models. Make each one in Blender, export it as a `.glb`, and drop it into `assets/models/`. The game attaches your parts to its own joints, so driving, digging, plowing and collisions all keep working.

You can do one vehicle at a time. Any vehicle without a file, and any part a file doesn't include, keeps its code-built look.

## Quick start

1. Import the reference file for the vehicle from `assets/reference/` into Blender.
2. Build or import your model on top of it. Keep the reference's empties: they are the pivots, named the way the game expects.
3. Parent each of your parts to the matching empty, then delete the reference meshes.
4. Export as glTF binary to `assets/models/<name>.glb` (file names below).
5. Serve the folder (models don't load from a page opened as a file):

   ```
   python3 -m http.server
   ```

   Open http://localhost:8000. A message in the game says which models loaded. The browser console (Cmd+Option+J in Chrome) has a report for each vehicle: which parts were used, which are missing, and any warnings.

| Vehicle | File | Reference |
|---|---|---|
| Wheel loader | `assets/models/loader.glb` | `assets/reference/loader_reference.glb` |
| Excavator | `assets/models/excavator.glb` | `assets/reference/excavator_reference.glb` |
| Dump truck | `assets/models/dumptruck.glb` | `assets/reference/dumptruck_reference.glb` |
| Salt truck | `assets/models/salttruck.glb` | `assets/reference/salttruck_reference.glb` |
| Parked and traffic car | `assets/models/car_sedan.glb` | `assets/reference/car_sedan_reference.glb` |
| Parked and traffic SUV | `assets/models/car_suv.glb` | `assets/reference/car_suv_reference.glb` |

## Rules that apply to every vehicle

- **Units:** metres, at real size.
- **Orientation in Blender:** the front of the vehicle faces **−Y**, up is **+Z**, and the wheels stand on z = 0. Centre the vehicle on x = 0. The driver's left is **+X**.
- **Origins are pivots.** Each moving part is a separate object, and its origin sits exactly on the point it turns around. The arm's origin goes on the arm's hinge pin, a wheel's origin on its hub centre. Parts rotate around their origin and nothing else.
- **Apply rotation and scale, never location:** use Ctrl+A → *Rotation & Scale*. Applying *location* (or *All Transforms*) moves every origin to the world centre and destroys the pivots.
- **Names** must match the tables below. Case doesn't matter, and Blender's `.001` suffixes are ignored.
- **Parenting:** a part's mesh can be many objects, as long as they're all parented under the part's object (Ctrl+P → *Object (Keep Transform)*). Meshes that aren't under any named part are ignored, and the console says so.
- **Pose:** keep the pose of the reference file. Most vehicles are in a neutral pose. The excavator is in its parked pose: boom raised, stick and bucket tucked down.
- **Materials:** Principled BSDF with image textures only: base colour, roughness/metallic and normal map. Procedural node setups don't export, so bake them to images first.
  - Name glass materials with `glass` in the name; the game makes them see-through and hides them from inside the cab.
  - Name lamp materials `light_front`, `light_rear` or `beacon`; the game makes them glow.
- **Size limits:**
  - Machines: 30,000–80,000 triangles each.
  - Cars: 5,000–15,000 triangles each, since there are many of them.
  - Textures: 2048 px at most.
  - Files: under about 20 MB each.
  - Draco compression on export is supported.
- **No real brands:** no brand names or logos (Caterpillar, Volvo, John Deere and so on).

## Export settings (File → Export → glTF 2.0)

- **Format:** glTF Binary (`.glb`).
- **Include:** *Visible Objects*, or *Selected Objects* if you select the vehicle.
- **Transform:** *+Y Up* on (the default).
- **Mesh:** *Apply Modifiers* on.
- **Animation:** off. The game animates the parts itself.

## What the game keeps drawing itself

These stay code-built on every vehicle, so leave them out of your model or leave room for them:

- **Hydraulic rams:** a painted barrel with a chrome rod, drawn between fixed points (listed per vehicle below). Leave room for them, or model them fused to the frame or arm as non-moving decoration if you'd rather they didn't show.
- **Beacons** (the flashing amber lamps). Put an empty named `mount_beacon` where they should sit on your roof; for two beacon bars, use `mount_beacon` and `mount_beacon_2`. Without one, the beacons stay where the code-built cab had them.
- **Cab interior and the operator.** The cab view and mirrors use the code-built cab's eye position. Keep your cab roughly where the reference cab is.
- **Work lights** (the light that lights the ground). Your lamp lenses only need the `light_front` material.
- **The load:** dirt in the bucket and truck bed, and the salt level.

## Cockpit (optional)

A vehicle can bring its own cab interior. The game then shows it in cab view (C) instead of the code-built one:

- **`cab_interior`:** everything inside the cab, origin at the vehicle origin (0, 0, 0). Only visible from the driver's seat. Build it around the driver's eye point and keep the view ahead clear. The eye points are: loader (0, 0.45, 2.75); excavator (0.68, −0.30, 2.90) in parked pose; salt truck (0.50, −2.45, 2.55).
- **`steering_wheel`:** origin on the hub, turned by the game around the steering column, which is tilted 0.62 rad toward the dash. The hubs are at (0, 0.09, 2.45) on the loader and (0.50, −2.87, 2.25) on the salt truck.
- **`joystick`** and **`joystick_2`:** origin at the pivot at the bottom of the lever. The game tilts them with the controls. The pivots are: loader (−0.42, 0.48, 2.20); excavator (0.42, −0.40, 2.55) and (0.95, −0.40, 2.55); salt truck gear lever, named `joystick`, (0.05, −2.60, 1.95).
- **`needle_rpm`, `needle_speed`, `needle_fuel`, `needle_temp`:** empties at each dial's centre, with the needle mesh inside, modelled pointing at the dial's zero mark. The game turns them clockwise about the line toward the driver's eye: 270° full scale for rpm and speed, 90° for fuel and temperature.
  - The speedometer reads 0–40 km/h, the rev counter 0–2500 rpm.
- **A material named `screen`:** the game draws a live display onto it (machine, time of day, gear, speed, direction, and plow or bucket state). Give the screen face 0–1 UVs, with u running left to right and v bottom to top as the driver sees it.
- **Kept by the game:** the wiper and the snow that settles on the glass.

`tools/blender/loader.py`, `excavator.py` and `salttruck.py` build full examples.

## The included models

Every vehicle in `assets/models/` is built by a script in `tools/blender/`, so you can change one and rebuild it:

```
blender --background --factory-startup --python tools/blender/<script>.py -- [--preview DIR]
```

| Script | Builds |
|---|---|
| `loader.py` | `loader.glb`, with the plow and the cockpit |
| `excavator.py` | `excavator.glb`, with the cockpit (two joysticks, monitor, gauges) |
| `dumptruck.py` | `dumptruck.glb`, with a simple interior that shows through the glass (the truck drives itself) |
| `salttruck.py` | `salttruck.glb`, with the cockpit (wheel, gear lever, dash gauges, screen) |
| `cars.py` | `car_sedan.glb` and `car_suv.glb` (`--only sedan` or `--only suv` for one) |

`--preview DIR` also renders a few PNG views with Cycles. The scripts share `common.py` (export and previews), `kit.py` (geometry in the game's coordinates, grime textures, booleans, tyres) and `cockpit.py` (dials, wheel, levers, seats). Delete a `.glb` to go back to the code-built vehicle.

## Wheel loader: `loader.glb`

The loader bends in the middle. The rear frame carries the cab and engine; the front frame carries the arms and steers around the joint at the origin.

| Part (object name) | Pivot, Blender (x, y, z) | Notes |
|---|---|---|
| `frame_rear` | (0, 0, 0) | engine, counterweight, cab, rear fenders |
| `frame_front` | (0, 0, 0) | front chassis and fenders; turns around the vertical axis through the origin |
| `arm` | (0, −0.70, 1.75) | lift arms and cross tube, child of `frame_front`; hinges around X |
| `bucket` | (0, −3.30, 1.75) | child of `arm`; the pivot is the bucket's hinge pin at the arm tip |
| `plow` | (0, −3.30, 1.75) | child of `arm`; swivels left and right around its vertical axis. The blade's cutting edge sits 0.95 m ahead of this pivot, and the game hides the plow or the bucket, whichever isn't in use. |
| `wheel_front_left`, `wheel_front_right`, `wheel_rear_left`, `wheel_rear_right` | (±1.05, ∓1.25, 0.70) | radius 0.70 m, width about 0.58 m; spin around X. Wheels are matched by position, so any parent works and the game puts each one on the right frame. |

**Rams** the game draws, at the rest pose in Blender coordinates:

- **Lift rams:** (±0.55, −1.50, 0.95) → (±0.55, −1.95, 1.63).
- **Tilt ram:** (0, −1.05, 1.55) → (0, −2.15, 2.25).
- **Steering rams:** (±0.42, 0.55, 1.00) → (±0.42, −0.45, 1.00).

## Excavator: `excavator.glb`

| Part | Pivot, Blender (x, y, z) | Notes |
|---|---|---|
| `undercarriage` | (0, 0, 0) | tracks, track frames and rollers; tracks about 3 m long, centred at x = ±1.1 |
| `house` | (0, 0, 0.95) | everything above the turntable; swings around the vertical axis |
| `boom` | (−0.25, −0.85, 2.10) | child of `house`; hinges around X |
| `stick` | (−0.25, −3.75, 3.88) | child of `boom` |
| `bucket` | (−0.25, −4.57, 2.05) | child of `stick` |
| `sprocket_front_left`, `sprocket_front_right`, `sprocket_rear_left`, `sprocket_rear_right` | (±1.10, ∓1.50, 0.42) | the wheels at each end of the tracks; they spin as you drive. Optional. |

**Rams**, in the parked pose:

- **Boom:** (−0.25, −0.60, 1.70) → (−0.25, −2.06, 2.90).
- **Stick:** (−0.25, −1.69, 3.34) → (−0.25, −3.88, 4.32).
- **Bucket:** (−0.25, −4.14, 3.73) → (−0.25, −4.72, 1.61).

## Dump truck: `dumptruck.glb`

| Part | Pivot, Blender (x, y, z) | Notes |
|---|---|---|
| `body` | (0, 0, 0) | everything that doesn't spin: cab, chassis, tipper body. The tipper doesn't tip in the game. |
| `wheel_1_left`, `wheel_1_right` | (±1.10, −2.30, 0.62) | front axle; radius 0.62 m |
| `wheel_2_left`, `wheel_2_right` | (±1.10, 0.90, 0.62) | |
| `wheel_3_left`, `wheel_3_right` | (±1.10, 2.20, 0.62) | |
| `mount_beacon` | on the cab roof | empty, snow job only |

The truck bed's inside should be roughly 2.3 m wide and 3.7 m long, with the floor about 1.5 m up, centred 0.7 m behind the middle of the truck. That's where the game draws the dirt.

## Salt truck: `salttruck.glb`

| Part | Pivot, Blender (x, y, z) | Notes |
|---|---|---|
| `body` | (0, 0, 0) | cab, chassis and the V-shaped spreader body (open at the top) |
| `spinner` | (0, 3.95, 0.95) | the spinning disc under the back; turns around the vertical axis |
| `salt` | (0, 1.20, 2.55) | optional: the top surface of the salt load, about 2.2 × 4 m. The game moves it down and narrows it as the tank empties. |
| `wheel_1_left`, `wheel_1_right` | (±1.10, −3.60, 0.55) | front axle; these steer. Radius 0.55 m. |
| `wheel_2_*`, `wheel_3_*` | (±1.12, 1.30 and 2.55, 0.55) | |
| `mount_beacon` | on the cab roof | empty |

## Cars: `car_sedan.glb` and `car_suv.glb`

Cars are simpler: no named parts and nothing moves.

- **Size:** about 1.8 m wide and 4.4–4.5 m long. Height about 1.5 m for the sedan and 1.9 m for the SUV.
- **Placement:** front faces −Y, centred on the origin, wheels standing on z = 0, wheel centres about 1.35 m in front of and behind the middle.
- **Body paint:** give the paint a material with `body` or `paint` in its name. The game recolours it for every car, so make it white or light grey and let the texture carry only the dirt and detail.
- **Glass and lights:** use `glass` for glass, and `light_front` and `light_rear` for the lamps. Traffic cars light theirs up.
- **Snow:** model cars clean. In the snow job the game adds its own snow caps on the roof, hood and trunk, sized for a car of the standard shape.

## Checking a model

The browser console report flags these problems:

- **"origin is 0.40 m and 12° off the game's pivot":** that part will swing around the wrong point. Move its origin onto the empty from the reference file.
- **"scale is not applied":** run Ctrl+A → *Rotation & Scale* on that object.
- **"no wheel of the game within 0.6 m of it":** a wheel is in the wrong place, or the vehicle is facing the wrong way. The front should face −Y.
- **"N mesh(es) are not under any named part":** those meshes aren't parented to a named part, so the game ignores them.
- **"none of the expected part names found":** check the names against the tables above.

## Prompts for an AI model generator

AI generators usually give you one fused mesh. Ask for the parts separately anyway: it makes the clean-up much easier. Replace the colour if you like.

**Wheel loader**

> A realistic medium-size articulated wheel loader for construction work, generic design with no brand names or logos, yellow paint with light wear and grime, black frame parts, tinted glass cab with a roof-mounted work light bar. Four large earthmover tyres with chevron tread, about 1.4 m in diameter. A front-mounted bucket about 2.5 m wide. Overall about 2.5 m wide, 3.3 m tall to the cab roof and 7.5 m long with the bucket. Separate objects for: rear frame with engine and cab, front frame, lift arms, bucket, and each of the four wheels. Neutral pose, bucket resting near the ground, arms nearly horizontal. PBR textures, no baked lighting or shadows in the colour texture, game-ready topology under 80,000 triangles.

**Snow plow blade** (if you want it as its own model, to attach as the loader's `plow`)

> A heavy snow plow blade for a wheel loader, generic design, orange paint with scratches, 3.4 m wide and about 1.1 m tall. A smooth shallow curved moldboard at the front, a flat back sheet with horizontal stiffeners, closed end plates, a steel cutting edge along the bottom and two tall curb marker rods with orange tips. A short mounting frame behind it. PBR textures, no baked lighting, under 15,000 triangles.

**Excavator**

> A realistic mid-size tracked hydraulic excavator, generic design with no brand names or logos, yellow paint with light wear, black undercarriage with steel track shoes, a tinted glass cab on the left side of the upper body, a rear counterweight. Boom raised, stick and digging bucket tucked down in a parked pose. Overall about 2.9 m wide and 3 m long across the tracks. Separate objects for: undercarriage with tracks, upper body with cab, boom, stick, bucket. PBR textures, no baked lighting, game-ready topology under 80,000 triangles.

**Dump truck**

> A realistic three-axle road dump truck, generic design with no brand names or logos, red cab with a long hood and a chrome-trimmed grille, grey steel tipper body with vertical ribs, chrome fuel tank and exhaust stack, six road tyres with steel rims, 1.24 m tyre diameter. About 2.5 m wide, 3.3 m tall and 7 m long. Separate objects for: the body (cab, chassis and tipper together) and each of the six wheels. PBR textures, no baked lighting, under 60,000 triangles.

**Salt spreader truck**

> A realistic three-axle municipal salt spreader truck, generic design with no brand names or logos, orange cab and hood, an open-topped galvanised steel V-shaped spreader body on the back, a spinning spreader disc under the rear, ladder and hazard stripes at the back, six road tyres, 1.1 m tyre diameter. About 2.5 m wide, 3.5 m tall and 9 m long. Separate objects for: the body, the spreader disc, and each of the six wheels. PBR textures, no baked lighting, under 60,000 triangles.

**Car** (do the same with "compact SUV" for `car_suv`)

> A generic mid-size four-door sedan, no brand names or logos, white paint, dark tinted windows, chrome trim, alloy wheels. About 1.8 m wide, 1.5 m tall and 4.5 m long. Clean, not dirty. PBR textures, no baked lighting, under 15,000 triangles.

## Clean-up checklist for AI-generated models in Blender

1. **Scale:** measure it with the reference file next to it and scale to match. Then Ctrl+A → *Rotation & Scale*.
2. **Orientation:** turn it to face −Y with the wheels on z = 0.
3. **Splitting parts:** if it's one fused mesh, split it.
   - Select faces in Edit mode (L picks connected geometry), then press P → *Selection*.
   - Wheels are usually separate pieces already; for arms and buckets you may need to cut.
4. **Origins:** for each part, snap the 3D cursor to the reference empty (select the empty, Shift+S → *Cursor to Selected*). Then select the part and choose Object → Set Origin → *Origin to 3D Cursor*. Name it, and parent it to the empty.
5. **Triangle count:** too many triangles? Use the Decimate modifier (Collapse, ratio 0.2–0.5), then apply it.
6. **Baked lighting:** check that the colour texture has no shadows or highlights painted in. If it does, the model will look wrong under the game's lighting. Regenerate with "no baked lighting", or paint them out.
7. **Materials:** rename the glass, lamp and car paint materials as described above.
8. **Delete the reference geometry** (keep the empties), then export.

## Regenerating the reference files

The reference files are the game's code-built vehicles exported at rest, with each joint as a named empty. If the code-built vehicles change, regenerate them:

1. Serve the folder.
2. Open `http://localhost:8000/?reference` and pick a job. The dirt lot has the loader and excavator; the snow day has the dump truck (with its beacon), the salt truck and the cars.
3. In the browser console, run this for each vehicle:

   ```js
   const b64 = await __exportReference('loader');
   ```

   The key is one of `loader`, `excavator`, `dumptruck`, `salttruck`, `car_sedan` or `car_suv`, and the result is the `.glb` file as base64.
4. Save it, for example with:

   ```js
   Object.assign(document.createElement('a'), { href: 'data:model/gltf-binary;base64,' + b64, download: 'loader_reference.glb' }).click()
   ```

   `__rigInfo()` lists every pivot position, in game coordinates (x, y up, z forward).
