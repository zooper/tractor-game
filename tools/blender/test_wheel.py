"""Pipeline test: one loader wheel (tyre with chevron lugs, dished rim, wheel nuts), exported and previewed."""
import math
import os
import sys

import bmesh
import bpy

sys.path.insert(0, os.path.dirname(__file__))
import common as C  # noqa: E402

opt = C.args()
C.reset()

R, W = 0.70, 0.58
hw = W / 2
rubber = C.material("tyre", C.srgb(0x1c1c1c), rough=0.88)
paint = C.material("rim_paint", C.srgb(0xd9a21b), rough=0.42, metal=0.1)
steel = C.material("nuts", C.srgb(0xc8c8c4), rough=0.3, metal=1.0)

wheel = C.empty("wheel_front_left", (0, 0, R))

# carcass: bead, sidewall bulge, rounded shoulders, flat crown
prof = [(R * 0.60, -hw * 0.80), (R * 0.70, -hw * 0.98)]
for k in range(1, 9):
    a = math.pi / 2 * k / 8
    prof.append((R - 0.12 + math.sin(a) * 0.12, -hw + 0.12 - math.cos(a) * 0.12 + 0.0))
for k in range(0, 9):
    a = math.pi / 2 * k / 8
    prof.append((R - 0.12 + math.cos(a) * 0.12, hw - 0.12 + math.sin(a) * 0.12))
prof += [(R * 0.70, hw * 0.98), (R * 0.60, hw * 0.80)]
carcass = C.mesh_object("carcass", C.lathe(prof, 64), rubber, wheel)

# chevron lugs: one angled block per side, 24 pairs round the crown, alternating like real L3 tread
bm = bmesh.new()
n = 20
for i in range(n):
    for side in (-1, 1):
        a = 2 * math.pi * (i + (0.5 if side > 0 else 0)) / n
        res = bmesh.ops.create_cube(bm, size=1.0)
        vs = res["verts"]
        bmesh.ops.scale(bm, vec=(hw * 0.8, 0.15, 0.11), verts=vs)   # across, along the tread, height
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(side * 0.5, 3, "Z"), verts=vs)
        bmesh.ops.translate(bm, vec=(side * hw * 0.42, 0, R - 0.005), verts=vs)   # stands about 5 cm proud of the crown
        bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(a, 3, "X"), verts=vs)
lugs = C.mesh_object("lugs", bm, rubber, wheel, smooth=False)
C.add_modifier(lugs, "BEVEL", width=0.018, segments=2, limit_method="ANGLE")
C.add_modifier(lugs, "WEIGHTED_NORMAL", keep_sharp=True)

# rim: dished centre disc, flange, hub, ten nuts
rr = R * 0.6
rim_prof = [(0.02, hw * 0.30), (rr * 0.30, hw * 0.34), (rr * 0.45, hw * 0.55), (rr * 0.90, hw * 0.60),
            (rr * 0.98, hw * 0.80), (rr * 1.05, hw * 0.88), (rr * 1.05, -hw * 0.88), (rr * 0.98, -hw * 0.80),
            (rr * 0.5, -hw * 0.40), (0.02, -hw * 0.36)]
rim = C.mesh_object("rim", C.lathe(rim_prof, 48), paint, wheel)
C.add_modifier(rim, "BEVEL", width=0.01, segments=2, limit_method="ANGLE")
bm = bmesh.new()
bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=R * 0.16, radius2=R * 0.13, depth=0.12)
bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.pi / 2, 3, "Y"), verts=bm.verts)
bmesh.ops.translate(bm, vec=(hw * 0.38, 0, 0), verts=bm.verts)
for k in range(10):
    a = 2 * math.pi * k / 10
    res = bmesh.ops.create_cone(bm, cap_ends=True, segments=6, radius1=0.028, radius2=0.028, depth=0.05)
    bmesh.ops.rotate(bm, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.pi / 2, 3, "Y"), verts=res["verts"])
    bmesh.ops.translate(bm, vec=(hw * 0.36, math.cos(a) * R * 0.24, math.sin(a) * R * 0.24), verts=res["verts"])
hub = C.mesh_object("hub_and_nuts", bm, steel, wheel, smooth=False)
C.add_modifier(hub, "BEVEL", width=0.006, segments=1, limit_method="ANGLE")

out = opt.get("out", "/tmp/test_wheel.glb")
C.export_glb(out)
print("exported", out, os.path.getsize(out), "bytes")
if opt.get("preview"):
    C.preview(opt["preview"], target=(0, 0, R), dist=3.2, az=55, el=12, size=(900, 600), samples=24)
    print("preview", opt["preview"])
