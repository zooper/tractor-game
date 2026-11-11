"""Tracked excavator -> assets/models/excavator.glb

    blender --background --factory-startup --python tools/blender/excavator.py -- [--out PATH] [--preview DIR]

Sizes and pivots are game coordinates (kit.py) copied from buildExcavator() in index.html. The boom, stick and
bucket are built straight out along +z like the code does, then their pivots are turned into the parked pose
the game expects (boom -0.55, stick 1.7, bucket 1.4 rad about x).
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, os.path.dirname(__file__))
import common as C  # noqa: E402
import kit as K  # noqa: E402
import cockpit as CP  # noqa: E402
from kit import G, box, cyl, plate, tube, merge  # noqa: E402

opt = C.args()
C.reset()

HY = 0.95                                   # the house sits on the turntable at this height
BOOM_L, STICK_L = 3.4, 2.0
BOOM_P = (-0.25, HY + 1.15, 0.85)
POSE = {"boom": -0.55, "stick": 1.7, "bucket": 1.4}

yellow = K.mat("paint_yellow", rough=0.42, metal=0.05, image=K.grime_image("grime_yellow", 0xd9a21b, 1.0, seed=41))
yellowD = K.mat("paint_yellow_dark", rough=0.48, metal=0.05, image=K.grime_image("grime_yellow_dark", 0xb8860f, 1.1, seed=42))
frame = K.mat("frame_dark", rough=0.55, metal=0.3, image=K.grime_image("grime_dark", 0x2f2d2a, 1.2, seed=43))
shoeM = K.mat("track_steel", rough=0.6, metal=0.55, image=K.grime_image("grime_track", 0x2b2a28, 1.4, seed=44))
black = K.mat("black_plastic", 0x171717, rough=0.55)
hose = K.mat("hose_rubber", 0x151515, rough=0.6)
steel = K.mat("steel_worn", 0x8a8880, rough=0.35, metal=0.9)
chrome = K.mat("chrome", 0xdadcdf, rough=0.15, metal=1.0)
iron = K.mat("iron", 0x2c2c2e, rough=0.5, metal=0.6)
glass = K.mat("glass", 0x2a3a40, rough=0.04, metal=0.1, alpha=0.38)
lensF = K.mat("light_front", 0xfff4dc, rough=0.05, emit=0xfff0d0, emit_strength=2.0)
lensR = K.mat("light_rear", 0x9c1c14, rough=0.1, emit=0xb0170f, emit_strength=1.0)
hz_y = K.mat("hazard_yellow", 0xf2c21a, rough=0.5)
hz_k = K.mat("hazard_black", 0x141414, rough=0.5)

under = K.Part("undercarriage")
house = K.Part("house", (0, HY, 0), under)
boom = K.Part("boom", BOOM_P, house)
stick = K.Part("stick", (BOOM_P[0], BOOM_P[1], BOOM_P[2] + BOOM_L), boom)
bucket = K.Part("bucket", (BOOM_P[0], BOOM_P[1], BOOM_P[2] + BOOM_L + STICK_L), stick)


def H(x, y, z):
    """house-local game position -> vehicle position"""
    return (x, y + HY, z)


def rel(part, y, z, x=None):
    """a point in a boom/stick/bucket's own (unposed) frame: y up, z along it"""
    w = part.world
    return (w.x if x is None else x, w.z + y, -w.y + z)


# ================================================================ undercarriage
L, RR = 1.5, 0.42
per = 4 * L + 2 * math.pi * RR
n_sh = 46
loop = []
for i in range(n_sh):
    d = i / n_sh * per
    if d < 2 * L:
        z, y, a = -L + d, 0.84, 0.0
    elif (d := d - 2 * L) < math.pi * RR:
        a = d / RR
        z, y = L + math.sin(a) * RR, 0.42 + math.cos(a) * RR
    elif (d := d - math.pi * RR) < 2 * L:
        z, y, a = L - d, 0.0, math.pi
    else:
        d -= 2 * L
        a = math.pi + d / RR
        z, y = -L + math.sin(a) * RR, 0.42 + math.cos(a) * RR
    loop.append((y, z, a))
