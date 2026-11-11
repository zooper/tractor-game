"""Wheel loader -> assets/models/loader.glb

    blender --background --factory-startup --python tools/blender/loader.py -- [--out PATH] [--preview DIR]

All sizes and pivots are in game coordinates (see kit.py) and match the code-built loader in index.html,
so the game's joints, hydraulic rams, cab view and physics line up with this model.
"""
import math
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(__file__))
import common as C  # noqa: E402
import kit as K  # noqa: E402
from kit import G, box, cyl, plate, tube, arc_shell, merge  # noqa: E402

opt = C.args()
C.reset()

HALF_WB, ARM_L = 1.25, 2.6
ARM_PIVOT = (0, 1.75, 0.7)
CZ = -0.6                    # cab centre along z
R_WHEEL, W_WHEEL = 0.70, 0.58

# ---------------------------------------------------------------- materials
yellow = K.mat("paint_yellow", rough=0.42, metal=0.05, image=K.grime_image("grime_yellow", 0xd9a21b, 1.0, seed=3))
yellowD = K.mat("paint_yellow_dark", rough=0.48, metal=0.05, image=K.grime_image("grime_yellow_dark", 0xb8860f, 1.1, seed=5))
frame = K.mat("frame_dark", rough=0.55, metal=0.25, image=K.grime_image("grime_dark", 0x2f2d2a, 0.8, seed=7))
orange = K.mat("paint_orange", rough=0.45, metal=0.05, image=K.grime_image("grime_orange", 0xe8692c, 0.9, seed=11))
black = K.mat("black_plastic", 0x171717, rough=0.55)
rubber = K.mat("tyre_rubber", 0x1b1b1b, rough=0.9)
steel = K.mat("steel_worn", 0x8a8880, rough=0.35, metal=0.9)
chrome = K.mat("chrome", 0xdadcdf, rough=0.15, metal=1.0)
iron = K.mat("iron", 0x2c2c2e, rough=0.5, metal=0.6)
glass = K.mat("glass", 0x2a3a40, rough=0.04, metal=0.1, alpha=0.38)
lensF = K.mat("light_front", 0xfff4dc, rough=0.05, emit=0xfff0d0, emit_strength=2.0)
lensR = K.mat("light_rear", 0x9c1c14, rough=0.1, emit=0xb0170f, emit_strength=1.0)
hazard_y = K.mat("hazard_yellow", 0xf2c21a, rough=0.5)
hazard_k = K.mat("hazard_black", 0x141414, rough=0.5)

# ---------------------------------------------------------------- pivots
rear = K.Part("frame_rear")
front = K.Part("frame_front")
arm = K.Part("arm", ARM_PIVOT, front)
bucket = K.Part("bucket", (0, ARM_PIVOT[1], ARM_PIVOT[2] + ARM_L), arm)
plow = K.Part("plow", (0, ARM_PIVOT[1], ARM_PIVOT[2] + ARM_L), arm)
mount = bpy.data.objects.new("mount_beacon", None)
mount.location = G(0, 3.24, CZ + 0.2)
bpy.context.collection.objects.link(mount)
mount.parent = rear.empty


def at(part, x, y, z):
    """game position relative to a part's pivot -> absolute game position"""
    w = part.world
    return (x + w.x, y + w.z, z - w.y)


def hazard(part, w, h, pos, normal_z=1, stripes=9):
    """yellow plate with slanted black bands, facing +z (normal_z=1) or -z"""
    x0, y0, z0 = pos
    part.add(hazard_y, box(w, h, 0.012, pos))
    band = w / stripes
    skew = h * 0.7                                  # how far a band leans over its height
    x, k = x0 - w / 2 - skew, 0
    while x < x0 + w / 2:
        if k % 2 == 0:
            # parallelogram, clipped to the plate's ends
            lo0, lo1, hi0, hi1 = x, x + band, x + skew, x + band + skew
            clip = lambda v: max(x0 - w / 2, min(x0 + w / 2, v))
            pts = [(clip(lo0), y0 - h / 2), (clip(lo1), y0 - h / 2), (clip(hi1), y0 + h / 2), (clip(hi0), y0 + h / 2)]
            if pts[1][0] - pts[0][0] > 1e-3 or pts[2][0] - pts[3][0] > 1e-3:
                pts = [p for i, p in enumerate(pts) if i == 0 or abs(p[0] - pts[i - 1][0]) > 1e-4 or abs(p[1] - pts[i - 1][1]) > 1e-4]
                if len(pts) >= 3:
                    part.add(hazard_k, K.slab_xy(pts, 0.004, z0 + normal_z * 0.008))
        x += band
        k += 1


# ================================================================ rear frame: chassis, engine, cab
side_prof = [(0.05, 0.55), (-2.55, 0.55), (-2.55, 1.15), (-0.2, 1.15), (0.05, 0.85)]
for x in (-0.62, 0.62):
    rear.add(frame, plate(side_prof, 0.16, x, r=0.02))
