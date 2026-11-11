"""Modelling kit for the vehicle build scripts: parts (pivot empties), geometry builders that take the game's
own coordinates, grime textures and box-projected UVs.

Game coordinates are three.js: x = driver's left, y = up, z = forward. Blender (and docs/MODELS.md) uses
x = left, -y = forward, z = up. G() converts, so sizes and pivots can be copied straight from index.html.
Rotations use the game's axes too: rx tips +y toward +z, ry turns +x toward -z (the same as three.js).
"""
import math
import random

import bmesh
import bpy
import numpy as np
from mathutils import Matrix, Vector


def G(x, y, z):
    return Vector((x, -z, y))


def rot_game(rx=0.0, ry=0.0, rz=0.0):
    """three.js Euler XYZ in game axes, as a Blender rotation matrix."""
    return Matrix.Rotation(rx, 4, "X") if not (ry or rz) else (
        Matrix.Rotation(rx, 4, "X") @ Matrix.Rotation(ry, 4, "Z") @ Matrix.Rotation(-rz, 4, "Y"))


# ---------------------------------------------------------------- textures and materials
def grime_image(name, base_hex, strength=1.0, seed=1, size=1024, mud=True):
    """Paint colour with blotches, scratches and chips, and grime/mud collecting toward the bottom rows
    (side faces map world height to v, see box_uv)."""
    rng = np.random.default_rng(seed)
    r, g, b = [(base_hex >> s & 255) / 255.0 for s in (16, 8, 0)]
    img = np.ones((size, size, 3), np.float32) * np.array([r, g, b], np.float32)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / size
    # large soft variation so panels aren't flat colour
    noise = np.zeros((size, size), np.float32)
    for k in range(5):
        f = 2 ** (k + 1)
        ph = rng.uniform(0, 6.28, 4)
        noise += (np.sin(xx * f * 6.28 + ph[0]) * np.sin(yy * f * 5.1 + ph[1]) + np.sin((xx + yy) * f * 3.7 + ph[2])) / (k + 2)
    img *= (1.0 + 0.035 * noise[..., None] * strength)
    dirt = np.array([0.30, 0.24, 0.17], np.float32)
    # grime gradient: v = 0 is the bottom of the machine
    grad = np.clip(1.0 - yy / 0.38, 0, 1) ** 1.6 * 0.55 * strength
    # splats
    for _ in range(int(260 * strength)):
        cx, cy, rad = rng.uniform(0, 1), rng.uniform(0, 1) ** (1.8 if mud else 1), rng.uniform(0.004, 0.05)
        a = rng.uniform(0.05, 0.25) * strength * (1.4 if cy < 0.3 else 0.6)
        x0, x1 = int(max(0, (cx - rad * 2) * size)), int(min(size, (cx + rad * 2) * size))
        y0, y1 = int(max(0, (cy - rad * 2) * size)), int(min(size, (cy + rad * 2) * size))
        if x1 <= x0 or y1 <= y0:
            continue
        d = ((xx[y0:y1, x0:x1] - cx) ** 2 + (yy[y0:y1, x0:x1] - cy) ** 2) / (rad * rad)
        grad[y0:y1, x0:x1] += a * np.exp(-d)
    # streaks running down from above
    for _ in range(int(40 * strength)):
        cx, top, ln, wd = rng.uniform(0, 1), rng.uniform(0.3, 1), rng.uniform(0.05, 0.3), rng.uniform(0.001, 0.004)
        m = (np.abs(xx - cx) < wd) & (yy < top) & (yy > top - ln)
        grad[m] += 0.12 * strength * ((yy[m] - (top - ln)) / ln)
    grad = np.clip(grad, 0, 0.85)
    img = img * (1 - grad[..., None]) + dirt * grad[..., None]
    # chips and scratches: dark primer showing through
    for _ in range(int(1400 * strength)):
        cx, cy = rng.uniform(0, 1), rng.uniform(0, 1)
        ln = rng.uniform(0.0008, 0.005) if rng.uniform() < 0.93 else rng.uniform(0.008, 0.02)
        ang = rng.uniform(0, math.pi)
        n = max(2, int(ln * size))
        px = (cx + np.cos(ang) * np.linspace(0, ln, n)) * size
        py = (cy + np.sin(ang) * np.linspace(0, ln, n)) * size
        ok = (px >= 0) & (px < size) & (py >= 0) & (py < size)
        img[py[ok].astype(int), px[ok].astype(int)] *= rng.uniform(0.35, 0.65)
    img = np.clip(img, 0, 1)
    rgba = np.concatenate([img, np.ones((size, size, 1), np.float32)], axis=2)
    im = bpy.data.images.new(name, size, size, alpha=False)
    im.pixels.foreach_set(rgba.ravel())   # row 0 is the bottom of the image (v = 0)
    im.pack()
    return im


