"""Three-axle dump truck -> assets/models/dumptruck.glb

    blender --background --factory-startup --python tools/blender/dumptruck.py -- [--out PATH] [--preview DIR]

Sizes and pivots are game coordinates (kit.py) copied from buildTruck() in index.html. The truck is driven by
the game, so its cab has a simple interior that shows through the glass rather than a full cockpit.
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(__file__))
import common as C  # noqa: E402
import kit as K  # noqa: E402
import cockpit as CP  # noqa: E402
from kit import G, box, cyl, tube  # noqa: E402

opt = C.args()
C.reset()

R_W, W_W = 0.62, 0.46
red = K.mat("paint_red", rough=0.38, metal=0.05, image=K.grime_image("grime_red", 0xa9472f, 0.7, seed=31))
redD = K.mat("paint_red_dark", rough=0.45, metal=0.05, image=K.grime_image("grime_red_dark", 0x8e3a25, 0.9, seed=32))
bed = K.mat("bed_steel", rough=0.5, metal=0.4, image=K.grime_image("grime_bed", 0x8f8b82, 1.2, seed=33))
bedL = K.mat("bed_steel_light", rough=0.45, metal=0.4, image=K.grime_image("grime_bed_light", 0xb9b5aa, 1.0, seed=34))
frame = K.mat("frame_dark", rough=0.55, metal=0.3, image=K.grime_image("grime_frame", 0x262523, 1.0, seed=35))
black = K.mat("black_plastic", 0x171717, rough=0.55)
rubber = K.mat("tyre_rubber", 0x1b1b1b, rough=0.9)
rimM = K.mat("rim_paint", rough=0.4, metal=0.3, image=K.grime_image("grime_rim", 0xc9ccd0, 0.9, seed=36))
chrome = K.mat("chrome", 0xdadcdf, rough=0.12, metal=1.0)
iron = K.mat("iron", 0x2c2c2e, rough=0.5, metal=0.6)
steel = K.mat("steel_worn", 0x8a8880, rough=0.35, metal=0.9)
rod = K.mat("ram_rod", 0xe0e2e4, rough=0.1, metal=1.0)
glass = K.mat("glass", 0x2a3a40, rough=0.04, metal=0.1, alpha=0.38)
lensF = K.mat("light_front", 0xfff4dc, rough=0.05, emit=0xfff0d0, emit_strength=2.0)
lensR = K.mat("light_rear", 0x9c1c14, rough=0.1, emit=0xb0170f, emit_strength=1.0)
amber = K.mat("light_marker", 0xffa21a, rough=0.1, emit=0xff9010, emit_strength=0.6)
M = CP.Mats(accent=0xa9472f)

body = K.Part("body")
mount = bpy.data.objects.new("mount_beacon", None)
mount.location = G(0, 2.86, 1.9)
bpy.context.collection.objects.link(mount)
mount.parent = body.empty

# ================================================================ chassis, axles, tanks
for x in (-0.48, 0.48):
    body.add(frame, box(0.2, 0.3, 6.6, (x, 0.92, -0.1), r=0.03))
for z in (-3.2, -1.6, -0.2, 1.2, 2.6):
    body.add(frame, box(0.78, 0.16, 0.12, (0, 0.92, z), r=0.02))
body.add(frame, box(2.44, 0.34, 0.3, (0, 0.86, 3.48), r=0.06))
for sx in (-0.7, 0.7):
    body.add(iron, K.torus((sx, 0.78, 3.65), ((1, 0, 0), (0, 1, 0), (0, 0, 1)), 0.06, 0.018, seg=16, rseg=6))
body.add(black, box(1.0, 0.14, 0.02, (0, 0.86, 3.635)))
body.add(iron, cyl(0.1, 1.9, (0, R_W, 2.3), axis="x", seg=16))
for z in (-0.9, -2.2):
    body.add(iron, cyl(0.12, 2.0, (0, R_W, z), axis="x", seg=18))
    body.add(iron, cyl(0.27, 0.36, (0, R_W, z), axis="z", seg=20, bevel=0.03))
for z, L in ((2.3, 1.3), (-1.55, 2.2)):
    for x in (-0.48, 0.48):
        for k in range(5):
            body.add(steel, box(0.09, 0.025, L - k * 0.22, (x, 0.72 + k * 0.026, z), r=0.008))
body.add(iron, cyl(0.07, 3.0, (0, 0.7, 0.7), axis="z", seg=12))
# chrome fuel tank on the left with straps, steps on the right, air tank, battery box
body.add(chrome, cyl(0.3, 1.1, (1.0, 1.0, 0.75), axis="z", seg=28, bevel=0.03))
for z in (0.42, 1.08):
    body.add(black, cyl(0.31, 0.05, (1.0, 1.0, z), axis="z", seg=28))
body.add(chrome, cyl(0.07, 0.04, (1.0, 1.3, 1.0), seg=14))
for k in range(2):
    body.add(iron, box(0.34, 0.04, 0.3, (-1.05, 0.72 + k * 0.42, 1.55), r=0.015))
    for gx in range(5):
        body.add(frame, box(0.04, 0.045, 0.2, (-1.17 + gx * 0.06, 0.74 + k * 0.42, 1.55)))
body.add(frame, box(0.5, 0.5, 0.5, (-0.95, 0.98, 1.55), r=0.03))
body.add(frame, cyl(0.13, 0.8, (-0.9, 0.95, 0.6), axis="z", seg=16))
# exhaust stack with a heat shield and a curved rain-cap top
body.add(chrome, cyl(0.08, 1.7, (-0.95, 2.45, 0.98), seg=20))
body.add(steel, cyl(0.11, 0.8, (-0.95, 2.1, 0.98), seg=20))
body.add(chrome, cyl(0.085, 0.1, (-0.95, 3.32, 0.98), seg=20, rot=K.rot_game(rx=0.5)))
body.add(iron, tube([(-0.95, 1.6, 0.98), (-0.85, 1.05, 0.98), (-0.5, 0.85, 0.98)], 0.07, seg=12))
# front fenders
for sx in (-1.1, 1.1):
    body.add(red, K.arc_shell(0.7, 0.55, math.radians(10), math.radians(170), 0.03, (sx, R_W, 2.3)))
    body.add(black, box(0.5, 0.06, 1.0, (sx * 1.02, 1.32, -1.55), r=0.02))       # spray guard over the rear wheels
    body.add(black, box(0.5, 0.5, 0.02, (sx, 0.62, -2.85), r=0.01))             # mud flaps
    body.add(frame, box(0.05, 0.05, 0.5, (sx * 0.85, 0.9, -2.75), r=0.01))

# ================================================================ cab and hood
CY, CZ = 2.05, 1.82                                     # cab x +-1.16, y 1.3..2.8, z 1.045..2.595
WS = (2.0, 2.06, 2.72)                                  # windshield width, bottom, top
SWz = (1.42, 2.42)
shell = K.boolean(box(2.32, 1.5, 1.55, (0, CY, CZ), r=0.14, seg=3), [
    box(2.2, 1.38, 1.43, (0, CY, CZ)),
    box(WS[0], WS[2] - WS[1], 0.4, (0, (WS[1] + WS[2]) / 2, CZ + 0.78), r=0.06),
    box(2.8, 0.6, SWz[1] - SWz[0], (0, 2.37, sum(SWz) / 2), r=0.06),
    box(1.2, 0.38, 0.4, (0, 2.4, CZ - 0.78), r=0.05),
])
body.add(red, shell)
body.add(glass, box(WS[0] + 0.02, WS[2] - WS[1] + 0.02, 0.012, (0, (WS[1] + WS[2]) / 2, CZ + 0.745)))
body.add(glass, box(1.22, 0.4, 0.012, (0, 2.4, CZ - 0.745)))
for sx in (-1, 1):
    body.add(glass, box(0.012, 0.62, SWz[1] - SWz[0] + 0.02, (sx * 1.13, 2.37, sum(SWz) / 2)))
    body.add(black, box(0.014, 1.3, 0.012, (sx * 1.162, 1.98, 1.32)))
    body.add(black, box(0.014, 1.3, 0.012, (sx * 1.162, 1.98, 2.48)))
    body.add(chrome, box(0.03, 0.04, 0.18, (sx * 1.175, 1.95, 1.5), r=0.01))
    body.add(chrome, tube([(sx * 1.15, 1.45, 2.5), (sx * 1.19, 1.9, 2.52), (sx * 1.19, 2.5, 2.52), (sx * 1.15, 2.65, 2.5)], 0.016))
    body.add(iron, tube([(sx * 1.1, 2.6, 2.4), (sx * 1.42, 2.62, 2.5), (sx * 1.45, 2.58, 2.5)], 0.016))
    body.add(iron, tube([(sx * 1.1, 2.12, 2.4), (sx * 1.42, 2.15, 2.5), (sx * 1.45, 2.2, 2.5)], 0.016))
    body.add(black, box(0.05, 0.38, 0.22, (sx * 1.46, 2.4, 2.5), r=0.02))
    body.add(chrome, box(0.01, 0.34, 0.18, (sx * 1.46, 2.4, 2.38)))
    for k in range(3):
        body.add(amber, box(0.07, 0.04, 0.05, (sx * (0.2 + k * 0.12), 2.82, 2.55), r=0.012))
body.add(black, box(2.36, 0.08, 0.22, (0, 2.85, 2.6), r=0.02, rot=K.rot_game(rx=-0.15)))     # sun visor
body.add(iron, box(1.6, 0.05, 0.14, (0, 2.84, 1.9), r=0.015))                  # light bar for the beacons (+-0.7)
for sx in (-0.7, 0.7):
    body.add(iron, box(0.24, 0.05, 0.24, (sx, 2.845, 1.9), r=0.02))
# long hood: rounded nose, raised centre crown, side vents; chrome grille surround and bars
body.add(red, box(2.06, 0.92, 1.1, (0, 1.5, 2.95), r=0.2, seg=4))
body.add(redD, box(1.9, 0.06, 0.95, (0, 1.98, 2.95), r=0.03))
for sx in (-1, 1):
    for k in range(6):
        body.add(frame, box(0.02, 0.025, 0.5, (sx * 1.035, 1.5 + k * 0.05, 2.75)))
body.add(chrome, box(1.42, 0.7, 0.04, (0, 1.45, 3.5), r=0.03))
body.add(frame, box(1.3, 0.62, 0.03, (0, 1.45, 3.51)))
for k in range(9):
    body.add(chrome, box(1.24, 0.025, 0.03, (0, 1.19 + k * 0.065, 3.525), r=0.006))
for sx in (-0.82, 0.82):
    body.add(iron, box(0.32, 0.2, 0.06, (sx, 1.42, 3.5), r=0.03))
    body.add(lensF, box(0.26, 0.15, 0.02, (sx, 1.42, 3.535), r=0.02))
    body.add(amber, box(0.18, 0.06, 0.03, (sx, 1.26, 3.52), r=0.01))
# simple interior that shows through the glass: dash, wheel, two seats, back wall
body.add(M.dash, K.plate([(2.53, 1.36), (2.53, 2.0), (2.4, 2.06), (2.28, 2.03), (2.22, 1.8), (2.3, 1.36)], 2.16, 0, r=0.03))
body.add(M.black, K.torus((0.55, 2.2, 2.15), ((1, 0, 0), (0, math.cos(0.7), math.sin(0.7)), (0, -math.sin(0.7), math.cos(0.7))), 0.22, 0.02, seg=32, rseg=6))
for sx in (0.55, -0.55):
    body.add(M.fabric, box(0.5, 0.12, 0.48, (sx, 1.75, 1.6), r=0.05))
    body.add(M.fabric, box(0.5, 0.68, 0.12, (sx, 2.1, 1.3), r=0.05, rot=K.rot_game(rx=-0.15)))
body.add(M.liner, box(2.16, 0.03, 1.4, (0, 2.76, CZ), r=0.01))

# ================================================================ dump body
BZc, BL = -0.7, 3.95
body.add(bed, box(2.5, 0.14, BL, (0, 1.45, BZc), r=0.04))
for sx in (-1, 1):
    body.add(bed, box(0.1, 0.98, BL, (sx * 1.22, 1.95, BZc), r=0.03))
    body.add(bedL, box(0.16, 0.1, 4.0, (sx * 1.22, 2.46, BZc), r=0.03))
    for k in range(5):
        body.add(bed, box(0.07, 0.9, 0.09, (sx * 1.3, 1.95, -2.5 + k * 0.9), r=0.02))
    body.add(bed, box(0.08, 0.1, BL, (sx * 1.3, 1.5, BZc), r=0.02))               # bottom side rail
    body.add(frame, box(0.16, 0.2, BL, (sx * 0.5, 1.28, BZc), r=0.02))            # bed longitudinals
    body.add(iron, cyl(0.06, 0.16, (sx * 1.2, 1.5, -2.66), axis="x", seg=12))    # tailgate hinge pins (bottom)
    body.add(iron, box(0.1, 0.2, 0.16, (sx * 1.22, 2.3, -2.68), r=0.02))         # top tailgate latch
for k in range(5):
    body.add(frame, box(2.3, 0.12, 0.1, (0, 1.3, -2.5 + k * 0.9), r=0.02))       # cross sills under the floor
body.add(bed, box(2.5, 1.3, 0.12, (0, 2.1, 1.25), r=0.03))                      # headboard
for k in range(4):
    body.add(bed, box(0.08, 1.2, 0.08, (-0.9 + k * 0.6, 2.1, 1.33), r=0.02))
body.add(bed, box(2.5, 0.08, 0.85, (0, 2.78, 1.62), r=0.03))                    # cab guard
for sx in (-1, 1):
    body.add(bed, box(0.08, 0.3, 0.85, (sx * 1.21, 2.64, 1.62), r=0.02))
body.add(bed, box(2.5, 0.9, 0.12, (0, 1.9, -2.66), r=0.03))                     # tailgate
for k in range(3):
    body.add(bedL, box(2.42, 0.06, 0.06, (0, 1.6 + k * 0.28, -2.74), r=0.015))
for sx in (-1, 1):                                                               # pressed bands along the sides
    for y in (1.75, 2.15):
        body.add(bedL, box(0.05, 0.06, BL - 0.1, (sx * 1.28, y, BZc), r=0.015))
body.add(iron, cyl(0.07, 2.4, (0, 2.55, 2.0), axis="x", seg=14))               # tarp roller on the guard
body.add(black, cyl(0.1, 2.3, (0, 2.55, 2.0), axis="x", seg=16))
for sx in (-0.9, 0.9):
    body.add(iron, box(0.26, 0.16, 0.06, (sx, 1.25, -2.72), r=0.02))
    body.add(lensR, box(0.22, 0.12, 0.02, (sx, 1.25, -2.755), r=0.01))
    body.add(amber, box(0.08, 0.08, 0.03, (sx * 1.3, 2.4, -2.74), r=0.015))
# hoist ram under the front of the bed (doesn't move: the bed never tips in the game)
body.add(frame, cyl(0.12, 0.6, (0, 1.12, 0.85), seg=18, rot=K.rot_game(rx=-0.78)))
body.add(rod, cyl(0.07, 0.3, (0, 1.35, 0.65), seg=16, rot=K.rot_game(rx=-0.78)))
body.add(iron, box(0.4, 0.14, 0.3, (0, 0.95, 1.05), r=0.03))

# ================================================================ wheels
wheels = []
for axle, z, drive in ((1, 2.3, False), (2, -0.9, True), (3, -2.2, True)):
    for xs in (1, -1):
        p = (xs * 1.1, R_W, z)
        w = K.Part(f"wheel_{axle}_{'left' if xs > 0 else 'right'}", p, body)
        car, blocks = K.road_tyre(R_W, W_W, p, blocks=28 if drive else 0)
        w.add(rubber, car)
        if drive:
            w.add(rubber, blocks)
        rim, holes, hub = K.steel_rim(R_W, W_W, p, out_sign=xs)
        w.add(rimM, rim)
        w.add(black, holes)
        w.add(chrome, hub)
        wheels.append(w)

for part in (body, *wheels):
    part.build()
tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
print(f"dumptruck: about {tris} triangles")
out = os.path.abspath(opt.get("out", os.path.join(os.path.dirname(__file__), "..", "..", "assets", "models", "dumptruck.glb")))
C.export_glb(out)
print("exported", out, os.path.getsize(out) // 1024, "KB")
if opt.get("preview"):
    d = opt["preview"]
    for name, az, el, dist in (("front", 35, 14, 11), ("rear", 215, 22, 11), ("side", 95, 6, 10)):
        C.preview(os.path.join(d, f"dumptruck_{name}.png"), target=(0, -0.2, 1.5), dist=dist, az=az, el=el, size=(1000, 650), samples=32)