rear.add(frame, box(1.4, 0.3, 2.4, (0, 0.72, -1.3), r=0.05))                    # belly pan
# engine hood: main body, a slightly narrower top that slopes down toward the back, side doors
rear.add(yellow, box(1.86, 0.84, 1.75, (0, 1.55, -1.55), r=0.12, seg=4))
rear.add(yellow, plate([(-0.68, 1.96), (-2.42, 1.9), (-2.42, 2.02), (-0.68, 2.1)], 1.72, 0, r=0.05, seg=3))
for sx in (-1, 1):
    x = sx * 0.935
    for k in range(8):                                                           # side louvres: real slats
        rear.add(iron, box(0.025, 0.035, 0.95, (x, 1.3 + k * 0.065, -1.65), rot=K.rot_game(rz=sx * 0.5)))
    rear.add(frame, box(0.02, 0.6, 1.05, (x - sx * 0.006, 1.52, -1.65)))       # dark recess behind the slats
    for z in (-0.85, -2.25):                                                     # door hinges and latch
        rear.add(iron, cyl(0.018, 0.12, (x + sx * 0.012, 1.86, z), axis="z", seg=10))
    rear.add(iron, box(0.02, 0.06, 0.14, (x + sx * 0.015, 1.45, -0.82), r=0.008))
    rear.add(frame, box(0.012, 0.75, 0.012, (x + sx * 0.002, 1.55, -0.78)))      # door seam
# counterweight with hazard stripes, tail lights, radiator grille
rear.add(yellowD, box(2.12, 0.86, 0.56, (0, 1.15, -2.42), r=0.16, seg=4))
hazard(rear, 1.7, 0.2, (0, 1.28, -2.706), normal_z=-1)
for sx in (-0.82, 0.82):
    rear.add(iron, box(0.24, 0.16, 0.06, (sx, 1.0, -2.69), r=0.02))
    rear.add(lensR, box(0.2, 0.12, 0.02, (sx, 1.0, -2.72), r=0.006))
    rear.add(iron, box(0.16, 0.12, 0.06, (sx * 0.68, 1.0, -2.69), r=0.02))
    rear.add(lensF, box(0.12, 0.08, 0.02, (sx * 0.68, 1.0, -2.72), r=0.006))
rear.add(frame, box(1.36, 0.5, 0.04, (0, 1.75, -2.43), r=0.01))                 # grille frame
for k in range(9):
    rear.add(iron, box(1.28, 0.025, 0.035, (0, 1.53 + k * 0.05, -2.45), rot=K.rot_game(rx=0.6)))
rear.add(frame, box(1.6, 0.18, 0.12, (0, 0.62, -2.62), r=0.03))                 # tow hitch bar
rear.add(iron, cyl(0.05, 0.2, (0, 0.62, -2.72), axis="y", seg=12))
# exhaust stack with heat shield and rain cap, air pre-cleaner
rear.add(iron, cyl(0.075, 0.78, (0.48, 2.35, -1.95), seg=20))
rear.add(frame, cyl(0.1, 0.36, (0.48, 2.2, -1.95), seg=20))
rear.add(iron, box(0.2, 0.025, 0.2, (0.48, 2.76, -1.98), r=0.01, rot=K.rot_game(rx=-0.35)))
rear.add(black, cyl(0.13, 0.32, (-0.45, 2.22, -1.35), seg=24, bevel=0.02))
rear.add(black, cyl(0.15, 0.06, (-0.45, 2.41, -1.35), seg=24, bevel=0.02))
# rear fenders, steps up to the cab, handrails
for sx in (-1.05, 1.05):
    rear.add(yellow, arc_shell(0.86, 0.66, math.radians(30), math.radians(170), 0.03, (sx, 0.7, -HALF_WB)))
    rear.add(frame, box(0.1, 0.08, 0.5, (sx * 0.86, 1.05, -0.7), r=0.02))       # fender mount
for k in range(3):
    rear.add(iron, box(0.36, 0.035, 0.24, (-0.98, 0.62 + k * 0.38, -0.32), r=0.01))
    for gx in range(5):                                                          # anti-slip tread holes
        rear.add(frame, box(0.04, 0.04, 0.16, (-1.12 + gx * 0.07, 0.638 + k * 0.38, -0.32)))
for sx in (-1.12, -0.84):
    rear.add(iron, box(0.025, 0.9, 0.03, (sx, 1.0, -0.2), r=0.008))             # step stringers
rear.add(iron, tube([(-1.12, 0.6, -0.48), (-1.14, 1.4, -0.48), (-1.08, 2.0, -0.5)], 0.022))
for sx in (-1, 1):
    rear.add(iron, tube([(sx * 0.92, 2.12, -0.95), (sx * 0.95, 2.2, -1.6), (sx * 0.92, 2.14, -2.25)], 0.02))
# articulation hitch, pin, steering ram lugs, rear axle
rear.add(frame, box(0.9, 0.5, 0.5, (0, 1.0, -0.3), r=0.05))
rear.add(iron, cyl(0.13, 1.0, (0, 1.0, 0), seg=24, bevel=0.02))
for sx in (-0.42, 0.42):
    rear.add(frame, box(0.08, 0.2, 0.22, (sx, 1.0, -0.55), r=0.02))
    rear.add(iron, cyl(0.05, 0.14, (sx, 1.0, -0.55), axis="x", seg=12))
rear.add(iron, cyl(0.17, 1.6, (0, 0.7, -HALF_WB), axis="x", seg=24))
for sx in (-0.82, 0.82):
    rear.add(iron, cyl(0.26, 0.16, (sx, 0.7, -HALF_WB), axis="x", seg=24, bevel=0.02))   # final drives

# ---- cab: the interior the game draws sits in x +-0.68, z -1.25..0.05, floor 1.79, roof 3.05
rear.add(frame, box(1.42, 0.16, 1.42, (0, 1.72, CZ), r=0.04))
for px, pz in ((-0.66, -0.63), (0.66, -0.63), (-0.66, 0.63), (0.66, 0.63)):
    rear.add(frame, box(0.09, 1.38, 0.09, (px, 2.42, CZ + pz), r=0.025))