def mat(name, hexv=None, rough=0.6, metal=0.0, image=None, alpha=1.0, emit=None, emit_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    p = nt.nodes.get("Principled BSDF")
    if image is not None:
        t = nt.nodes.new("ShaderNodeTexImage")
        t.image = image
        nt.links.new(t.outputs["Color"], p.inputs["Base Color"])
    elif hexv is not None:
        p.inputs["Base Color"].default_value = (*srgb_lin(hexv), 1)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if alpha < 1:
        p.inputs["Alpha"].default_value = alpha
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    if emit:
        p.inputs["Emission Color"].default_value = (*srgb_lin(emit), 1)
        p.inputs["Emission Strength"].default_value = emit_strength
    return m


def srgb_lin(hexv):
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin(hexv >> 16 & 255), lin(hexv >> 8 & 255), lin(hexv & 255))


# ---------------------------------------------------------------- parts
class Part:
    """A pivot empty. Geometry added to it is collected per material and becomes one mesh object each."""

    def __init__(self, name, gpos=(0, 0, 0), parent=None):
        self.name, self.parent = name, parent
        self.world = G(*gpos)
        self.empty = bpy.data.objects.new(name, None)
        self.empty.empty_display_type = "PLAIN_AXES"
        self.empty.empty_display_size = 0.25
        self.empty.location = self.world - (parent.world if parent else Vector())
        bpy.context.collection.objects.link(self.empty)
        if parent:
            self.empty.parent = parent.empty
        self.bms = {}
        self.keep_uv = set()

    def add(self, material, bm, keep_uv=False):
        if keep_uv:
            self.keep_uv.add(material.name)
        tgt = self.bms.get(material.name)
        if tgt is None:
            tgt = self.bms[material.name] = (material, bmesh.new())
        me = bpy.data.meshes.new("_tmp")
        bm.to_mesh(me)
        bm.free()
        tgt[1].from_mesh(me)
        bpy.data.meshes.remove(me)

    def build(self, uv_scale=3.4):
        out = []
        for name, (material, bm) in self.bms.items():
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
            if name not in self.keep_uv:
                box_uv(bm, uv_scale)
            bmesh.ops.translate(bm, vec=-self.world, verts=bm.verts)
            me = bpy.data.meshes.new(f"{self.name}_{name}")
            bm.to_mesh(me)
            bm.free()
            me.materials.append(material)
            ob = bpy.data.objects.new(f"{self.name}_{name}", me)
            bpy.context.collection.objects.link(ob)
            ob.parent = self.empty
            for poly in me.polygons:
                poly.use_smooth = True
            # sharp edges stay sharp, curved surfaces stay smooth
            mod = ob.modifiers.new("wn", "WEIGHTED_NORMAL")
            mod.keep_sharp = True
            me.set_sharp_from_angle(angle=math.radians(35)) if hasattr(me, "set_sharp_from_angle") else None
            out.append(ob)
        self.bms = {}
        return out


def box_uv(bm, scale):
    """Box projection in world space. Side faces map height to v (0 at the ground), so the grime texture's
    dirty bottom rows land low on the machine."""
    uv = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            c = l.vert.co
            if ax == 2:      # top/bottom: keep away from the dirty rows
                l[uv].uv = (c.x / scale, 0.62 + (c.y / scale) % 0.3)
            elif ax == 0:
                l[uv].uv = (c.y / scale, c.z / scale)
            else:
                l[uv].uv = (c.x / scale, c.z / scale)