shoes = []
for sx in (-1.1, 1.1):
    for y, z, a in loop:
        # shoe plate with a grouser bar, turned to follow the loop (outward = away from the track centre)
        s = merge(box(0.66, 0.05, 0.19, (0, 0, 0), r=0.01, seg=1), box(0.66, 0.05, 0.035, (0, 0.045, 0.05), r=0.008, seg=1),
                  box(0.14, 0.05, 0.2, (sx * -0.12 / 1.1, -0.045, 0), r=0.01, seg=1))
        bmesh.ops.translate(s, vec=-G(0, 0, 0), verts=s.verts)
        bmesh.ops.transform(s, matrix=Matrix.Rotation(-a, 4, "X"), verts=s.verts)
        bmesh.ops.translate(s, vec=G(sx, y, z), verts=s.verts)
        shoes.append(s)
under.add(shoeM, merge(*shoes))
for sx in (-1.1, 1.1):
    sg = math.copysign(1, sx)
    under.add(yellow, box(0.4, 0.42, 2.9, (sx, 0.42, 0), r=0.08))                  # track frame
    under.add(yellowD, plate([(-1.2, 0.25), (1.2, 0.25), (1.0, 0.62), (-1.0, 0.62)], 0.05, sx + sg * 0.21, r=0.01))   # outer side plate
    for k in range(5):
        under.add(iron, cyl(0.12, 0.46, (sx, 0.14, -1.0 + k * 0.5), axis="x", seg=16, bevel=0.015))
        under.add(frame, box(0.08, 0.12, 0.12, (sx + sg * 0.25, 0.2, -1.0 + k * 0.5), r=0.02))
    for z in (-0.5, 0.5):
        under.add(iron, cyl(0.09, 0.3, (sx, 0.74, z), axis="x", seg=14, bevel=0.01))
    under.add(frame, box(0.3, 0.12, 0.5, (sx, 0.42, -1.05), r=0.03))              # final drive guard
    under.add(iron, box(0.12, 0.1, 0.3, (sx, 0.5, 1.15), r=0.02))                  # track adjuster
under.add(frame, box(1.6, 0.42, 2.2, (0, 0.6, 0), r=0.08))                        # carbody
for sz in (-1, 1):
    under.add(frame, plate([(sz * 0.3, 0.42), (sz * 0.9, 0.5), (sz * 0.9, 0.78), (sz * 0.3, 0.8)], 1.8, 0, r=0.03))
under.add(iron, cyl(0.95, 0.12, (0, 0.86, 0), seg=40, bevel=0.01))               # swing bearing
sprockets = []
for sz in (-1.5, 1.5):
    for sx in (1.1, -1.1):
        p = (sx, 0.42, sz)
        sp = K.Part(f"sprocket_{'front' if sz > 0 else 'rear'}_{'left' if sx > 0 else 'right'}", p, under)
        if sz < 0:                                                                 # drive sprocket: toothed ring
            sp.add(iron, cyl(0.3, 0.12, p, axis="x", seg=28, bevel=0.01))
            for k in range(11):
                a = 2 * math.pi * k / 11
                sp.add(iron, box(0.1, 0.1, 0.1, (sx, 0.42 + math.cos(a) * 0.33, sz + math.sin(a) * 0.33), r=0.02, rot=None))
            sp.add(yellowD, cyl(0.22, 0.4, p, axis="x", seg=24, bevel=0.02))
        else:                                                                      # idler wheel
            sp.add(iron, K.lathe([(0.05, -0.22), (0.3, -0.22), (0.36, -0.15), (0.36, -0.05), (0.3, -0.03), (0.3, 0.03), (0.36, 0.05), (0.36, 0.15), (0.3, 0.22), (0.05, 0.22)], p, seg=32))
        sp.add(chrome, cyl(0.1, 0.5, p, axis="x", seg=14))
        for k in range(6):
            a = 2 * math.pi * k / 6
            sp.add(steel, cyl(0.02, 0.52, (sx, 0.42 + math.cos(a) * 0.16, sz + math.sin(a) * 0.16), axis="x", seg=6))
        sprockets.append(sp)