for px in (-0.66, 0.66):                                                         # rear-pillar gussets
    rear.add(frame, box(0.06, 0.16, 0.2, (px, 3.0, CZ - 0.55), r=0.02))
glass_panes = [(1.24, 0.012, 0, 0.655), (1.24, 0.012, 0, -0.655), (0.012, 1.2, -0.665, 0), (0.012, 1.2, 0.665, 0)]
for w, d, px, pz in glass_panes:
    rear.add(glass, box(w, 1.2, d, (px, 2.43, CZ + pz)))
for x in (-0.69, 0.69):
    rear.add(frame, box(0.05, 0.05, 1.28, (x, 1.98, CZ), r=0.012))
rear.add(frame, box(1.3, 0.05, 0.05, (0, 1.98, CZ + 0.66), r=0.012))
# door on the left side: frame, handle, hinges
rear.add(frame, box(0.03, 1.16, 0.04, (0.672, 2.4, CZ - 0.05), r=0.01))
rear.add(chrome, box(0.03, 0.04, 0.16, (0.69, 2.2, CZ + 0.45), r=0.01))
for y in (1.95, 2.85):
    rear.add(iron, cyl(0.02, 0.1, (0.68, y, CZ - 0.6), seg=10))
# roof: overhanging canopy, top panel, AC unit, work lights, beacon mount, wiper, mirrors
rear.add(yellow, box(1.6, 0.12, 1.64, (0, 3.11, CZ + 0.02), r=0.05, seg=4))
rear.add(yellowD, box(1.3, 0.06, 1.2, (0, 3.2, CZ - 0.05), r=0.03))
rear.add(black, box(0.7, 0.14, 0.4, (0, 3.29, CZ - 0.5), r=0.04))
for k in range(5):
    rear.add(iron, box(0.6, 0.012, 0.03, (0, 3.365, CZ - 0.64 + k * 0.07)))
for sx in (-0.55, 0.55):
    rear.add(iron, box(0.26, 0.15, 0.12, (sx, 3.02, CZ + 0.8), r=0.03))
    rear.add(lensF, box(0.21, 0.1, 0.02, (sx, 3.02, CZ + 0.865), r=0.008))
for sx in (-0.5, 0.5):
    rear.add(iron, box(0.2, 0.12, 0.1, (sx, 3.02, CZ - 0.82), r=0.03))
    rear.add(lensF, box(0.15, 0.08, 0.02, (sx, 3.02, CZ - 0.875), r=0.008))
rear.add(iron, box(0.3, 0.03, 0.2, (0, 3.235, CZ + 0.2), r=0.01))              # beacon base plate
rear.add(black, box(0.02, 0.6, 0.015, (0.2, 2.36, CZ + 0.672), rot=K.rot_game(rz=0.5)))
for sd in (-1, 1):
    rear.add(iron, tube([(sd * 0.7, 2.9, CZ + 0.6), (sd * 0.95, 2.92, CZ + 0.62), (sd * 1.02, 2.75, CZ + 0.62)], 0.015))
    rear.add(black, box(0.05, 0.32, 0.22, (sd * 1.03, 2.6, CZ + 0.62), r=0.02))
    rear.add(chrome, box(0.01, 0.28, 0.18, (sd * 1.0, 2.6, CZ + 0.62)))

# ================================================================ front frame
fr_prof = [(0.1, 0.55), (2.0, 0.55), (2.0, 0.95), (1.55, 1.55), (0.85, 1.6), (0.1, 1.15)]
for x in (-0.58, 0.58):
    front.add(frame, plate(fr_prof, 0.18, x, r=0.02))
    # arm-pivot towers up to the pin, with a boss
    front.add(frame, plate([(0.35, 1.1), (1.05, 1.1), (0.85, 1.85), (0.55, 1.85)], 0.14, x * 1.16, r=0.015))
    front.add(iron, cyl(0.12, 0.2, (x * 1.16, ARM_PIVOT[1], ARM_PIVOT[2]), axis="x", seg=20, bevel=0.015))
front.add(frame, box(1.0, 0.36, 1.7, (0, 0.78, 1.1), r=0.05))
front.add(frame, box(0.7, 0.45, 0.5, (0, 1.0, 0.25), r=0.05))
front.add(frame, box(1.32, 0.3, 0.3, (0, 0.85, 1.95), r=0.05))                  # front cross member / bumper
front.add(iron, cyl(0.17, 1.6, (0, 0.7, HALF_WB), axis="x", seg=24))
for sx in (-0.82, 0.82):
    front.add(iron, cyl(0.26, 0.16, (sx, 0.7, HALF_WB), axis="x", seg=24, bevel=0.02))
for sx in (-1.05, 1.05):
    front.add(yellow, arc_shell(0.86, 0.66, math.radians(10), math.radians(150), 0.03, (sx, 0.7, HALF_WB)))
for sx in (-0.78, 0.78):
    front.add(iron, box(0.24, 0.17, 0.13, (sx, 1.62, 1.72), r=0.04))
    front.add(lensF, box(0.18, 0.11, 0.02, (sx, 1.62, 1.79), r=0.01))
# ram lugs: lift rams low at the front, tilt ram on top, steering rams at the joint
for sx in (-0.55, 0.55):
    front.add(frame, box(0.07, 0.22, 0.24, (sx + (0.06 if sx > 0 else -0.06), 0.95, 1.5), r=0.02))
    front.add(iron, cyl(0.05, 0.22, (sx, 0.95, 1.5), axis="x", seg=12))