# ---------------------------------------------------------------- geometry builders (game coordinates)
def _finish(bm, pos, rot=None):
    if rot is not None:
        bmesh.ops.transform(bm, matrix=rot, verts=bm.verts)
    bmesh.ops.translate(bm, vec=G(*pos), verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def _bevel(bm, r, seg=3):
    if r > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=r, offset_type="OFFSET", segments=seg, profile=0.5,
                        affect="EDGES", clamp_overlap=True)


def box(w, h, d, pos, r=0.0, seg=3, rot=None):
    """w across (x), h up (y), d along (z), centred on pos."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w, d, h), verts=bm.verts)
    _bevel(bm, min(r, w / 2.05, h / 2.05, d / 2.05), seg)
    return _finish(bm, pos, rot)


def plate(profile, t, x, r=0.012, seg=2, offset=(0, 0, 0)):
    """A plate cut to a side profile [(z, y), ...] in game coordinates, t thick across x, centred on x."""
    bm = bmesh.new()
    vs = [bm.verts.new(G(x - t / 2, y, z)) for z, y in profile]
    f = bm.faces.new(vs)
    ex = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(t, 0, 0), verts=[e for e in ex["geom"] if isinstance(e, bmesh.types.BMVert)])
    _bevel(bm, r, seg)
    return _finish(bm, offset)


def cyl(r, length, pos, axis="y", seg=24, r2=None, bevel=0.0, rot=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=length)
    if bevel:
        caps = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-6]
        bmesh.ops.bevel(bm, geom=caps, offset=bevel, segments=2, affect="EDGES", clamp_overlap=True)
    m = {"y": Matrix(), "x": Matrix.Rotation(math.pi / 2, 4, "Y"), "z": Matrix.Rotation(math.pi / 2, 4, "X")}[axis]
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    return _finish(bm, pos, rot)


def lathe(profile, pos, seg=48, axis="x"):
    """Spin a [(radius, along)] profile around the game axis through pos."""
    bm = bmesh.new()
    rings = []
    for s in range(seg):
        a = 2 * math.pi * s / seg
        rings.append([bm.verts.new((t, math.cos(a) * rr, math.sin(a) * rr)) for rr, t in profile])
    for s in range(seg):
        r0, r1 = rings[s], rings[(s + 1) % seg]
        for k in range(len(profile) - 1):
            bm.faces.new((r0[k], r0[k + 1], r1[k + 1], r1[k]))
    if axis == "y":
        bmesh.ops.transform(bm, matrix=Matrix.Rotation(-math.pi / 2, 4, "Y"), verts=bm.verts)
    return _finish(bm, pos)


def arc_shell(radius, width, a0, a1, th, pos, seg=28, rot=None):
    """A curved sheet: part of a cylinder around the game x axis, angles measured from +z (forward) toward +y."""
    bm = bmesh.new()
    rows = []
    for k in range(seg + 1):
        a = a0 + (a1 - a0) * k / seg
        row = []
        for rr in (radius, radius + th):
            for x in (-width / 2, width / 2):
                row.append(bm.verts.new(G(x, math.sin(a) * rr, math.cos(a) * rr)))
        rows.append(row)
    for k in range(seg):
        a, b = rows[k], rows[k + 1]
        for i, j in ((0, 1), (3, 2), (1, 3), (2, 0)):
            bm.faces.new((a[i], a[j], b[j], b[i]))
    bm.faces.new((rows[0][0], rows[0][1], rows[0][3], rows[0][2]))
    bm.faces.new((rows[-1][2], rows[-1][3], rows[-1][1], rows[-1][0]))
    return _finish(bm, pos, rot)


def tube(points, r, seg=8, samples=6):
    """A pipe or handrail along game-coordinate points (Catmull-Rom through them)."""
    P = [Vector(G(*p)) for p in points]
    pts = []
    for i in range(len(P) - 1):
        p0, p1, p2, p3 = P[max(0, i - 1)], P[i], P[i + 1], P[min(len(P) - 1, i + 2)]
        for s in range(samples):
            t = s / samples
            pts.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    pts.append(P[-1])
    bm = bmesh.new()
    rings = []
    for i, p in enumerate(pts):
        d = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        u = d.cross(Vector((0, 0, 1)))
        if u.length < 1e-3:
            u = d.cross(Vector((1, 0, 0)))
        u.normalize()
        v = d.cross(u)
        rings.append([bm.verts.new(p + (u * math.cos(a) + v * math.sin(a)) * r) for a in (2 * math.pi * k / seg for k in range(seg))])
    for i in range(len(rings) - 1):
        for k in range(seg):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % seg], rings[i + 1][(k + 1) % seg], rings[i + 1][k]))
    bm.faces.new(rings[0][::-1])
    bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def slab_xy(pts, t, z, r=0.0):
    """A flat piece cut to an outline [(x, y), ...] in the game's x/y plane, t thick along z, centred on z."""
    bm = bmesh.new()
    vs = [bm.verts.new(G(x, y, z - t / 2)) for x, y in pts]
    f = bm.faces.new(vs)
    ex = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=G(0, 0, t) - G(0, 0, 0), verts=[e for e in ex["geom"] if isinstance(e, bmesh.types.BMVert)])
    _bevel(bm, r, 1)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def beam(p0, p1, w, h, r=0.02, seg=2):
    """A box-section beam from game point p0 to p1, w wide and h tall."""
    a, b = G(*p0), G(*p1)
    d = b - a
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w, d.length, h), verts=bm.verts)
    _bevel(bm, min(r, w / 2.05, h / 2.05), seg)
    q = d.normalized().to_track_quat("Y", "Z")
    bmesh.ops.transform(bm, matrix=q.to_matrix().to_4x4(), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(a + b) / 2, verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def merge(*bms):
    out = bmesh.new()
    for b in bms:
        me = bpy.data.meshes.new("_m")
        b.to_mesh(me)
        b.free()
        out.from_mesh(me)
        bpy.data.meshes.remove(me)
    return out


def earthmover_tyre(R, W, pos, lugs=20):
    """Tyre carcass plus chevron lugs, centred on pos, rolling around the game x axis."""
    hw = W / 2
    prof = [(R * 0.60, -hw * 0.80), (R * 0.70, -hw * 0.98)]
    for k in range(1, 9):
        a = math.pi / 2 * k / 8
        prof.append((R - 0.12 + math.sin(a) * 0.12, -hw + 0.12 - math.cos(a) * 0.12))
    for k in range(9):
        a = math.pi / 2 * k / 8
        prof.append((R - 0.12 + math.cos(a) * 0.12, hw - 0.12 + math.sin(a) * 0.12))
    prof += [(R * 0.70, hw * 0.98), (R * 0.60, hw * 0.80)]
    carcass = lathe(prof, pos, seg=64)
    bm = bmesh.new()
    for i in range(lugs):
        for side in (-1, 1):
            a = 2 * math.pi * (i + (0.5 if side > 0 else 0)) / lugs
            cube = bmesh.new()
            bmesh.ops.create_cube(cube, size=1.0)
            bmesh.ops.scale(cube, vec=(hw * 0.8, 0.15, 0.11), verts=cube.verts)
            _bevel(cube, 0.018, 2)
            bmesh.ops.rotate(cube, cent=(0, 0, 0), matrix=Matrix.Rotation(side * 0.5, 3, "Z"), verts=cube.verts)
            bmesh.ops.translate(cube, vec=(side * hw * 0.42, 0, R - 0.005), verts=cube.verts)
            bmesh.ops.rotate(cube, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, "X"), verts=cube.verts)
            me = bpy.data.meshes.new("_l")
            cube.to_mesh(me)
            cube.free()
            bm.from_mesh(me)
            bpy.data.meshes.remove(me)
    bmesh.ops.translate(bm, vec=G(*pos), verts=bm.verts)
    return carcass, bm