# ================================================================ house
house.add(iron, cyl(0.9, 0.18, H(0, 0, 0), seg=40))
house.add(yellow, box(2.4, 0.92, 2.5, H(0, 0.6, -0.45), r=0.14, seg=4))
house.add(yellowD, box(2.48, 0.86, 0.66, H(0, 0.58, -1.78), r=0.28, seg=5))      # counterweight
K.hazard(house, hz_y, hz_k, 1.9, 0.14, H(0, 0.7, -2.115), normal_z=-1, stripes=13)
for sx in (-0.95, 0.95):
    house.add(iron, box(0.22, 0.13, 0.05, H(sx, 0.88, -2.1), r=0.02))
    house.add(lensR, box(0.18, 0.1, 0.02, H(sx, 0.88, -2.125), r=0.01))
house.add(frame, box(2.3, 0.06, 2.3, H(0, 0.13, -0.4), r=0.02))                 # under-house plate
# engine hood on the right-rear with side grille, top louvres, exhaust, air cleaner
house.add(yellowD, box(1.05, 0.32, 1.45, H(-0.65, 1.2, -0.9), r=0.08))
for k in range(6):
    house.add(iron, box(0.025, 0.04, 0.9, H(-1.205, 0.78 + k * 0.07, -0.85), rot=K.rot_game(rz=-0.5)))
    house.add(iron, box(0.7, 0.02, 0.05, H(-0.65, 1.37, -1.4 + k * 0.12)))
house.add(frame, box(0.02, 0.44, 1.0, H(-1.197, 0.95, -0.85)))
house.add(iron, cyl(0.06, 0.62, H(-0.95, 1.62, -1.1), seg=16))
house.add(iron, box(0.15, 0.025, 0.15, H(-0.95, 1.94, -1.12), r=0.01, rot=K.rot_game(rx=-0.35)))
house.add(black, cyl(0.12, 0.3, H(-0.35, 1.45, -1.3), seg=20, bevel=0.02))
# toolbox and fuel tank on the right front, handrails along the top, steps, mirrors
house.add(yellow, box(0.85, 0.6, 0.85, H(-0.75, 0.75, 0.42), r=0.06))
house.add(iron, box(0.03, 0.06, 0.18, H(-0.75, 0.9, 0.86), r=0.01))
for sd, pts in ((-1, [(-1.18, 1.1, -0.2), (-1.2, 1.5, -0.3), (-1.18, 1.5, -1.5), (-1.15, 1.1, -1.6)]),
                (1, [(1.2, 1.1, -0.6), (1.22, 1.45, -0.7), (1.2, 1.45, -1.5), (1.18, 1.1, -1.6)])):
    house.add(iron, tube([H(*p) for p in pts], 0.02))
for k in range(2):
    house.add(iron, box(0.3, 0.035, 0.22, H(1.15, 0.25 + k * 0.32, 0.8), r=0.01))
house.add(iron, tube([H(1.13, 1.9, 0.92), H(1.35, 1.95, 1.0), H(1.4, 1.75, 1.02)], 0.014))
house.add(black, box(0.05, 0.28, 0.2, H(1.42, 1.62, 1.02), r=0.02))
house.add(chrome, box(0.01, 0.24, 0.16, H(1.40, 1.62, 1.11)))
# boom foot: two heavy brackets either side of the boom pin, and the boom-ram lugs low in front
for sx in (-0.52, 0.02):
    house.add(frame, plate([(0.35, 0.3), (1.05, 0.3), (1.05, 1.0), (0.7, 1.32), (0.4, 1.2)], 0.1, sx, r=0.02, offset=(0, HY, 0)))