front.add(frame, box(0.3, 0.2, 0.2, (0, 1.5, 1.05), r=0.03))
front.add(iron, cyl(0.05, 0.34, (0, 1.55, 1.05), axis="x", seg=12))
for sx in (-0.42, 0.42):
    front.add(frame, box(0.08, 0.2, 0.22, (sx, 1.0, 0.45), r=0.02))
    front.add(iron, cyl(0.05, 0.14, (sx, 1.0, 0.45), axis="x", seg=12))

# ================================================================ lift arms (arm-local profile, offset by the pivot)
arm_prof = [(-0.12, -0.17), (0.9, -0.05), (1.9, -0.2), (ARM_L + 0.14, -0.12), (ARM_L + 0.14, 0.13), (1.9, 0.12), (0.9, 0.26), (-0.12, 0.16)]
apos = (0, ARM_PIVOT[1], ARM_PIVOT[2])
for x in (-0.78, 0.78):
    arm.add(yellow, plate(arm_prof, 0.2, x, r=0.03, seg=3, offset=apos))
    arm.add(iron, cyl(0.11, 0.26, at(arm, x, 0, 0), axis="x", seg=20, bevel=0.015))
    arm.add(iron, cyl(0.1, 0.26, at(arm, x, 0, ARM_L), axis="x", seg=20, bevel=0.015))
    arm.add(yellowD, plate([(1.05, -0.12), (1.45, -0.12), (1.4, -0.24), (1.1, -0.24)], 0.06, x * 0.71, r=0.01, offset=apos))  # lift ram lugs
arm.add(iron, cyl(0.05, 1.2, at(arm, 0, -0.12, 1.25), axis="x", seg=12))
arm.add(yellow, cyl(0.13, 1.5, at(arm, 0, 0.06, ARM_L * 0.58), axis="x", seg=24, bevel=0.02))
arm.add(yellowD, plate([(-0.15, -0.1), (0.25, -0.25), (0.42, 0.45), (0.05, 0.6)], 0.16, 0, r=0.02, offset=(0, ARM_PIVOT[1], ARM_PIVOT[2] + ARM_L * 0.52)))  # tilt bellcrank
arm.add(iron, cyl(0.05, 0.2, at(arm, 0, 0.5, ARM_L * 0.52 + 0.1), axis="x", seg=12))
for sd in (-1, 1):                                                               # hoses along the arms
    arm.add(black, tube([at(arm, sd * 0.62, 0.22, 0.2), at(arm, sd * 0.64, 0.3, 1.2), at(arm, sd * 0.64, 0.2, 2.1), at(arm, sd * 0.6, 0.05, ARM_L - 0.1)], 0.022))

# ================================================================ bucket
bpos = (0, ARM_PIVOT[1], ARM_PIVOT[2] + ARM_L)
inner = [(1.18, -0.57), (0.25, -0.57), (0.02, -0.5), (-0.09, -0.3), (-0.1, 0.0), (-0.05, 0.3), (0.05, 0.47), (0.36, 0.52)]
outer = []
for i, (z, y) in enumerate(inner):
    z0, y0 = inner[max(0, i - 1)]
    z1, y1 = inner[min(len(inner) - 1, i + 1)]
    tz, ty = z1 - z0, y1 - y0
    l = math.hypot(tz, ty) or 1
    outer.append((z - ty / l * 0.07, y + tz / l * 0.07))
bucket.add(yellowD, plate(inner + outer[::-1], 2.44, 0, r=0.015, offset=bpos))
for x in (-1.25, 1.25):
    bucket.add(yellow, plate([(-0.1, -0.62), (1.2, -0.62), (1.22, -0.48), (0.42, 0.55), (-0.1, 0.55)], 0.06, x, r=0.012, offset=bpos))
    bucket.add(steel, plate([(0.5, -0.62), (1.21, -0.62), (1.22, -0.5), (0.9, -0.2)], 0.07, x, r=0.01, offset=bpos))   # side cutters
bucket.add(steel, box(2.56, 0.07, 0.18, at(bucket, 0, -0.58, 1.2), r=0.02))
for t in range(8):
    tx = -1.12 + t * 0.32
    bucket.add(iron, box(0.14, 0.1, 0.12, at(bucket, tx, -0.57, 1.26), r=0.02))                       # adapters
    bucket.add(steel, cyl(0.055, 0.22, at(bucket, tx, -0.57, 1.42), axis="z", seg=4, r2=0.012, rot=K.rot_game(rz=math.pi / 4)))
for zz in (0.35, 0.7, 1.0):
    bucket.add(steel, box(2.3, 0.025, 0.1, at(bucket, 0, -0.6, zz), r=0.008))
for x in (-0.35, 0.35):
    bucket.add(yellowD, box(0.12, 0.5, 0.18, at(bucket, x, 0.2, -0.13), r=0.03))
    bucket.add(iron, cyl(0.06, 0.18, at(bucket, x, 0.2, -0.13), axis="x", seg=14))
for x in (-0.9, 0.0, 0.9):                                                       # back ribs
    bucket.add(yellowD, box(0.06, 0.6, 0.06, at(bucket, x, 0.05, -0.14), r=0.015))