def dished_rim(R, W, pos, out_sign=1):
    hw = W / 2
    rr = R * 0.6
    s = out_sign
    prof = [(0.02, s * hw * 0.30), (rr * 0.30, s * hw * 0.34), (rr * 0.45, s * hw * 0.55), (rr * 0.90, s * hw * 0.60),
            (rr * 0.98, s * hw * 0.80), (rr * 1.05, s * hw * 0.88), (rr * 1.05, -s * hw * 0.88), (rr * 0.98, -s * hw * 0.80),
            (rr * 0.5, -s * hw * 0.40), (0.02, -s * hw * 0.36)]
    rim = lathe(prof, pos, seg=48)
    hub = cyl(R * 0.16, 0.12, (pos[0] + s * hw * 0.38, pos[1], pos[2]), axis="x", seg=24, r2=R * 0.13 if s > 0 else None)
    nuts = []
    for k in range(10):
        a = 2 * math.pi * k / 10
        nuts.append(cyl(0.028, 0.05, (pos[0] + s * hw * 0.36, pos[1] + math.sin(a) * R * 0.24, pos[2] + math.cos(a) * R * 0.24), axis="x", seg=6))
    return rim, merge(hub, *nuts)


# ---------------------------------------------------------------- instruments
FONT = {  # 3x5 pixel glyphs, rows top to bottom
    "0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"], "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"], "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"], "7": ["111", "001", "010", "010", "010"], "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"], "R": ["110", "101", "110", "101", "101"], "P": ["110", "101", "110", "100", "100"],
    "M": ["101", "111", "111", "101", "101"], "K": ["101", "110", "100", "110", "101"], "H": ["101", "101", "111", "101", "101"],
    "/": ["001", "001", "010", "100", "100"], "X": ["101", "101", "010", "101", "101"], "E": ["111", "100", "110", "100", "111"],
    "F": ["111", "100", "110", "100", "100"], "C": ["111", "100", "100", "100", "111"], " ": ["000", "000", "000", "000", "000"],
}


