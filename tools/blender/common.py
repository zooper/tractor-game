"""Shared helpers for the vehicle build scripts.

Run a build script with:
    blender --background --factory-startup --python tools/blender/<script>.py -- [--preview out.png]

Conventions (docs/MODELS.md): metres, front faces -Y, up +Z, wheels on z = 0, driver's left is +X.
"""
import math
import sys

import bmesh
import bpy
from mathutils import Vector


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = {}
    for i, a in enumerate(argv):
        if a.startswith("--"):
            out[a[2:]] = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else True
    return out


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system = "METRIC"


def material(name, color, rough=0.6, metal=0.0, alpha=1.0, emission=None, strength=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1.0)
    p.inputs["Roughness"].default_value = rough
    p.inputs["Metallic"].default_value = metal
    if alpha < 1.0:
        p.inputs["Alpha"].default_value = alpha
        m.surface_render_method = "BLENDED" if hasattr(m, "surface_render_method") else None
    if emission:
        p.inputs["Emission Color"].default_value = (*emission, 1.0)
        p.inputs["Emission Strength"].default_value = strength
    return m


def srgb(hexv):
    """0xRRGGBB in sRGB to linear floats, as Blender's colour inputs expect."""
    def lin(c):
        c /= 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return (lin((hexv >> 16) & 255), lin((hexv >> 8) & 255), lin(hexv & 255))


def empty(name, loc=(0, 0, 0), parent=None, size=0.3):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = "PLAIN_AXES"
    e.empty_display_size = size
    e.location = loc
    bpy.context.collection.objects.link(e)
    if parent:
        e.parent = parent
    return e


def mesh_object(name, bm, mat=None, parent=None, loc=(0, 0, 0), smooth=True):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    if mat:
        me.materials.append(mat)
    if smooth:
        for poly in me.polygons:
            poly.use_smooth = True
    ob.location = loc
    if parent:
        ob.parent = parent
    return ob


def lathe(profile, segments=48, axis="X"):
    """Spin a (radius, along-axis) profile into a closed ring of faces around the given axis."""
    bm = bmesh.new()
    rings = []
    for s in range(segments):
        a = 2 * math.pi * s / segments
        ring = []
        for r, t in profile:
            if axis == "X":
                co = (t, math.cos(a) * r, math.sin(a) * r)
            else:
                co = (math.cos(a) * r, math.sin(a) * r, t)
            ring.append(bm.verts.new(co))
        rings.append(ring)
    for s in range(segments):
        r0, r1 = rings[s], rings[(s + 1) % segments]
        for k in range(len(profile) - 1):
            bm.faces.new((r0[k], r0[k + 1], r1[k + 1], r1[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm


def add_modifier(ob, kind, **props):
    m = ob.modifiers.new(kind.lower(), kind)
    for k, v in props.items():
        setattr(m, k, v)
    return m


def apply_modifiers(ob):
    bpy.context.view_layer.objects.active = ob
    for m in list(ob.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def export_glb(path, objects=None):
    bpy.ops.object.select_all(action="DESELECT")
    for ob in objects or bpy.context.scene.objects:
        ob.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
                              export_yup=True, export_animations=False)


def preview(path, target=(0, 0, 0.7), dist=6.0, az=35, el=18, size=(1200, 800), samples=48, cam_at=None, look_at=None, lens=50, floor=True):
    """Render a quick studio preview: sky light, a sun, grey floor, camera orbiting `target`."""
    sc = bpy.context.scene
    floor = bpy.data.objects.get("__floor")
    if not floor:
        bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
        floor = bpy.context.active_object
        floor.name = "__floor"
        floor.data.materials.append(material("__floor", srgb(0x8a8a86), rough=0.9))
    world = bpy.data.worlds.new("__world") if not sc.world else sc.world
    sc.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = (*srgb(0xc9d3de), 1)
    world.node_tree.nodes["Background"].inputs[1].default_value = 0.8
    sun = bpy.data.objects.get("__sun")
    if not sun:
        sun = bpy.data.objects.new("__sun", bpy.data.lights.new("__sun", "SUN"))
        sc.collection.objects.link(sun)
    sun.data.energy = 3.5
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
    cam = bpy.data.objects.get("__cam")
    if not cam:
        cam = bpy.data.objects.new("__cam", bpy.data.cameras.new("__cam"))
        sc.collection.objects.link(cam)
    cam.data.lens = lens
    cam.data.clip_start = 0.02
    if cam_at is not None:
        cam.location, t = Vector(cam_at), Vector(look_at)
    else:
        t = Vector(target)
        a, e = math.radians(az), math.radians(el)
        cam.location = t + Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e))) * dist
    cam.rotation_euler = (t - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    sc.render.engine = "CYCLES"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons["cycles"].preferences
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception:
        sc.cycles.device = "CPU"
    sc.render.resolution_x, sc.render.resolution_y = size
    sc.render.filepath = path
    sc.view_settings.view_transform = "AgX"
    bpy.ops.render.render(write_still=True)
    # keep the preview helpers out of any later export
    for n in ("__floor", "__sun", "__cam"):
        ob = bpy.data.objects.get(n)
        if ob:
            bpy.data.objects.remove(ob, do_unlink=True)