# ================================================================ plow (same pivot as the bucket)
PZ = 0.45                                       # the blade sits 0.45 m ahead of the coupler
MB_C, MB_R, MB_T0, MB_T1 = (1.385 + PZ, 0.166), 1.0, 2.506, 3.626
arc = [(MB_C[0] + math.cos(MB_T0 + (MB_T1 - MB_T0) * k / 24) * MB_R, MB_C[1] + math.sin(MB_T0 + (MB_T1 - MB_T0) * k / 24) * MB_R) for k in range(25)]
(tz, ty), (bz, by) = arc[0], arc[-1]
back, dep = (-0.997, 0.0753), 0.19
T_b, B_b = (tz + back[0] * dep, ty + back[1] * dep), (bz + back[0] * dep, by + back[1] * dep)
# moldboard: a 15 mm sheet following the arc
face = arc + [(z + (z - MB_C[0]) / MB_R * 0.015, y + (y - MB_C[1]) / MB_R * 0.015) for z, y in arc[::-1]]
plow.add(orange, plate(face, 3.4, 0, r=0.004, seg=1, offset=bpos))
for x in (-1.72, 1.72):
    plow.add(orange, plate(arc + [B_b, T_b], 0.05, x, r=0.01, offset=bpos))
plow.add(orange, plate([T_b, B_b, (B_b[0] - 0.03, B_b[1]), (T_b[0] - 0.03, T_b[1])], 3.44, 0, r=0.008, offset=bpos))
for f in (0.3, 0.7):
    z = B_b[0] + (T_b[0] - B_b[0]) * f - 0.05
    y = B_b[1] + (T_b[1] - B_b[1]) * f
    plow.add(orange, box(3.3, 0.1, 0.07, at(plow, 0, y, z), r=0.02))
for x in (-1.2, -0.4, 0.4, 1.2):                                                 # vertical ribs on the back sheet
    plow.add(orange, box(0.05, 0.9, 0.05, at(plow, x, (ty + by) / 2, (T_b[0] + B_b[0]) / 2 - 0.05), r=0.012))
plow.add(steel, box(3.46, 0.1, 0.12, at(plow, 0, by - 0.02, bz + 0.02), r=0.02))
for k in range(12):                                                              # cutting-edge bolts
    plow.add(iron, cyl(0.018, 0.02, at(plow, -1.6 + k * 0.29, by + 0.01, bz + 0.085), axis="z", seg=8))
plow.add(orange, box(3.44, 0.07, 0.26, at(plow, 0, ty + 0.03, (tz + T_b[0]) / 2), r=0.025))
hazard(plow, 3.38, 0.05, at(plow, 0, ty + 0.03, tz + 0.12), normal_z=1, stripes=21)
for x in (-1.72, 1.72):
    plow.add(black, cyl(0.012, 1.2, at(plow, x, ty + 0.62, T_b[0] + 0.05), seg=8))
    plow.add(orange, cyl(0.03, 0.18, at(plow, x, ty + 1.25, T_b[0] + 0.05), seg=12))
# mounting frame: mount block, pivot pin, struts out to the back sheet, coupler beam across the arm tips
plow.add(frame, box(0.9, 0.42, 0.4, at(plow, 0, 0.05, 0.23), r=0.05))
plow.add(iron, cyl(0.09, 0.5, at(plow, 0, 0.05, 0.08), seg=20, bevel=0.015))
# push frame: an A-frame of heavy beams from the pivot out to the back of the blade, braced across,
# with hinge brackets bolted to the back sheet, so the blade is visibly carried by the loader
sheet_z = (T_b[0] + B_b[0]) / 2 - 0.03          # back face of the back sheet, plow-local
sheet_y = (T_b[1] + B_b[1]) / 2
for sd in (-1, 1):
    plow.add(frame, K.beam(at(plow, sd * 0.18, 0.05, 0.12), at(plow, sd * 0.95, sheet_y - 0.05, sheet_z - 0.04), 0.16, 0.18, r=0.03))
    plow.add(frame, box(0.08, 0.5, 0.12, at(plow, sd * 0.95, sheet_y, sheet_z - 0.06), r=0.02))         # hinge bracket
    plow.add(iron, cyl(0.035, 0.3, at(plow, sd * 0.95, sheet_y, sheet_z - 0.06), axis="x", seg=12))
    plow.add(iron, K.beam(at(plow, sd * 0.55, 0.18, 0.35), at(plow, sd * 0.62, sheet_y + 0.3, sheet_z - 0.05), 0.05, 0.05, r=0.012))  # trip springs
plow.add(frame, K.beam(at(plow, -0.62, 0.05, 0.5), at(plow, 0.62, 0.05, 0.5), 0.14, 0.14, r=0.03))      # cross brace
plow.add(frame, K.beam(at(plow, 0, 0.05, 0.2), at(plow, 0, sheet_y - 0.05, sheet_z - 0.04), 0.18, 0.2, r=0.03))  # centre spine
plow.add(frame, box(0.3, 0.5, 0.1, at(plow, 0, sheet_y, sheet_z - 0.05), r=0.02))
plow.add(frame, box(1.82, 0.3, 0.26, at(plow, 0, 0.02, 0.08), r=0.05))

# ================================================================ wheels
wheels = []
for zsign, parent in ((1, front), (-1, rear)):
    for xsign in (1, -1):
        name = f"wheel_{'front' if zsign > 0 else 'rear'}_{'left' if xsign > 0 else 'right'}"
        p = (xsign * 1.05, R_WHEEL, zsign * HALF_WB)
        w = K.Part(name, p, parent)
        carcass, lugs = K.earthmover_tyre(R_WHEEL, W_WHEEL, p)
        w.add(rubber, carcass)
        w.add(rubber, lugs)
        rim, nuts = K.dished_rim(R_WHEEL, W_WHEEL, p, out_sign=xsign)
        w.add(yellow, rim)
        w.add(chrome, nuts)
        wheels.append(w)

# ================================================================ cockpit (shown by the game only in cab view)
# Laid out around the game's eye point and its cab box (x +-0.68, z -1.25..0.05, floor 1.79, roof 3.05).
from mathutils import Vector  # noqa: E402
EYE = (0, 2.75, CZ + 0.15)
dashP = K.mat("dash_plastic", 0x26282b, rough=0.7)
trimP = K.mat("trim_plastic", 0x41464b, rough=0.6)
liner = K.mat("headliner", 0x6a6e73, rough=0.95)
fabric = K.mat("seat_fabric", 0x23272b, rough=0.95)
mat_rubber = K.mat("floor_mat", 0x1a1b1c, rough=0.9)
screen = K.mat("screen", 0x10243a, rough=0.2, emit=0x16304d, emit_strength=0.8)
needleM = K.mat("needle", 0xff7a1a, rough=0.3, emit=0xff6a10, emit_strength=2.5)
lamp_cols = [0x3cff6a, 0xffb020, 0xff3a2a, 0x3aa8ff, 0xffb020, 0x3cff6a]
lampMs = [K.mat(f"warn_lamp_{i}", c, rough=0.3, emit=c, emit_strength=0.6) for i, c in enumerate(lamp_cols)]
btnM = K.mat("button_caps", 0x2c2f33, rough=0.5)
red = K.mat("extinguisher_red", 0xb3190f, rough=0.35)

cab = K.Part("cab_interior", (0, 0, 0), rear)
FZ, BZ, FL, RF, HW = CZ + 0.65, CZ - 0.65, 1.79, 3.05, 0.68
dashTop = EYE[1] - 0.42
# floor with a ribbed mat, front console under the windshield, pillar and sill trim, door panel, headliner
cab.add(mat_rubber, box(HW * 2 - 0.08, 0.02, 1.2, (0, FL + 0.01, CZ - 0.02), r=0.008))
for k in range(9):
    cab.add(mat_rubber, box(HW * 2 - 0.2, 0.008, 0.02, (0, FL + 0.024, CZ - 0.5 + k * 0.12)))
# no dashboard across the front: the windshield runs almost to the floor, with only a low glass rail and
# a narrow steering pedestal in the middle carrying the column and the instrument pod
WAIST = 1.98                                    # the cab's waist rail, where the side glass starts
cab.add(trimP, box(HW * 2 - 0.1, 0.06, 0.06, (0, FL + 0.05, FZ - 0.05), r=0.02))
# the pedestal stands behind the wheel (the rim's lowest point is at z -0.19, y 2.31), narrow at the top
cab.add(dashP, plate([(-0.07, FL), (0.04, FL), (0.04, 2.4), (-0.05, 2.4), (-0.07, 2.2)], 0.24, 0, r=0.03, seg=3))
cab.add(dashP, plate([(-0.04, FL), (0.04, FL), (0.04, 2.0), (-0.04, 2.0)], 0.36, 0, r=0.03, seg=3))
for sx in (-1, 1):
    cab.add(trimP, box(0.09, RF - FL, 0.09, (sx * (HW - 0.06), (RF + FL) / 2, FZ - 0.06), r=0.02))                # A-pillar trim
    cab.add(trimP, box(0.09, RF - FL, 0.11, (sx * (HW - 0.06), (RF + FL) / 2, BZ + 0.07), r=0.02))             # rear pillar trim
    cab.add(trimP, box(0.05, 0.05, FZ - BZ, (sx * (HW - 0.04), WAIST, CZ), r=0.015))                           # sills on the waist rail
cab.add(liner, box(0.03, WAIST - FL - 0.06, 0.95, (HW - 0.03, (WAIST + FL) / 2, CZ - 0.05), r=0.01))          # door panel (left)
cab.add(chrome, box(0.03, 0.04, 0.16, (HW - 0.05, WAIST + 0.12, CZ + 0.1), r=0.01))                           # door handle
cab.add(black, tube([(HW - 0.08, dashTop + 0.25, FZ - 0.1), (HW - 0.12, dashTop + 0.4, FZ - 0.12), (HW - 0.08, dashTop + 0.55, FZ - 0.1)], 0.014))  # grab handle
cab.add(liner, box(HW * 2 - 0.06, 0.03, FZ - BZ - 0.04, (0, RF - 0.05, CZ), r=0.01))
cab.add(trimP, box(0.5, 0.06, 0.18, (0, RF - 0.09, BZ + 0.2), r=0.02))                                         # radio console
cab.add(K.mat("radio_display", 0x0c1a2a, rough=0.2, emit=0x2a6a9a, emit_strength=0.6), box(0.16, 0.03, 0.005, (0, RF - 0.09, BZ + 0.293)))
for sx in (-0.3, 0.3):
    cab.add(black, cyl(0.06, 0.02, (sx, RF - 0.075, BZ + 0.25), seg=20))                                       # speakers
cab.add(lensF, box(0.14, 0.015, 0.06, (0, RF - 0.07, CZ - 0.1), r=0.006))                                      # dome light
for sx in (-0.35, 0.35):
    cab.add(trimP, box(0.16, 0.03, 0.06, (sx, RF - 0.075, FZ - 0.2), r=0.01))                                  # air vents
    for k in range(4):
        cab.add(black, box(0.14, 0.004, 0.006, (sx, RF - 0.088, FZ - 0.22 + k * 0.014)))
cab.add(black, box(0.5, 0.02, 0.2, (0.15, RF - 0.11, FZ - 0.17), r=0.01, rot=K.rot_game(rx=0.25)))            # sun visor
cab.add(chrome, box(0.2, 0.07, 0.015, (0, RF - 0.12, FZ - 0.1), r=0.01))                                       # mirror
cab.add(red, cyl(0.05, 0.32, (HW - 0.12, FL + 0.3, BZ + 0.15), seg=20, bevel=0.02))                              # extinguisher
cab.add(black, cyl(0.02, 0.05, (HW - 0.12, FL + 0.49, BZ + 0.15), seg=10))
# pedals and the steering column pod
for sx, h in ((0.13, 0.22), (-0.13, 0.26)):
    cab.add(black, box(0.1, h, 0.025, (sx, FL + 0.18, FZ - 0.32), r=0.01, rot=K.rot_game(rx=-0.5)))
    for k in range(4):
        cab.add(mat_rubber, box(0.09, 0.006, 0.01, (sx, FL + 0.11 + k * 0.045, FZ - 0.34 + k * 0.022)))
H = Vector((0, 2.45, -0.09))                                    # the game's steering hub and tilt
WX, WY, WZ = Vector((1, 0, 0)), Vector((0, math.cos(0.62), math.sin(0.62))), Vector((0, -math.sin(0.62), math.cos(0.62)))
cab.add(dashP, K.oriented_box(H + WZ * 0.07, WZ, WX, WY, 0.075, 0.075, 0.1, r=0.025))                         # column stub into the pedestal
# instrument pod on the dash, facing the driver: rpm and speed, fuel and temperature, warning lamps
POD = Vector((0, 2.47, 0.0))
n, u, v = K.frame_at(POD, EYE)
cab.add(dashP, K.oriented_box(POD - n * 0.035, n, u, v, 0.5, 0.19, 0.07, r=0.03))
cab.add(dashP, K.oriented_box(POD + v * 0.1 + n * 0.02, n, u, v, 0.52, 0.025, 0.1, r=0.01))                 # hood over the dials
dials = [("rpm", -0.095, 0.07, ["0", "5", "10", "15", "20", "25"], 270, 225, 0.82, "RPMX100"),
         ("speed", 0.095, 0.07, ["0", "10", "20", "30", "40"], 270, 225, None, "KM/H"),
         ("fuel", -0.205, 0.036, ["E", "", "F"], 90, 225, None, ""),
         ("temp", 0.205, 0.036, ["C", "", "H"], 90, 225, 0.8, "")]
needles = []
for name, du, rad, labels, sweep, start, redz, cap in dials:
    c = POD + u * du + v * (0.0 if rad > 0.05 else -0.02)
    img = K.dial_image(f"dial_{name}", labels, sweep, start, redz, cap)
    cab.add(chrome, K.disc(c, n, u, v, rad + 0.008, lift=0.001))
    cab.add(K.dial_mat(f"dial_{name}", img), K.disc(c, n, u, v, rad, lift=0.003), keep_uv=True)
    needle = K.Part(f"needle_{name}", tuple(c + n * 0.006), cab)
    needles.append(needle)
    d0 = u * math.cos(math.radians(start)) + v * math.sin(math.radians(start))
    side = n.cross(d0).normalized()
    ln = rad * 0.82
    needle.add(needleM, K.oriented_box(c + n * 0.006 + d0 * (ln / 2 - rad * 0.12), n, d0, side, ln + rad * 0.24, rad * 0.06, 0.002))
    needle.add(black, K.disc(c, n, u, v, rad * 0.12, lift=0.008))
for i, m in enumerate(lampMs):
    cab.add(m, K.oriented_box(POD + u * (-0.0625 + i * 0.025) + v * -0.075, n, u, v, 0.016, 0.012, 0.004))
# display on the right front pillar; the game draws gear, speed and tool onto the "screen" material
SCR = Vector((-0.5, 2.6, -0.06))
n2, u2, v2 = K.frame_at(SCR, EYE)
cab.add(dashP, K.oriented_box(SCR - n2 * 0.015, n2, u2, v2, 0.25, 0.18, 0.03, r=0.012))
cab.add(screen, K.quad(SCR, n2, u2, v2, 0.21, 0.13, lift=0.001), keep_uv=True)
cab.add(trimP, K.beam((-0.5, 2.48, -0.06), (-HW + 0.07, 2.42, FZ - 0.06), 0.04, 0.04, r=0.01))                 # screen arm
# right-hand console: armrest, switch panel, ignition, joystick boot; seat with suspension and belts
cab.add(dashP, box(0.32, 0.38, 0.75, (-0.5, FL + 0.19, CZ - 0.1), r=0.03))
cab.add(trimP, box(0.3, 0.03, 0.7, (-0.5, FL + 0.395, CZ - 0.1), r=0.012))
cab.add(fabric, box(0.14, 0.07, 0.34, (-0.48, FL + 0.48, CZ - 0.32), r=0.03))                                  # armrest
for r_ in range(3):
    for c_ in range(3):
        cab.add(btnM, box(0.04, 0.018, 0.05, (-0.6 + c_ * 0.05, FL + 0.42, CZ + 0.06 + r_ * 0.065), r=0.006))
        cab.add(lampMs[(r_ * 3 + c_) % 6], box(0.01, 0.004, 0.01, (-0.6 + c_ * 0.05, FL + 0.432, CZ + 0.075 + r_ * 0.065)))