def draw_text(img, text, cx, cy, px, col):
    """Stamp text centred at (cx, cy) in pixels, each font pixel px wide; image rows run bottom to top."""
    w = len(text) * 4 * px - px
    x0, y0 = int(cx - w / 2), int(cy + 2.5 * px)
    for i, ch in enumerate(text):
        g = FONT.get(ch.upper(), FONT[" "])
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                if bit == "1":
                    xa, ya = x0 + (i * 4 + c) * px, y0 - (r + 1) * px
                    img[max(0, ya):ya + px, max(0, xa):xa + px] = col


def dial_image(name, labels, sweep_deg=270, start_deg=225, red_from=None, caption="", size=512):
    """A gauge face: dark, a tick ring over the sweep (clockwise from start), numbers, a red zone, a caption.
    The needle modelled at the start angle and turned clockwise by the game lines up with these marks."""
    img = np.zeros((size, size, 3), np.float32)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    c = size / 2
    rr = np.hypot(xx - c, yy - c) / c
    ang = (np.degrees(np.arctan2(yy - c, xx - c)) + 360) % 360
    img[:] = 0.035
    img[rr < 0.98] = 0.06
    img[(rr > 0.98)] = 0.0
    rel = (start_deg - ang) % 360                       # degrees clockwise from the start mark
    on = rel <= sweep_deg
    n = len(labels) - 1
    for k in range(n * 5 + 1):                           # minor and major ticks
        a = math.radians(start_deg - sweep_deg * k / (n * 5))
        major = k % 5 == 0
        r0, r1 = (0.70 if major else 0.78), 0.88
        for t in np.linspace(r0, r1, 40):
            x, y = c + math.cos(a) * t * c, c + math.sin(a) * t * c
            wd = 5 if major else 2
            img[int(y) - wd // 2:int(y) + wd // 2 + 1, int(x) - wd // 2:int(x) + wd // 2 + 1] = 0.92
    if red_from is not None:
        m = on & (rel >= sweep_deg * red_from) & (rr > 0.89) & (rr < 0.95)
        img[m] = (0.85, 0.12, 0.08)
    arcm = on & (rr > 0.885) & (rr < 0.9)
    img[arcm] = 0.8
    for k, lab in enumerate(labels):
        if not lab:
            continue
        a = math.radians(start_deg - sweep_deg * k / n)
        draw_text(img, lab, c + math.cos(a) * 0.53 * c, c + math.sin(a) * 0.53 * c, max(3, size // 80), 0.95)
    if caption:
        draw_text(img, caption, c, c - 0.42 * c, max(3, size // 96), (0.95, 0.62, 0.2))
    rgba = np.concatenate([img, np.ones((size, size, 1), np.float32)], axis=2)
    im = bpy.data.images.new(name, size, size, alpha=False)
    im.pixels.foreach_set(rgba.ravel())
    im.pack()
    return im


def dial_mat(name, image, glow=0.5):
    m = mat(name, rough=0.25, image=image)
    p = m.node_tree.nodes.get("Principled BSDF")
    t = [n for n in m.node_tree.nodes if n.type == "TEX_IMAGE"][0]
    m.node_tree.links.new(t.outputs["Color"], p.inputs["Emission Color"])
    p.inputs["Emission Strength"].default_value = glow
    return m


def frame_at(center, toward):
    """An orthonormal frame on a face at `center` (game coords) facing the point `toward` (the driver's eye):
    returns (n, u, v) as game-coordinate Vectors, u to the driver's right, v up."""
    c, e = Vector(center), Vector(toward)
    n = (e - c).normalized()
    u = Vector((0, 1, 0)).cross(n).normalized()
    v = n.cross(u).normalized()
    return n, u, v


def disc(center, n, u, v, radius, seg=40, lift=0.0, uv=True):
    """A flat round face (game coords) in the plane (u, v), pushed `lift` along n, with 0..1 UVs."""
    bm = bmesh.new()
    lay = bm.loops.layers.uv.verify()
    c = Vector(center) + n * lift
    vs = [bm.verts.new(G(*(c + (u * math.cos(2 * math.pi * k / seg) + v * math.sin(2 * math.pi * k / seg)) * radius))) for k in range(seg)]
    f = bm.faces.new(vs)
    for l, k in zip(f.loops, range(seg)):
        a = 2 * math.pi * k / seg
        l[lay].uv = (0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a))
    if f.normal.dot(G(*n) - G(0, 0, 0)) < 0:
        bmesh.ops.reverse_faces(bm, faces=[f])
    return bm


def quad(center, n, u, v, w, h, lift=0.0):
    """A flat rectangle (game coords) in the plane (u, v) with 0..1 UVs (u = 0 at the driver's left)."""
    bm = bmesh.new()
    lay = bm.loops.layers.uv.verify()
    c = Vector(center) + n * lift
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    vs = [bm.verts.new(G(*(c + u * (a * w / 2) + v * (b * h / 2)))) for a, b in corners]
    f = bm.faces.new(vs)
    for l, (a, b) in zip(f.loops, corners):
        l[lay].uv = ((a + 1) / 2, (b + 1) / 2)
    if f.normal.dot(G(*n) - G(0, 0, 0)) < 0:
        bmesh.ops.reverse_faces(bm, faces=[f])
    return bm


def oriented_box(center, n, u, v, w, h, d, r=0.0):
    """A box centred at `center`, w along u, h along v, d along n (game coords)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(w, h, d), verts=bm.verts)
    _bevel(bm, min(r, w / 2.05, h / 2.05, d / 2.05), 2)
    U, V, N = G(*u) - G(0, 0, 0), G(*v) - G(0, 0, 0), G(*n) - G(0, 0, 0)
    m = Matrix((U, V, N)).transposed().to_4x4()
    bmesh.ops.transform(bm, matrix=m, verts=bm.verts)
    bmesh.ops.translate(bm, vec=G(*center), verts=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def torus(center, axis_frame, R, r, seg=48, rseg=10):
    """A ring of radius R (tube radius r) in the plane of axis_frame's first two vectors (game coords)."""
    X, Y, Z = (Vector(a) for a in axis_frame)
    c = Vector(center)
    bm = bmesh.new()
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        d = X * math.cos(a) + Y * math.sin(a)
        rings.append([bm.verts.new(G(*(c + d * (R + r * math.cos(b)) + Z * (r * math.sin(b))))) for b in (2 * math.pi * k / rseg for k in range(rseg))])
    for i in range(seg):
        for k in range(rseg):
            a0, a1 = rings[i], rings[(i + 1) % seg]
            bm.faces.new((a0[k], a0[(k + 1) % rseg], a1[(k + 1) % rseg], a1[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


# ---------------------------------------------------------------- booleans, road tyres
def boolean(base, cutters, op="DIFFERENCE"):
    """Cut (or join) bmeshes with Blender's exact boolean solver; returns a new bmesh. Used for hollow cabs
    with real window openings, so the view from inside isn't blocked by a solid painted box."""
    def obj(bm, name):
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        bpy.context.collection.objects.link(ob)
        return ob
    ob = obj(base, "_bool_base")
    tmp = []
    for i, c in enumerate(cutters):
        co = obj(c, f"_bool_cut{i}")
        tmp.append(co)
        m = ob.modifiers.new(f"b{i}", "BOOLEAN")
        m.operation, m.object, m.solver = op, co, "EXACT"
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    out = bmesh.new()
    out.from_mesh(ev.to_mesh())
    ev.to_mesh_clear()
    for o in [ob, *tmp]:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        bpy.data.meshes.remove(me)
    return out


def road_tyre(R, W, pos, grooves=(-0.3, 0.0, 0.3), blocks=0, sh=0.07, seg=56):
    """A truck or car tyre around the game x axis: rounded shoulders, circumferential grooves cut into the
    crown and, for drive tyres, `blocks` shallow tread blocks across each shoulder."""
    hw = W / 2
    prof = [(R * 0.62, -hw * 0.8), (R * 0.72, -hw * 0.97)]
    for k in range(1, 7):
        a = math.pi / 2 * k / 6
        prof.append((R - sh + math.sin(a) * sh, -hw + sh - math.cos(a) * sh))
    for gx in grooves:
        x = gx * W
        prof += [(R, x - 0.014), (R - 0.022, x - 0.009), (R - 0.022, x + 0.009), (R, x + 0.014)]
    for k in range(0, 6):
        a = math.pi / 2 * k / 6
        prof.append((R - sh + math.cos(a) * sh, hw - sh + math.sin(a) * sh))
    prof += [(R * 0.72, hw * 0.97), (R * 0.62, hw * 0.8)]
    carcass = lathe(prof, pos, seg=seg)
    bm = bmesh.new()
    for i in range(blocks):
        for side in (-1, 1):
            a = 2 * math.pi * (i + (0.5 if side > 0 else 0)) / blocks
            cube = bmesh.new()
            bmesh.ops.create_cube(cube, size=1.0)
            bmesh.ops.scale(cube, vec=(hw * 0.38, 2 * math.pi * R / blocks * 0.42, 0.03), verts=cube.verts)
            bmesh.ops.rotate(cube, cent=(0, 0, 0), matrix=Matrix.Rotation(side * 0.25, 3, "Z"), verts=cube.verts)
            bmesh.ops.translate(cube, vec=(side * hw * 0.68, 0, R - 0.02), verts=cube.verts)
            bmesh.ops.rotate(cube, cent=(0, 0, 0), matrix=Matrix.Rotation(a, 3, "X"), verts=cube.verts)
            me = bpy.data.meshes.new("_tb")
            cube.to_mesh(me)
            cube.free()
            bm.from_mesh(me)
            bpy.data.meshes.remove(me)
    bmesh.ops.translate(bm, vec=G(*pos), verts=bm.verts)
    return carcass, bm


def steel_rim(R, W, pos, out_sign=1, holes=8, nuts=10, rr=None):
    """A dished steel disc wheel with hand holes and a hub with wheel nuts; returns (rim, dark holes, hub+nuts)."""
    hw, s = W / 2, out_sign
    rr = rr or R * 0.58
    x0 = pos[0]
    prof = [(0.03, s * hw * 0.5), (rr * 0.32, s * hw * 0.52), (rr * 0.5, s * hw * 0.34), (rr * 0.72, s * hw * 0.3),
            (rr * 0.92, s * hw * 0.62), (rr * 1.04, s * hw * 0.9), (rr * 1.04, -s * hw * 0.9), (rr * 0.95, -s * hw * 0.8),
            (rr * 0.6, -s * hw * 0.2), (0.03, -s * hw * 0.1)]
    rim = lathe(prof, pos, seg=40)
    dark = []
    for k in range(holes):
        a = 2 * math.pi * (k + 0.5) / holes
        dark.append(cyl(rr * 0.09, 0.01, (x0 + s * hw * 0.335, pos[1] + math.sin(a) * rr * 0.61, pos[2] + math.cos(a) * rr * 0.61), axis="x", seg=12))
    hub = [cyl(rr * 0.3, 0.09, (x0 + s * hw * 0.56, pos[1], pos[2]), axis="x", seg=24, r2=rr * 0.22 if s > 0 else None, bevel=0.01)]
    for k in range(nuts):
        a = 2 * math.pi * k / nuts
        hub.append(cyl(0.022, 0.05, (x0 + s * hw * 0.55, pos[1] + math.sin(a) * rr * 0.4, pos[2] + math.cos(a) * rr * 0.4), axis="x", seg=6))
    return rim, merge(*dark), merge(*hub)


def hazard(part, mat_y, mat_k, w, h, pos, normal_z=1, stripes=9):
    """A yellow plate with slanted black bands, facing +z (normal_z=1) or -z, centred on pos (game coords)."""
    x0, y0, z0 = pos
    part.add(mat_y, box(w, h, 0.012, pos))
    band, skew = w / stripes, h * 0.7
    clip = lambda v: max(x0 - w / 2, min(x0 + w / 2, v))
    x, k = x0 - w / 2 - skew, 0
    while x < x0 + w / 2:
        if k % 2 == 0:
            pts = [(clip(x), y0 - h / 2), (clip(x + band), y0 - h / 2), (clip(x + band + skew), y0 + h / 2), (clip(x + skew), y0 + h / 2)]
            pts = [p for i, p in enumerate(pts) if i == 0 or abs(p[0] - pts[i - 1][0]) > 1e-4 or abs(p[1] - pts[i - 1][1]) > 1e-4]
            if len(pts) >= 3 and (pts[-1][0] - pts[0][0]) ** 2 + (pts[-1][1] - pts[0][1]) ** 2 > 1e-8:
                part.add(mat_k, slab_xy(pts, 0.004, z0 + normal_z * 0.008))
        x += band
        k += 1


def bumpy_top(w, d, y, pos_xz, amp=0.05, nx=22, nz=40, seed=1, skirt=0.1):
    """A lumpy heaped surface w across, d long, top around y, with a skirt hanging down (a load of salt or dirt)."""
    rng = np.random.default_rng(seed)
    cx, cz = pos_xz
    ph = rng.uniform(0, 6.28, 6)
    def hgt(u, v):
        edge = min(1.0, 6 * min(u, 1 - u), 6 * min(v, 1 - v))
        n = (math.sin(u * 9 + ph[0]) * math.sin(v * 13 + ph[1]) + 0.5 * math.sin(u * 23 + ph[2]) * math.sin(v * 31 + ph[3])
             + 0.3 * math.sin((u + v) * 47 + ph[4]))
        return y + amp * (0.6 + 0.4 * n) * edge
    bm = bmesh.new()
    grid = [[bm.verts.new(G(cx - w / 2 + w * i / nx, hgt(i / nx, j / nz), cz - d / 2 + d * j / nz)) for j in range(nz + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(nz):
            bm.faces.new((grid[i][j], grid[i + 1][j], grid[i + 1][j + 1], grid[i][j + 1]))
    ring = [grid[i][0] for i in range(nx + 1)] + [grid[nx][j] for j in range(1, nz + 1)] + [grid[i][nz] for i in range(nx - 1, -1, -1)] + [grid[0][j] for j in range(nz - 1, 0, -1)]
    low = [bm.verts.new(v.co - Vector((0, 0, skirt))) for v in ring]
    for k in range(len(ring)):
        a, b = ring[k], ring[(k + 1) % len(ring)]
        bm.faces.new((a, b, low[(k + 1) % len(ring)], low[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm
