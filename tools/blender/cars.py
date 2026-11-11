"""Parked and traffic cars -> assets/models/car_sedan.glb and car_suv.glb

    blender --background --factory-startup --python tools/blender/cars.py -- [--only sedan|suv] [--preview DIR]

The body is lofted from cross-sections along the car (side profile, plan width, a squarish superellipse
section), with the wheel arches cut out by booleans. The paint material is white and named `body_paint`:
the game recolours it for every car. No named parts: cars don't move their wheels.
"""
import math
import os
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, os.path.dirname(__file__))
import common as C  # noqa: E402
import kit as K  # noqa: E402
from kit import G, cyl  # noqa: E402


def box(*a, **k):
    """kit.box with single-segment bevels: cars are many, so keep them light"""
    k.setdefault("seg", 1)
    return K.box(*a, **k)

opt = C.args()


def interp(table, z):
    """piecewise-linear lookup in [(z, value), ...] sorted by z"""
    if z <= table[0][0]:
        return table[0][1]
    for (z0, a), (z1, b) in zip(table, table[1:]):
        if z <= z1:
            t = (z - z0) / (z1 - z0)
            return a + (b - a) * t
    return table[-1][1]


def loft(zs, section):
    """section(z) -> list of (x, y) points around the section (same count each); closed ends."""
    bm = bmesh.new()
    rings = [[bm.verts.new(G(x, y, z)) for x, y in section(z)] for z in zs]
    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for k in range(n):
            bm.faces.new((a[k], a[(k + 1) % n], b[(k + 1) % n], b[k]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def superellipse(hw, y0, y1, p=5.0, n=28, tumble=0.0):
    """a rounded-square section from y0 to y1, half width hw; `tumble` pulls the top corners in"""
    out = []
    yc, hh = (y0 + y1) / 2, (y1 - y0) / 2
    for k in range(n):
        t = 2 * math.pi * k / n
        c, s = math.cos(t), math.sin(t)
        x = hw * math.copysign(abs(c) ** (2 / p), c)
        y = hh * math.copysign(abs(s) ** (2 / p), s)
        if y > 0:
            x *= 1 - tumble * (y / hh) ** 2
        out.append((x, yc + y))
    return out


SPECS = {
    "sedan": dict(
        length=4.5, wheel_z=1.35, R=0.33, belt=0.98,
        bottom=[(-2.25, 0.36), (-2.0, 0.24), (-1.7, 0.2), (1.7, 0.2), (2.05, 0.24), (2.25, 0.34)],
        top=[(-2.25, 0.82), (-2.1, 0.97), (-1.4, 1.0), (1.25, 0.98), (1.6, 0.9), (2.05, 0.82), (2.25, 0.66)],
        width=[(-2.25, 0.78), (-2.0, 0.88), (-1.4, 0.9), (1.4, 0.9), (2.0, 0.87), (2.25, 0.76)],
        # greenhouse: (z, top y, top half width) from the windshield base to the rear window base
        gh=[(1.25, 0.98, 0.8), (0.85, 1.22, 0.72), (0.42, 1.42, 0.66), (-0.72, 1.45, 0.66), (-1.05, 1.27, 0.7), (-1.4, 1.0, 0.8)],
        gh_base_w=0.82, b_pillar=-0.12, lights_y=(0.62, 0.7), grille_y=0.55),
    "suv": dict(
        length=4.5, wheel_z=1.35, R=0.36, belt=1.1,
        bottom=[(-2.25, 0.45), (-2.1, 0.3), (-1.8, 0.26), (1.8, 0.26), (2.1, 0.3), (2.25, 0.44)],
        top=[(-2.25, 1.0), (-2.15, 1.1), (1.45, 1.1), (1.8, 1.04), (2.15, 0.98), (2.25, 0.82)],
        width=[(-2.25, 0.84), (-2.05, 0.9), (1.4, 0.91), (2.05, 0.88), (2.25, 0.8)],
        gh=[(1.45, 1.1, 0.82), (1.1, 1.45, 0.74), (0.8, 1.84, 0.7), (-1.95, 1.88, 0.7), (-2.1, 1.75, 0.74), (-2.16, 1.1, 0.82)],
        gh_base_w=0.84, b_pillar=-0.2, lights_y=(0.8, 0.88), grille_y=0.7),
}


def build(name, S):
    C.reset()
    paint = K.mat("body_paint", 0xf2f2f2, rough=0.32, metal=0.1)
    glass = K.mat("glass", 0x1c252c, rough=0.05, metal=0.3, alpha=0.72)
    trim = K.mat("trim_black", 0x18191a, rough=0.55)
    inner = K.mat("interior_dark", 0x1d1f22, rough=0.9)
    tyre = K.mat("tyre_rubber", 0x161616, rough=0.9)
    rim = K.mat("rim_alloy", 0xb9bdc2, rough=0.3, metal=0.9)
    chrome = K.mat("chrome", 0xd8dade, rough=0.18, metal=1.0)
    lensF = K.mat("light_front", 0xe8eef2, rough=0.1, metal=0.2)
    lensR = K.mat("light_rear", 0x7a1410, rough=0.15)
    amber = K.mat("lamp_amber", 0xd98a1a, rough=0.15)
    car = K.Part(f"car_{name}")
    L2, WZ, R = S["length"] / 2, S["wheel_z"], S["R"]

    zs = [-L2 + S["length"] * k / 24 for k in range(25)]
    lower = loft(zs, lambda z: superellipse(interp(S["width"], z), interp(S["bottom"], z), interp(S["top"], z), p=5.5, n=24, tumble=0.08))
    arches = [cyl(R + 0.08, 2.4, (0, R, sz * WZ), axis="x", seg=20) for sz in (-1, 1)]
    car.add(paint, K.boolean(lower, arches))
    # greenhouse: glass loft from the belt line, a painted roof skin and pillars over it
    gz = [p[0] for p in S["gh"]]
    gzs = [gz[0] + (gz[-1] - gz[0]) * k / 20 for k in range(21)]
    top_y = [(p[0], p[1]) for p in S["gh"]][::-1]
    top_w = [(p[0], p[2]) for p in S["gh"]][::-1]
    belt = S["belt"] - 0.02
    def gh_sec(z, lift=0.0, shrink=0.0):
        ty, tw, bw = interp(top_y, z) + lift, interp(top_w, z) - shrink, S["gh_base_w"] - shrink
        ty = max(ty, belt + 0.03)
        return [(bw, belt), (tw, ty), (-tw, ty), (-bw, belt)]
    car.add(glass, loft(gzs, gh_sec))
    roof_z = [p[0] for p in S["gh"] if p[1] > max(q[1] for q in S["gh"]) - 0.06]
    rz0, rz1 = min(roof_z), max(roof_z)
    rzs = [rz0 - 0.08 + (rz1 - rz0 + 0.16) * k / 10 for k in range(11)]
    def roof_sec(z):
        ty, tw = interp(top_y, z), interp(top_w, z)
        return [(tw + 0.015, ty - 0.03), (tw - 0.02, ty + 0.018), (-tw + 0.02, ty + 0.018), (-tw - 0.015, ty - 0.03)]
    car.add(paint, loft(rzs, roof_sec))
    # pillars: round-edged strips along the glass corners (A and C) and up the side at B
    def corner(z, side, inset=0.0):
        return (side * (interp(top_w, z) + 0.01 - inset), interp(top_y, z) + 0.005, z)
    for side in (-1, 1):
        a_pts = [corner(gz[0] + (rz1 - gz[0]) * k / 6, side) for k in range(7)]
        c_pts = [corner(rz0 + (gz[-1] - rz0) * k / 6, side) for k in range(7)]
        c_pts = [(x, y - 0.01, z) for x, y, z in c_pts]
        car.add(paint, K.tube([(side * (S["gh_base_w"] + 0.005), belt + 0.01, gz[0])] + a_pts[1:], 0.04, seg=8, samples=3))
        car.add(paint, K.tube(c_pts[:-1] + [(side * (S["gh_base_w"] + 0.005), belt + 0.01, gz[-1])], 0.045, seg=8, samples=3))
        zb = S["b_pillar"]
        car.add(paint, K.beam((side * (S["gh_base_w"] + 0.01), belt, zb), corner(zb, side), 0.03, 0.1, r=0.01))
        car.add(trim, box(0.02, 0.04, gz[0] - gz[-1], (side * (S["gh_base_w"] + 0.01), belt + 0.01, (gz[0] + gz[-1]) / 2)))   # window seal
    # a dark cabin tub and seat backs, so the glass doesn't show an empty shell
    cz0, cz1 = gz[-1] + 0.15, gz[0] - 0.1
    car.add(inner, box(S["gh_base_w"] * 2 - 0.12, belt - 0.45, cz1 - cz0, (0, (belt + 0.45) / 2, (cz0 + cz1) / 2)))
    for sz in (0.05, -0.85) if name == "sedan" else (0.0, -0.95):
        for sx in (-0.38, 0.38):
            car.add(inner, box(0.48, 0.55, 0.12, (sx, belt + 0.2, sz), r=0.04, rot=K.rot_game(rx=-0.12)))
    car.add(inner, box(S["gh_base_w"] * 2 - 0.15, 0.12, 0.3, (0, belt + 0.02, gz[0] - 0.22), r=0.03))   # dash top
    # lights, grille, bumpers, plates, mirrors, handles, door seams
    fz, rz = L2, -L2
    ly0, ly1 = S["lights_y"]
    for sx in (-1, 1):
        x = sx * 0.6
        car.add(lensF, box(0.36, ly1 - ly0 + 0.02, 0.3, (x, (ly0 + ly1) / 2, fz - 0.24), r=0.03))
        car.add(amber, box(0.1, 0.05, 0.04, (sx * 0.8, ly0 - 0.02, fz - 0.14), r=0.01))
        car.add(lensR, box(0.38, 0.13, 0.24, (sx * 0.6, ly1 + 0.03, rz + 0.17), r=0.03))
        car.add(trim, box(0.03, 0.1, 0.18, (sx * 0.9, S["belt"] + 0.04, S["gh"][0][0] - 0.12), r=0.02))   # mirror arm
        car.add(paint, box(0.16, 0.13, 0.08, (sx * 0.97, S["belt"] + 0.07, S["gh"][0][0] - 0.14), r=0.035))
        car.add(trim, box(0.012, 0.11, 0.06, (sx * 0.97, S["belt"] + 0.07, S["gh"][0][0] - 0.09)))
        for z in (0.25, -0.75):
            car.add(chrome, box(0.02, 0.03, 0.16, (sx * (interp(S["width"], z) + 0.005), S["belt"] - 0.12, z), r=0.008))
        for z in (S["gh"][0][0] - 0.05, S["b_pillar"], (-1.1 if name == "sedan" else -1.5)):
            car.add(trim, box(0.008, S["belt"] - 0.32, 0.01, (sx * (interp(S["width"], z) + 0.002), (S["belt"] + 0.32) / 2, z)))
        # arch liners
        for sz in (-1, 1):
            car.add(trim, K.arc_shell(R + 0.07, 0.3, math.radians(0), math.radians(180), 0.015, (sx * 0.74, R, sz * WZ)))
    car.add(trim, box(0.95, 0.2, 0.05, (0, S["grille_y"], fz - 0.04), r=0.03))
    for k in range(4):
        car.add(chrome, box(0.88, 0.012, 0.02, (0, S["grille_y"] - 0.07 + k * 0.045, fz - 0.015)))
    car.add(trim, box(1.6, 0.12, 0.1, (0, 0.3 if name == "sedan" else 0.38, fz - 0.06), r=0.04))     # lower valances
    car.add(trim, box(1.6, 0.12, 0.1, (0, 0.34 if name == "sedan" else 0.42, rz + 0.06), r=0.04))
    car.add(chrome, box(0.4, 0.12, 0.02, (0, 0.46 if name == "sedan" else 0.56, fz + 0.005)))
    car.add(chrome, box(0.4, 0.12, 0.02, (0, 0.6 if name == "sedan" else 0.75, rz - 0.005)))
    car.add(trim, box(1.62, 0.05, 2.6, (0, 0.2 if name == "sedan" else 0.26, 0)))                     # underbody
    if name == "suv":
        for sx in (-0.6, 0.6):
            car.add(trim, box(0.04, 0.04, 2.2, (sx, 1.91, -0.5), r=0.015))                             # roof rails
    # wheels: tyre with grooves, five-spoke alloy
    for sx in (-1, 1):
        for sz in (-1, 1):
            p = (sx * 0.8, R, sz * WZ)
            t, _ = K.road_tyre(R, 0.22, p, grooves=(-0.2, 0.2), sh=0.05, seg=28)
            car.add(tyre, t)
            rr = R * 0.62
            car.add(rim, K.lathe([(0.03, sx * 0.08), (rr * 0.5, sx * 0.075), (rr * 0.95, sx * 0.09), (rr * 1.03, sx * 0.1),
                                   (rr * 1.03, -sx * 0.09), (rr * 0.7, -sx * 0.06), (0.03, -sx * 0.06)], p, seg=24))
            for k in range(5):
                a = 2 * math.pi * k / 5
                car.add(rim, box(0.03, rr * 0.9, 0.05, (p[0] + sx * 0.095, R + math.cos(a) * rr * 0.48, p[2] + math.sin(a) * rr * 0.48), r=0.01, rot=K.rot_game(rx=-a)))
            car.add(chrome, cyl(0.04, 0.03, (p[0] + sx * 0.1, R, p[2]), axis="x", seg=12))
            car.add(trim, cyl(rr * 0.98, 0.01, (p[0] + sx * 0.06, R, p[2]), axis="x", seg=24))       # dark behind the spokes
    car.build()
    tris = sum(sum(len(p.vertices) - 2 for p in o.data.polygons) for o in bpy.data.objects if o.type == "MESH")
    out = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "assets", "models", f"car_{name}.glb"))
    C.export_glb(out)
    print(f"car_{name}: about {tris} triangles, exported {out} {os.path.getsize(out) // 1024} KB")
    if opt.get("preview"):
        for m in bpy.data.materials:
            if m.name == "body_paint":
                m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.12, 0.35, 1)
        for nm, az, el in (("front", 35, 12), ("rear", 215, 16)):
            C.preview(os.path.join(opt["preview"], f"car_{name}_{nm}.png"), target=(0, 0, 0.8), dist=7.5, az=az, el=el, size=(900, 560), samples=32)


for name, S in SPECS.items():
    if opt.get("only") in (None, True, name):
        build(name, S)
