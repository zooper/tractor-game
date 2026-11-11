"""Salt spreader truck -> assets/models/salttruck.glb

    blender --background --factory-startup --python tools/blender/salttruck.py -- [--out PATH] [--preview DIR]

Sizes and pivots are game coordinates (kit.py) copied from buildSaltTruck() in index.html.
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(__file__))
import common as C  # noqa: E402
import kit as K  # noqa: E402
import cockpit as CP  # noqa: E402
from kit import G, box, cyl, tube, merge  # noqa: E402

opt = C.args()
C.reset()

R_W, W_W = 0.55, 0.42
CAB = dict(w=2.42, h=1.62, d=1.82, y=2.05, z=2.6)       # x +-1.21, y 1.24..2.86, z 1.69..3.51
FL = 1.30                                               # cab floor (top of the floor sheet)
EYE = (0.5, 2.55, 2.45)

orange = K.mat("paint_orange", rough=0.42, metal=0.05, image=K.grime_image("grime_orange", 0xe8692c, 0.7, seed=21))
orangeD = K.mat("paint_orange_dark", rough=0.48, metal=0.05, image=K.grime_image("grime_orange_dark", 0xc4541f, 0.9, seed=22))
frame = K.mat("frame_dark", rough=0.55, metal=0.3, image=K.grime_image("grime_frame", 0x262523, 1.0, seed=23))
galv = K.mat("galvanised", rough=0.45, metal=0.7, image=K.grime_image("grime_galv", 0x9aa1a6, 0.8, seed=24, mud=False))
black = K.mat("black_plastic", 0x171717, rough=0.55)
rubber = K.mat("tyre_rubber", 0x1b1b1b, rough=0.9)
rimM = K.mat("rim_paint", rough=0.4, metal=0.3, image=K.grime_image("grime_rim", 0xc9ccd0, 0.8, seed=25))
chrome = K.mat("chrome", 0xdadcdf, rough=0.15, metal=1.0)
iron = K.mat("iron", 0x2c2c2e, rough=0.5, metal=0.6)
steel = K.mat("steel_worn", 0x8a8880, rough=0.35, metal=0.9)
glass = K.mat("glass", 0x2a3a40, rough=0.04, metal=0.1, alpha=0.38)
lensF = K.mat("light_front", 0xfff4dc, rough=0.05, emit=0xfff0d0, emit_strength=2.0)
lensR = K.mat("light_rear", 0x9c1c14, rough=0.1, emit=0xb0170f, emit_strength=1.0)
amber = K.mat("light_marker", 0xffa21a, rough=0.1, emit=0xff9010, emit_strength=0.6)
hz_y = K.mat("hazard_yellow", 0xf2c21a, rough=0.5)
hz_k = K.mat("hazard_black", 0x141414, rough=0.5)
saltM = K.mat("salt", 0xd9dfe6, rough=0.95)

body = K.Part("body")
spinner = K.Part("spinner", (0, 0.95, -3.95), body)
salt = K.Part("salt", (0, 2.55, -1.2), body)
mount = bpy.data.objects.new("mount_beacon", None)
mount.location = G(0, 2.98, 2.6)
bpy.context.collection.objects.link(mount)
mount.parent = body.empty

# ================================================================ chassis
for x in (-0.5, 0.5):
    body.add(frame, box(0.2, 0.32, 7.4, (x, 1.0, 0.3), r=0.03))
for z in (-3.2, -2.0, -0.6, 0.9, 2.2, 3.9):
    body.add(frame, box(0.82, 0.18, 0.12, (0, 1.0, z), r=0.02))
for z in (-1.3, -2.55):
    body.add(iron, cyl(0.12, 2.0, (0, R_W, z), axis="x", seg=18))
    body.add(iron, cyl(0.26, 0.34, (0.0, R_W, z), axis="z", seg=20, bevel=0.03))
    for x in (-0.5, 0.5):                                                         # leaf springs
        for k in range(4):
            body.add(steel, box(0.09, 0.025, 1.3 - k * 0.22, (x, 0.74 + k * 0.026, z), r=0.008))
body.add(iron, cyl(0.1, 1.9, (0, R_W, 3.6), axis="x", seg=16))                   # front axle beam
for x in (-0.5, 0.5):
    for k in range(4):
        body.add(steel, box(0.09, 0.025, 1.2 - k * 0.2, (x, 0.76 + k * 0.026, 3.6), r=0.008))
body.add(iron, cyl(0.07, 4.2, (0, 0.72, 0.5), axis="z", seg=12))               # drive shaft
# fenders over the front wheels, mud flaps behind the rear ones
for sx in (-1.1, 1.1):
    body.add(orange, K.arc_shell(0.64, 0.5, math.radians(15), math.radians(165), 0.03, (sx, R_W, 3.6)))
    body.add(black, box(0.46, 0.06, 1.0, (sx * 1.02, 0.92, -1.92), r=0.02))      # rear wheel spray guard
    body.add(black, box(0.48, 0.55, 0.02, (sx, 0.58, -3.2), r=0.01))
    body.add(frame, box(0.05, 0.05, 0.4, (sx * 0.9, 0.9, -3.0), r=0.01))
# fuel tank with straps on the right, steps and battery box on the left
body.add(chrome, cyl(0.28, 1.0, (-1.0, 1.05, 1.0), axis="z", seg=28, bevel=0.03))
for z in (0.7, 1.3):
    body.add(black, cyl(0.29, 0.05, (-1.0, 1.05, z), axis="z", seg=28))
body.add(black, cyl(0.06, 0.04, (-1.0, 1.33, 1.25), seg=14))
body.add(frame, box(0.5, 0.55, 0.6, (1.0, 1.05, 2.0), r=0.03))                  # battery box under the steps
for k in range(2):
    body.add(iron, box(0.36, 0.035, 0.32, (1.15, 0.8 + k * 0.4, 2.0), r=0.01))
    for gx in range(5):
        body.add(frame, box(0.04, 0.04, 0.22, (1.02 + gx * 0.065, 0.818 + k * 0.4, 2.0)))
body.add(frame, cyl(0.14, 0.7, (-0.85, 1.0, -0.2), axis="z", seg=16))          # air tanks
body.add(frame, cyl(0.14, 0.7, (0.85, 1.0, -0.2), axis="z", seg=16))
# exhaust stack behind the cab with a heat shield and a rain-cap cut
body.add(chrome, cyl(0.08, 1.5, (1.32, 2.8, 1.62), seg=20))
body.add(steel, cyl(0.11, 0.9, (1.32, 2.55, 1.62), seg=20))
body.add(frame, box(0.12, 0.12, 0.2, (1.25, 1.95, 1.62), r=0.02))
body.add(iron, tube([(1.25, 1.9, 1.62), (1.1, 1.3, 1.62), (0.6, 1.05, 1.62)], 0.07, seg=12))

# ================================================================ cab: hollow shell with real window openings
cx, cy, cz = 0.0, CAB["y"], CAB["z"]
W2, H2, D2 = CAB["w"] / 2, CAB["h"] / 2, CAB["d"] / 2
WS = dict(w=2.0, y0=2.12, y1=2.8)                                                 # windshield opening
SW = dict(y0=2.16, y1=2.74, z0=2.0, z1=3.22)                                      # side windows
shell = K.boolean(box(CAB["w"], CAB["h"], CAB["d"], (cx, cy, cz), r=0.12, seg=3), [
    box(CAB["w"] - 0.12, CAB["h"] - 0.12, CAB["d"] - 0.12, (cx, cy + 0.0, cz)),
    box(WS["w"], WS["y1"] - WS["y0"], 0.4, (0, (WS["y0"] + WS["y1"]) / 2, cz + D2), r=0.06),
    box(CAB["w"] + 0.4, SW["y1"] - SW["y0"], SW["z1"] - SW["z0"], (0, (SW["y0"] + SW["y1"]) / 2, (SW["z0"] + SW["z1"]) / 2), r=0.06),
    box(1.3, 0.42, 0.4, (0, 2.48, cz - D2), r=0.06),                               # rear window
])
body.add(orange, shell)
body.add(orangeD, box(2.46, 0.12, 1.86, (0, 2.9, cz), r=0.05))                  # roof cap
body.add(glass, box(WS["w"] + 0.02, WS["y1"] - WS["y0"] + 0.02, 0.012, (0, (WS["y0"] + WS["y1"]) / 2, cz + D2 - 0.03)))
for sx in (-1, 1):
    body.add(glass, box(0.012, SW["y1"] - SW["y0"] + 0.02, SW["z1"] - SW["z0"] + 0.02, (sx * (W2 - 0.03), (SW["y0"] + SW["y1"]) / 2, (SW["z0"] + SW["z1"]) / 2)))
    body.add(frame, box(0.02, 0.6, 0.03, (sx * (W2 - 0.03), (SW["y0"] + SW["y1"]) / 2, 2.72)))   # vent window divider
    body.add(black, box(0.014, 1.36, 0.012, (sx * (W2 + 0.002), 1.95, 1.98)))     # door seams
    body.add(black, box(0.014, 1.36, 0.012, (sx * (W2 + 0.002), 1.95, 3.28)))
    body.add(black, box(0.014, 0.012, 1.3, (sx * (W2 + 0.002), 1.3, 2.63)))
    body.add(chrome, box(0.03, 0.04, 0.18, (sx * (W2 + 0.012), 2.05, 2.2), r=0.01))   # door handle
    body.add(chrome, tube([(sx * 1.2, 1.5, 3.36), (sx * 1.24, 1.9, 3.38), (sx * 1.24, 2.6, 3.38), (sx * 1.2, 2.75, 3.36)], 0.016))   # grab handle
    # west-coast mirror on two arms, with a convex spotter below
    body.add(iron, tube([(sx * 1.18, 2.7, 3.3), (sx * 1.5, 2.72, 3.4), (sx * 1.52, 2.66, 3.4)], 0.016))
    body.add(iron, tube([(sx * 1.18, 2.15, 3.3), (sx * 1.5, 2.18, 3.4), (sx * 1.52, 2.24, 3.4)], 0.016))
    body.add(black, box(0.06, 0.44, 0.24, (sx * 1.53, 2.45, 3.4), r=0.025))
    body.add(chrome, box(0.01, 0.4, 0.2, (sx * 1.53, 2.45, 3.4 - 0.13)))
    body.add(black, cyl(0.09, 0.06, (sx * 1.48, 2.1, 3.48), axis="z", seg=16))
    for k in range(3):                                                           # roof marker lamps
        body.add(amber, box(0.08, 0.04, 0.05, (sx * 0.25 + (k - 1) * 0.12 * sx, 2.97, cz + 0.88), r=0.012))
# light bar across the roof, pads under the game's two beacons (+-0.8)
body.add(iron, box(1.9, 0.05, 0.14, (0, 2.98, 2.6), r=0.015))
for sx in (-0.8, 0.8):
    body.add(iron, box(0.24, 0.05, 0.24, (sx, 2.99, 2.6), r=0.02))
    body.add(iron, box(0.06, 0.1, 0.06, (sx * 0.6, 2.94, 2.6), r=0.01))
# sun visor over the windshield
body.add(black, box(2.4, 0.06, 0.24, (0, 2.84, cz + D2 + 0.1), r=0.02, rot=K.rot_game(rx=-0.2)))

# ================================================================ hood, grille, bumper
body.add(orange, box(2.26, 0.98, 1.12, (0, 1.6, 3.98), r=0.2, seg=4))
body.add(orangeD, box(2.0, 0.04, 0.8, (0, 2.09, 3.95), r=0.02))                 # hood top seam panel
body.add(frame, box(1.48, 0.72, 0.03, (0, 1.6, 4.545), r=0.02))                 # grille surround
for k in range(10):
    body.add(chrome, box(1.36, 0.03, 0.03, (0, 1.29 + k * 0.067, 4.555), r=0.006))
for k in range(5):
    body.add(chrome, box(0.025, 0.64, 0.03, (-0.56 + k * 0.28, 1.6, 4.56), r=0.006))
for sx in (-0.88, 0.88):
    body.add(iron, box(0.36, 0.22, 0.06, (sx, 1.55, 4.53), r=0.03))
    body.add(lensF, box(0.3, 0.16, 0.02, (sx, 1.55, 4.565), r=0.02))
    body.add(amber, box(0.2, 0.07, 0.03, (sx, 1.38, 4.55), r=0.01))
body.add(frame, box(2.54, 0.32, 0.28, (0, 0.95, 4.6), r=0.06))
for sx in (-0.75, 0.75):
    body.add(iron, K.torus((sx, 0.86, 4.76), ((1, 0, 0), (0, 1, 0), (0, 0, 1)), 0.06, 0.018, seg=16, rseg=6))   # tow hooks
body.add(black, box(1.0, 0.14, 0.02, (0, 0.95, 4.745)))                          # plate
# plow hitch frame on the bumper (municipal trucks carry one)
for sx in (-0.5, 0.5):
    body.add(frame, box(0.12, 0.42, 0.2, (sx, 0.72, 4.72), r=0.02))
body.add(frame, box(1.2, 0.1, 0.12, (0, 0.55, 4.78), r=0.02))

# ================================================================ spreader body (V-box)
vOut = [(-1.175, 2.62), (-1.175, 2.2), (-0.42, 1.38), (0.42, 1.38), (1.175, 2.2), (1.175, 2.62)]
vIn = [(1.115, 2.62), (1.115, 2.22), (0.395, 1.44), (-0.395, 1.44), (-1.115, 2.22), (-1.115, 2.62)]
body.add(galv, K.slab_xy(vOut + vIn, 4.2, -1.2))
for z in (-3.32 + 0.025, 0.88 + 0.025):
    body.add(galv, K.slab_xy(vOut, 0.05, z))
for sx in (-1, 1):
    body.add(orange, box(0.08, 0.16, 4.26, (sx * 1.2, 2.64, -1.2), r=0.03))     # top rails
    for k in range(6):
        z = -3.1 + k * 0.76
        body.add(galv, K.beam((sx * 1.2, 2.58, z), (sx * 1.2, 2.2, z), 0.05, 0.08, r=0.012))
        body.add(galv, K.beam((sx * 1.2, 2.2, z), (sx * 0.45, 1.36, z), 0.05, 0.08, r=0.012))
    body.add(galv, box(0.06, 0.06, 4.2, (sx * 1.2, 2.2, -1.2), r=0.015))         # knee rail
    body.add(frame, box(0.14, 0.14, 4.3, (sx * 0.45, 1.3, -1.2), r=0.02))        # long sills on the chassis
# top screen grate across the open top (thin bars), the salt load shows through
for k in range(9):
    body.add(iron, box(2.28, 0.02, 0.02, (0, 2.66, -3.0 + k * 0.45)))
# conveyor drive, chain chute, spinner motor and guard, ladder, lights, hazard band
body.add(galv, box(0.52, 0.36, 0.92, (0, 1.25, -3.55), r=0.05))
body.add(iron, cyl(0.12, 0.3, (0.34, 1.25, -3.85), axis="x", seg=16))
body.add(iron, cyl(0.1, 0.22, (0, 1.12, -3.95), seg=16))                         # spinner motor above the disc
body.add(galv, box(0.06, 0.05, 0.6, (0, 1.24, -3.75), r=0.01))
body.add(iron, tube([(-0.55, 0.9, -3.4), (-0.6, 0.88, -3.95), (-0.48, 0.86, -4.42), (0, 0.86, -4.5), (0.48, 0.86, -4.42), (0.6, 0.88, -3.95), (0.55, 0.9, -3.4)], 0.018, seg=8))
for x in (0.82, 1.08):
    body.add(iron, box(0.035, 1.3, 0.035, (x, 1.95, -3.38), r=0.01))
for k in range(5):
    body.add(iron, box(0.28, 0.035, 0.05, (0.95, 1.5 + k * 0.24, -3.38), r=0.01))
for sx in (-0.8, 0.8):
    body.add(iron, box(0.26, 0.17, 0.06, (sx, 1.3, -3.5), r=0.02))
    body.add(lensR, box(0.22, 0.13, 0.02, (sx, 1.3, -3.535), r=0.01))
    body.add(amber, box(0.1, 0.1, 0.04, (sx * 1.3, 2.55, -3.34), r=0.02))
K.hazard(body, hz_y, hz_k, 2.0, 0.14, (0, 1.08, -3.35), normal_z=-1, stripes=13)
body.add(black, box(0.5, 0.14, 0.02, (-0.55, 0.85, -3.36)))                      # plate

# spinner: disc with fins
spinner.add(steel, cyl(0.42, 0.04, (0, 0.95, -3.95), seg=36, bevel=0.01))
for k in range(4):
    a = k * math.pi / 4
    spinner.add(iron, box(0.05, 0.1, 0.78, (0, 1.01, -3.95), r=0.012, rot=K.rot_game(ry=a)))
spinner.add(iron, cyl(0.07, 0.12, (0, 1.02, -3.95), seg=16))
# the salt load's top surface; the game lowers and narrows it as the tank empties
salt.add(saltM, K.bumpy_top(2.16, 3.96, 2.56, (0, -1.2), amp=0.06, seed=4))

# ================================================================ wheels
wheels = []
for z, drive in ((3.6, False), (-1.3, True), (-2.55, True)):
    for xs in (1, -1):
        x = xs * (1.1 if z > 0 else 1.12)
        axle = 1 if z > 0 else (2 if z > -2 else 3)
        p = (x, R_W, z)
        w = K.Part(f"wheel_{axle}_{'left' if xs > 0 else 'right'}", p, body)
        car, blocks = K.road_tyre(R_W, W_W, p, blocks=26 if drive else 0)
        w.add(rubber, car)
        if drive:
            w.add(rubber, blocks)
        rim, holes, hub = K.steel_rim(R_W, W_W, p, out_sign=xs)
        w.add(rimM, rim)
        w.add(black, holes)
        w.add(chrome, hub)
        wheels.append(w)

# ================================================================ cockpit
M = CP.Mats(accent=0xe8692c)
cab = K.Part("cab_interior", (0, 0, 0), body)
FZ, BZ, HW = cz + D2 - 0.06, cz - D2 + 0.06, W2 - 0.06
cab.add(M.floor, box(HW * 2 - 0.04, 0.02, FZ - BZ - 0.04, (0, FL + 0.01, cz), r=0.008))
for k in range(12):
    cab.add(M.floor, box(0.7, 0.008, 0.02, (0.5, FL + 0.024, 2.4 + k * 0.08)))
# dashboard: full width, low under the windshield, a driver's binnacle and a centre stack angled to the driver
DASH = [(FZ, FL), (FZ, 2.08), (FZ - 0.16, 2.14), (3.12, 2.12), (3.02, 1.98), (3.06, 1.62), (3.14, FL)]
cab.add(M.dash, K.plate(DASH, HW * 2 - 0.02, 0, r=0.03, seg=3))
cab.add(M.trim, box(HW * 2 - 0.04, 0.025, 0.32, (0, 2.145, FZ - 0.2), r=0.01, rot=K.rot_game(rx=-0.06)))
for sx in (-0.85, -0.25, 0.85):                                                  # dash vents
    cab.add(M.trim, box(0.18, 0.07, 0.03, (sx, 2.03, 3.035), r=0.012, rot=K.rot_game(rx=-0.35)))
    for k in range(4):
        cab.add(M.black, box(0.16, 0.006, 0.01, (sx, 2.005 + k * 0.016, 3.026), rot=K.rot_game(rx=-0.35)))
needles = CP.dial_pod(cab, M, (0.5, 2.24, 3.14), EYE,
                      [("rpm", -0.11, 0.0, 0.07), ("speed", 0.11, 0.0, 0.07), ("fuel", -0.215, -0.03, 0.035), ("temp", 0.215, -0.03, 0.035)],
                      pod_size=(0.54, 0.2))
CP.screen(cab, M, (-0.05, 2.08, 3.09), EYE, w=0.22, h=0.14)
# switch bank below the screen, and the spreader panel the game lights (its lamp sits at x 0.2, y 2.18, z 3.1)
for r_ in range(2):
    for c_ in range(5):
        cab.add(M.btn, box(0.035, 0.03, 0.02, (-0.15 + c_ * 0.05, 1.9 - r_ * 0.05, 3.03 + r_ * 0.008), r=0.006, rot=K.rot_game(rx=-0.3)))
        cab.add(M.lamps[(r_ * 5 + c_) % 6], box(0.01, 0.006, 0.004, (-0.15 + c_ * 0.05, 1.912 - r_ * 0.05, 3.02 + r_ * 0.008)))
cab.add(M.dash, box(0.18, 0.1, 0.06, (0.2, 2.15, 3.125), r=0.015, rot=K.rot_game(rx=-0.35)))
# engine tunnel and console carrying the gear lever (the game's shifter pivot is at 0.05, 1.95, 2.6)
cab.add(M.dash, box(0.44, 1.95 - FL - 0.03, 0.9, (0.05, (1.95 + FL - 0.03) / 2, 2.65), r=0.05, seg=3))
cab.add(M.trim, box(0.4, 0.02, 0.86, (0.05, 1.925, 2.65), r=0.008))
cab.add(M.btn, box(0.14, 0.012, 0.1, (0.05, 1.94, 2.85), r=0.004))
stick = CP.lever(cab, M, "joystick", (0.05, 1.95, 2.6), length=0.26, grip="knob")
# steering wheel on the game's hub: tilted 0.62 rad, radius 0.23
sw = CP.steering_wheel(cab, M, (0.5, 2.25, 2.87), 0.62, r=0.23, column=0.32, knob=False)
CP.pedals(cab, M, 0.5, FL, 3.0, pairs=((0.16, 0.22), (-0.05, 0.24), (-0.2, 0.2)))
CP.seat(cab, M, 0.5, FL, 2.36, 1.8, width=0.52)
CP.seat(cab, M, -0.62, FL, 2.36, 1.74, width=0.5, suspension=False)
cab.add(M.iron, box(0.42, 1.74 - FL - 0.12, 0.42, (-0.62, (1.74 + FL - 0.12) / 2, 2.36), r=0.03))
# walls: door panels below the side windows, A-pillar trim, back wall and headliner
for sx in (-1, 1):
    cab.add(M.liner, box(0.03, SW["y0"] - FL - 0.04, SW["z1"] - SW["z0"] + 0.1, (sx * (W2 - 0.075), (SW["y0"] + FL) / 2, (SW["z0"] + SW["z1"]) / 2), r=0.01))
    cab.add(M.trim, box(0.07, 0.07, SW["z1"] - SW["z0"] + 0.1, (sx * (W2 - 0.09), SW["y0"] - 0.02, (SW["z0"] + SW["z1"]) / 2), r=0.02))  # arm rest sill
    cab.add(M.trim, box(0.1, 0.72, 0.12, (sx * (W2 - 0.1), 2.45, FZ - 0.04), r=0.03))                                               # A-pillar
    cab.add(M.chrome, box(0.03, 0.03, 0.14, (sx * (W2 - 0.1), 2.0, 2.3), r=0.01))                                                     # door pull
cab.add(M.liner, box(HW * 2 - 0.04, 2.78 - FL, 0.03, (0, (2.78 + FL) / 2, BZ + 0.015)))
cab.add(M.liner, box(HW * 2 - 0.04, 0.03, FZ - BZ, (0, 2.78, cz), r=0.01))
cab.add(M.trim, box(HW * 2 - 0.1, 0.1, 0.34, (0, 2.72, FZ - 0.22), r=0.03))     # overhead console
cab.add(K.mat("radio_display", 0x0c1a2a, rough=0.2, emit=0x2a6a9a, emit_strength=0.6), box(0.2, 0.005, 0.05, (-0.35, 2.668, FZ - 0.2)))
for sx in (-0.75, 0.0, 0.75):
    cab.add(M.black, cyl(0.05, 0.02, (sx, 2.665, FZ - 0.3), seg=20))
cab.add(M.dome, box(0.2, 0.015, 0.08, (0, 2.765, cz - 0.1), r=0.006))
for sx in (0.5, -0.6):
    cab.add(M.black, box(0.6, 0.02, 0.22, (sx, 2.72, FZ - 0.48), r=0.01, rot=K.rot_game(rx=0.3)))             # sun visors
cab.add(M.chrome, box(0.24, 0.08, 0.015, (0.1, 2.66, FZ - 0.12), r=0.01))         # rear-view mirror
cab.add(M.red, cyl(0.05, 0.32, (-0.15, FL + 0.18, BZ + 0.12), seg=20, bevel=0.02))
cab.add(M.black, box(0.3, 0.2, 0.18, (-0.55, 2.62, BZ + 0.12), r=0.02))          # radio box on the back wall

# ================================================================ build, export, preview
objs = []
for part in (body, spinner, salt, *wheels, cab, sw, stick, *needles):
    objs += part.build()
tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
print(f"salttruck: about {tris} triangles")
out = os.path.abspath(opt.get("out", os.path.join(os.path.dirname(__file__), "..", "..", "assets", "models", "salttruck.glb")))
C.export_glb(out)
print("exported", out, os.path.getsize(out) // 1024, "KB")
if opt.get("preview"):
    d = opt["preview"]
    for name, az, el, dist in (("front", 35, 14, 12), ("rear", 215, 18, 12), ("side", 95, 6, 11)):
        C.preview(os.path.join(d, f"salttruck_{name}.png"), target=(0, 0.0, 1.6), dist=dist, az=az, el=el, size=(1000, 650), samples=32)
    eye = G(*EYE)
    for nm, look, lens in (("cab_ahead", G(0.5, 2.3, 5.0), 22), ("cab_dash", G(0.4, 2.15, 3.1), 30)):
        C.preview(os.path.join(d, f"salttruck_{nm}.png"), size=(1000, 650), samples=48, cam_at=eye, look_at=look, lens=lens)