house.add(iron, cyl(0.14, 0.62, (BOOM_P[0], BOOM_P[1], BOOM_P[2]), axis="x", seg=20))
house.add(frame, box(0.5, 0.3, 0.35, H(-0.25, 0.7, 0.62), r=0.04))
house.add(iron, cyl(0.07, 0.6, H(-0.25, 0.75, 0.6), axis="x", seg=14))

# ---- cab: a hollow box of posts and glass, roof with lights
CXc, CZc = 0.68, 0.35
cab_shell = K.boolean(box(0.98, 1.36, 1.18, H(CXc, 1.75, CZc), r=0.07, seg=3), [
    box(0.86, 1.24, 1.06, H(CXc, 1.75, CZc)),
    box(0.8, 1.1, 0.4, H(CXc, 1.76, CZc + 0.59), r=0.04),                         # front
    box(0.4, 1.06, 0.92, H(CXc + 0.49, 1.78, CZc), r=0.04),                        # left (door)
    box(0.4, 1.0, 0.92, H(CXc - 0.49, 1.8, CZc), r=0.04),                          # right
    box(0.74, 0.7, 0.4, H(CXc, 1.95, CZc - 0.59), r=0.04),                         # rear
])
house.add(frame, cab_shell)
house.add(glass, box(0.82, 1.12, 0.012, H(CXc, 1.76, CZc + 0.565)))
house.add(glass, box(0.012, 1.08, 0.94, H(CXc + 0.465, 1.78, CZc)))
house.add(glass, box(0.012, 1.02, 0.94, H(CXc - 0.465, 1.8, CZc)))
house.add(glass, box(0.76, 0.72, 0.012, H(CXc, 1.95, CZc - 0.565)))
house.add(frame, box(0.82, 0.04, 0.03, H(CXc, 1.5, CZc + 0.575)))                 # front window split
house.add(chrome, box(0.03, 0.04, 0.14, H(CXc + 0.5, 1.5, CZc + 0.2), r=0.01))
house.add(yellow, box(1.08, 0.1, 1.28, H(CXc, 2.48, CZc), r=0.04))
house.add(yellowD, box(0.92, 0.05, 1.05, H(CXc, 2.55, CZc), r=0.02))
house.add(frame, box(0.95, 0.12, 0.12, H(CXc, 2.42, CZc + 0.64), r=0.03))          # visor / guard bar
for sx in (0.35, 1.0):
    house.add(iron, box(0.16, 0.1, 0.08, H(sx, 2.44, 0.95), r=0.02))
    house.add(lensF, box(0.12, 0.07, 0.02, H(sx, 2.44, 0.995), r=0.008))
house.add(iron, box(0.2, 0.12, 0.1, H(-0.25, 1.45, 0.75), r=0.02))               # boom work light
house.add(lensF, box(0.15, 0.08, 0.02, H(-0.25, 1.45, 0.805), r=0.008))

# ================================================================ boom (unposed, along +z)
bp = (0, BOOM_P[1], BOOM_P[2])
boom_prof = [(-0.28, -0.25), (1.7, 0.18), (BOOM_L + 0.18, -0.17), (BOOM_L + 0.18, 0.16), (1.5, 0.64), (-0.28, 0.24)]
boom.add(yellow, plate(boom_prof, 0.44, BOOM_P[0], r=0.04, seg=3, offset=bp))
for sd in (-1, 1):                                                                  # side reinforcement at the knee
    boom.add(yellowD, plate([(0.9, 0.0), (2.3, 0.08), (2.3, 0.42), (1.5, 0.58), (0.9, 0.42)], 0.02, BOOM_P[0] + sd * 0.23, r=0.005, offset=bp))
boom.add(yellowD, plate([(0.9, 0.05), (1.6, -0.05), (1.75, 0.2), (1.1, 0.25)], 0.22, BOOM_P[0], r=0.015, offset=bp))   # boom-ram lug
boom.add(yellowD, plate([(1.15, 0.5), (1.6, 0.55), (1.52, 0.82), (1.25, 0.78)], 0.2, BOOM_P[0], r=0.015, offset=bp))   # stick-ram lug
boom.add(iron, cyl(0.06, 0.3, rel(boom, 0.05, 1.45), axis="x", seg=12))
boom.add(iron, cyl(0.06, 0.28, rel(boom, 0.62, 1.36), axis="x", seg=12))
for z in (0, BOOM_L):
    boom.add(iron, cyl(0.13, 0.5, rel(boom, 0, z), axis="x", seg=18, bevel=0.015))
for sd in (-1, 1):
    boom.add(hose, tube([rel(boom, 0.4, 0.3, BOOM_P[0] + sd * 0.18), rel(boom, 0.62, 1.5, BOOM_P[0] + sd * 0.2),
                         rel(boom, 0.3, 3.0, BOOM_P[0] + sd * 0.19), rel(boom, 0.1, BOOM_L, BOOM_P[0] + sd * 0.17)], 0.022))
    for z in (0.8, 2.3):
        boom.add(iron, box(0.05, 0.05, 0.06, rel(boom, 0.5 if z < 1.5 else 0.34, z, BOOM_P[0] + sd * 0.2), r=0.01))

# ================================================================ stick
sp_ = (0, stick.world.z, -stick.world.y)
stick.add(yellow, plate([(-0.6, 0.26), (STICK_L + 0.12, 0.13), (STICK_L + 0.12, -0.14), (-0.6, -0.22)], 0.34, BOOM_P[0], r=0.03, seg=3, offset=sp_))
stick.add(yellowD, plate([(-0.15, 0.2), (0.55, 0.18), (0.45, 0.42), (0.05, 0.42)], 0.18, BOOM_P[0], r=0.015, offset=sp_))   # bucket-ram lug
stick.add(iron, cyl(0.1, 0.4, rel(stick, 0.3, -0.35), axis="x", seg=14, bevel=0.012))
stick.add(iron, cyl(0.1, 0.4, rel(stick, 0, STICK_L), axis="x", seg=14, bevel=0.012))
stick.add(iron, cyl(0.06, 0.24, rel(stick, 0.3, 0.29), axis="x", seg=12))
for sd in (-1, 1):
    stick.add(hose, tube([rel(stick, 0.25, -0.4, BOOM_P[0] + sd * 0.14), rel(stick, 0.32, 0.4, BOOM_P[0] + sd * 0.15), rel(stick, 0.24, 1.2, BOOM_P[0] + sd * 0.15)], 0.02))
    stick.add(steel, box(0.03, 0.12, 0.9, rel(stick, -0.05, 1.3, BOOM_P[0] + sd * 0.18), r=0.01))   # wear strips

# ================================================================ bucket
BK = [(0, -0.05), (0.2, 0.45), (0.65, 0.62), (1.05, 0.35), (1.25, -0.05)]
outer = []
for i, (z, y) in enumerate(BK):
    z0, y0 = BK[max(0, i - 1)]
    z1, y1 = BK[min(len(BK) - 1, i + 1)]
    tz, ty = z1 - z0, y1 - y0
    l = math.hypot(tz, ty) or 1
    outer.append((z - ty / l * 0.06, y + tz / l * 0.06))
bk_ = (0, bucket.world.z, -bucket.world.y)
# a smoother shell: resample the polyline through Catmull-Rom so the back of the bucket is round
def smooth(pts, n=6):
    P = [Vector(p) for p in pts]
    out = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(0, i - 1)], P[i], P[i + 1], P[min(len(P) - 1, i + 2)]
        for s in range(n):
            t = s / n
            out.append(tuple(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3)))
    out.append(tuple(P[-1]))
    return out
inner_s, outer_s = smooth(BK), smooth(outer)
bucket.add(yellowD, plate(inner_s + outer_s[::-1], 1.0, BOOM_P[0], r=0.01, offset=bk_))
for sx in (-0.5, 0.5):
    bucket.add(yellow, plate(inner_s, 0.05, BOOM_P[0] + sx, r=0.01, offset=bk_))
    bucket.add(steel, plate([(0.85, -0.05), (1.27, -0.07), (1.12, 0.3)], 0.06, BOOM_P[0] + sx * 1.02, r=0.008, offset=bk_))   # side cutters
bucket.add(steel, box(1.04, 0.05, 0.14, rel(bucket, -0.07, 1.22), r=0.02, rot=None))
lip = Vector((0.2, -0.4)).normalized()                                             # teeth continue the lip downward
ta = math.atan2(-lip.y, lip.x)
for t in range(5):
    tx = BOOM_P[0] - 0.4 + t * 0.2
    bucket.add(iron, box(0.11, 0.08, 0.12, rel(bucket, -0.1, 1.27, tx), r=0.015, rot=K.rot_game(rx=ta)))
    bucket.add(steel, cyl(0.05, 0.22, rel(bucket, -0.17, 1.33, tx), axis="z", seg=4, r2=0.012, rot=K.rot_game(rx=ta) @ K.rot_game(rz=math.pi / 4)))
for x in (-0.18, 0.18):
    bucket.add(yellow, plate([(-0.05, 0.3), (0.3, 0.42), (0.3, 0.68), (-0.05, 0.62)], 0.07, BOOM_P[0] + x, r=0.012, offset=bk_))   # ears
bucket.add(iron, cyl(0.06, 0.5, rel(bucket, 0.5, 0.1), axis="x", seg=12))
bucket.add(iron, cyl(0.08, 0.5, rel(bucket, 0, 0), axis="x", seg=14))

# ================================================================ cockpit (house frame)
M = CP.Mats(accent=0xd9a21b)
cab = K.Part("cab_interior", (0, 0, 0), house)
EYE = H(0.68, 1.95, 0.3)
FLv = HY + 1.08 + 0.02
X0, X1, Z0, Z1 = CXc - 0.43, CXc + 0.43, CZc - 0.53, CZc + 0.53
cab.add(M.floor, box(0.84, 0.02, 1.04, (CXc, FLv, CZc), r=0.008))
for k in range(8):
    cab.add(M.floor, box(0.6, 0.008, 0.02, (CXc, FLv + 0.014, Z0 + 0.2 + k * 0.1)))
# seat where the game's operator sits, consoles each side carrying the joysticks (pivots 0.42 and 0.95, y 2.55, z 0.4)
CP.seat(cab, M, CXc, FLv, 0.15, HY + 1.2, width=0.46)
for jx in (0.42, 0.95):
    side = 1 if jx > CXc else -1
    cab.add(M.dash, box(0.2, 2.53 - FLv - 0.12, 0.62, (jx, (2.53 + FLv - 0.12) / 2 + 0.06, 0.28), r=0.03))
    cab.add(M.trim, box(0.2, 0.03, 0.62, (jx, 2.53 - 0.03, 0.28), r=0.01))
    cab.add(M.fabric, box(0.12, 0.06, 0.3, (jx + side * 0.01, 2.53 + 0.02, 0.04), r=0.025))   # arm rests
    for r_ in range(2):
        for c_ in range(2):
            cab.add(M.btn, box(0.035, 0.014, 0.03, (jx - 0.04 + c_ * 0.06, 2.512, 0.5 + r_ * 0.05), r=0.005))
sticks = [CP.lever(cab, M, "joystick", (0.42, 2.55, 0.4), length=0.12),
          CP.lever(cab, M, "joystick_2", (0.95, 2.55, 0.4), length=0.12)]
# travel levers and pedals in front of the seat
for sx in (-0.08, 0.08):
    cab.add(M.chrome, K.beam((CXc + sx, FLv + 0.1, 0.72), (CXc + sx, FLv + 0.58, 0.66), 0.016, 0.016, r=0.006))
    cab.add(M.black, box(0.05, 0.1, 0.05, (CXc + sx, FLv + 0.62, 0.655), r=0.02))
    cab.add(M.black, box(0.12, 0.03, 0.26, (CXc + sx * 2.2, FLv + 0.08, 0.7), r=0.01, rot=K.rot_game(rx=-0.4)))
cab.add(M.dash, box(0.4, 0.12, 0.12, (CXc, FLv + 0.06, 0.76), r=0.02))
# monitor and gauges on the right front post, facing the operator
CP.screen(cab, M, (0.33, 2.72, 0.78), EYE, w=0.18, h=0.12)
needles = CP.dial_pod(cab, M, (0.31, 2.5, 0.8), EYE, [("rpm", 0.0, 0.0, 0.045), ("fuel", -0.075, -0.0, 0.028), ("temp", 0.075, 0.0, 0.028)],
                      pod_size=(0.24, 0.12), lamps=False)
cab.add(M.trim, K.beam((0.3, 2.42, 0.82), (X0 + 0.02, 2.2, Z1 - 0.04), 0.04, 0.04, r=0.01))
# walls: lower rear panel, headliner, pillar trim, extinguisher, radio
cab.add(M.liner, box(0.84, 0.6, 0.03, (CXc, FLv + 0.3, Z0 + 0.015)))
cab.add(M.liner, box(0.86, 0.03, 1.06, (CXc, HY + 2.4, CZc), r=0.01))
for px, pz in ((X0, Z1), (X1, Z1), (X0, Z0), (X1, Z0)):
    cab.add(M.trim, box(0.06, 1.25, 0.06, (px, HY + 1.75, pz), r=0.015))
cab.add(M.red, cyl(0.045, 0.28, (X0 + 0.08, FLv + 0.16, Z0 + 0.1), seg=18, bevel=0.015))
cab.add(M.trim, box(0.3, 0.1, 0.15, (CXc - 0.2, HY + 2.32, Z0 + 0.1), r=0.02))
cab.add(K.mat("radio_display", 0x0c1a2a, rough=0.2, emit=0x2a6a9a, emit_strength=0.6), box(0.14, 0.04, 0.005, (CXc - 0.2, HY + 2.32, Z0 + 0.178)))
cab.add(M.dome, box(0.14, 0.015, 0.06, (CXc, HY + 2.38, CZc - 0.1), r=0.006))

# ================================================================ build, pose, export
objs = []
for part in (under, house, boom, stick, bucket, *sprockets, cab, *sticks, *needles):
    objs += part.build()
for name, ang in POSE.items():
    bpy.data.objects[name].rotation_euler = (ang, 0, 0)
tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
print(f"excavator: about {tris} triangles")
out = os.path.abspath(opt.get("out", os.path.join(os.path.dirname(__file__), "..", "..", "assets", "models", "excavator.glb")))
C.export_glb(out)
print("exported", out, os.path.getsize(out) // 1024, "KB")
if opt.get("preview"):
    d = opt["preview"]
    for name, az, el, dist in (("front", 35, 14, 11), ("rear", 215, 18, 10), ("side", 95, 6, 10)):
        C.preview(os.path.join(d, f"excavator_{name}.png"), target=(0, -1.2, 2.0), dist=dist, az=az, el=el, size=(1000, 650), samples=32)
    C.preview(os.path.join(d, "excavator_cab.png"), size=(1000, 650), samples=48, cam_at=G(*EYE), look_at=G(0.6, 2.4, 2.0), lens=20)