cab.add(chrome, cyl(0.016, 0.02, (-0.38, FL + 0.415, CZ + 0.2), seg=12))                                       # ignition
cab.add(black, cyl(0.05, 0.06, (-0.42, 2.18, CZ + 0.12), seg=16, r2=0.035))                                    # joystick boot
cab.add(iron, box(0.4, 0.2, 0.42, (0, 1.9, CZ - 0.12), r=0.03))                                                # seat suspension
cab.add(black, cyl(0.12, 0.08, (0, 1.98, CZ - 0.12), seg=20))
cab.add(fabric, box(0.5, 0.12, 0.48, (0, 2.08, CZ - 0.08), r=0.05, seg=4))                                     # cushion
cab.add(fabric, box(0.5, 0.62, 0.12, (0, 2.45, CZ - 0.38), r=0.05, seg=4, rot=K.rot_game(rx=-0.15)))           # backrest
cab.add(fabric, box(0.3, 0.16, 0.1, (0, 2.86, CZ - 0.45), r=0.04, rot=K.rot_game(rx=-0.15)))                    # headrest
cab.add(fabric, box(0.07, 0.06, 0.3, (0.31, 2.3, CZ - 0.2), r=0.025))                                          # left armrest
for sx in (-0.2, 0.2):
    cab.add(fabric, box(0.08, 0.4, 0.1, (sx * 1.25, 2.4, CZ - 0.34), r=0.035, rot=K.rot_game(rx=-0.15)))      # side bolsters
cab.add(black, box(0.05, 0.5, 0.008, (0.22, 2.35, CZ - 0.3), rot=K.rot_game(rz=0.25)))                          # seat belt
cab.add(chrome, box(0.04, 0.025, 0.06, (-0.24, 2.1, CZ - 0.2), r=0.008))
# steering wheel (turns with steering) and joystick (tilts with the boom and bucket controls)
sw = K.Part("steering_wheel", tuple(H), cab)
sw.add(black, K.torus(H, (WX, WY, WZ), 0.17, 0.017))
for k in range(3):
    a = k * 2.094 + math.pi
    d = WX * math.sin(a) + WY * math.cos(a)
    sw.add(dashP, K.oriented_box(H + d * 0.095 + WZ * 0.006, WZ, d, d.cross(WZ), 0.15, 0.024, 0.012, r=0.004))
sw.add(dashP, cyl(0.05, 0.045, tuple(H + WZ * 0.012), seg=28, bevel=0.012, rot=K.rot_game(rx=0.62 + math.pi / 2)))   # round hub boss
sw.add(orange, K.disc(H, -WZ, WX, WY, 0.012, lift=0.012))
knob = H + (WX * math.sin(0.8) + WY * math.cos(0.8)) * 0.17
sw.add(black, K.oriented_box(knob - WZ * 0.02, WZ, WX, WY, 0.016, 0.016, 0.04, r=0.006))
sw.add(black, cyl(0.016, 0.04, tuple(knob - WZ * 0.045), seg=14, bevel=0.006, rot=K.rot_game(rx=0.62 + math.pi / 2)))
J = (-0.42, 2.2, CZ + 0.12)
js = K.Part("joystick", J, cab)
js.add(chrome, cyl(0.012, 0.18, (J[0], J[1] + 0.1, J[2]), seg=10))
js.add(black, box(0.06, 0.12, 0.08, (J[0], J[1] + 0.24, J[2] + 0.005), r=0.025))
js.add(orange, box(0.025, 0.02, 0.02, (J[0] + 0.012, J[1] + 0.305, J[2] + 0.02), r=0.006))
js.add(btnM, box(0.018, 0.014, 0.018, (J[0] - 0.015, J[1] + 0.3, J[2] + 0.03), r=0.005))

# ================================================================ build, export, preview
objs = []
for part in (rear, front, arm, bucket, plow, *wheels, cab, sw, js, *needles):
    objs += part.build()
tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in objs)
print(f"loader: {len(objs)} mesh objects, about {tris} triangles")

out = opt.get("out", os.path.join(os.path.dirname(__file__), "..", "..", "assets", "models", "loader.glb"))
C.export_glb(os.path.abspath(out))
print("exported", os.path.abspath(out), os.path.getsize(out) // 1024, "KB")
if opt.get("preview"):
    d = opt["preview"]
    plow_objs = [o for o in bpy.data.objects if o.parent == plow.empty]
    for o in plow_objs:
        o.hide_render = True                    # show the bucket in the first views
    for name, az, el, dist in (("front", 35, 14, 9), ("rear", 210, 16, 9), ("side", 95, 6, 8.5)):
        C.preview(os.path.join(d, f"loader_{name}.png"), target=(0, 0.0, 1.3), dist=dist, az=az, el=el, size=(1000, 650), samples=32)
    for o in plow_objs:
        o.hide_render = False
    for o in bpy.data.objects:
        if o.parent == bucket.empty:
            o.hide_render = True
    C.preview(os.path.join(d, "loader_plow.png"), target=(0, -1.5, 1.1), dist=8.5, az=25, el=12, size=(1000, 650), samples=32)
    eye = G(*EYE)
    for nm, look, lens in (("cab_ahead", G(0, 2.35, 1.5), 22), ("cab_pod", G(0, 2.45, 0.0), 40), ("cab_right", G(-0.6, 2.3, -0.2), 24)):
        C.preview(os.path.join(d, f"loader_{nm}.png"), size=(1000, 650), samples=48, cam_at=eye, look_at=look, lens=lens, floor=True)
    C.preview(os.path.join(d, "loader_plow_top.png"), target=(0, -3.0, 1.0), dist=7.5, az=200, el=60, size=(1000, 650), samples=32)
    C.preview(os.path.join(d, "loader_plow_back.png"), target=(0, -3.6, 1.2), dist=4.5, az=150, el=25, size=(1000, 650), samples=32)
