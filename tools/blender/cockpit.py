"""Cockpit pieces shared by the vehicle scripts: instrument pods with live needles, steering wheels, control
levers, the display the game draws on, and seats. All positions are game coordinates (see kit.py).

The game finds these by name (docs/MODELS.md, "Cockpit"): cab_interior, steering_wheel, joystick, joystick_2,
needle_rpm / needle_speed / needle_fuel / needle_temp, and the material named `screen`.
"""
import math

from mathutils import Vector

import kit as K
from kit import box, cyl


class Mats:
    def __init__(self, accent=0xe8692c):
        self.dash = K.mat("dash_plastic", 0x26282b, rough=0.7)
        self.trim = K.mat("trim_plastic", 0x41464b, rough=0.6)
        self.liner = K.mat("headliner", 0x6a6e73, rough=0.95)
        self.fabric = K.mat("seat_fabric", 0x23272b, rough=0.95)
        self.floor = K.mat("floor_mat", 0x1a1b1c, rough=0.9)
        self.black = K.mat("black_plastic_cab", 0x161616, rough=0.55)
        self.chrome = K.mat("chrome_cab", 0xdadcdf, rough=0.15, metal=1.0)
        self.iron = K.mat("iron_cab", 0x2c2c2e, rough=0.5, metal=0.6)
        self.screen = K.mat("screen", 0x10243a, rough=0.2, emit=0x16304d, emit_strength=0.8)
        self.needle = K.mat("needle", 0xff7a1a, rough=0.3, emit=0xff6a10, emit_strength=2.5)
        self.btn = K.mat("button_caps", 0x2c2f33, rough=0.5)
        self.accent = K.mat("cab_accent", accent, rough=0.45)
        self.red = K.mat("extinguisher_red", 0xb3190f, rough=0.35)
        self.dome = K.mat("light_front_dome", 0xfff4dc, rough=0.05, emit=0xfff0d0, emit_strength=1.0)
        cols = [0x3cff6a, 0xffb020, 0xff3a2a, 0x3aa8ff, 0xffb020, 0x3cff6a]
        self.lamps = [K.mat(f"warn_lamp_{i}", c, rough=0.3, emit=c, emit_strength=0.6) for i, c in enumerate(cols)]


DIALS = {
    "rpm": (["0", "5", "10", "15", "20", "25"], 270, 225, 0.82, "RPMX100"),
    "speed": (["0", "10", "20", "30", "40"], 270, 225, None, "KM/H"),
    "fuel": (["E", "", "F"], 90, 225, None, ""),
    "temp": (["C", "", "H"], 90, 225, 0.8, ""),
}


def dial_pod(cab, M, center, eye, layout, pod_size=(0.5, 0.19), lamps=True):
    """A pod facing the eye with dials laid out as [(kind, du, dv, radius)], du/dv along the pod face.
    Returns the needle parts (children of `cab`)."""
    c0 = Vector(center)
    n, u, v = K.frame_at(c0, eye)
    w, h = pod_size
    cab.add(M.dash, K.oriented_box(c0 - n * 0.035, n, u, v, w, h, 0.07, r=0.03))
    cab.add(M.dash, K.oriented_box(c0 + v * (h / 2 + 0.005) + n * 0.02, n, u, v, w + 0.02, 0.025, 0.1, r=0.01))   # brow
    needles = []
    for kind, du, dv, rad in layout:
        labels, sweep, start, redz, cap = DIALS[kind]
        c = c0 + u * du + v * dv
        img = K.dial_image(f"dial_{kind}_{cab.name}", labels, sweep, start, redz, cap)
        cab.add(M.chrome, K.disc(c, n, u, v, rad + 0.008, lift=0.001))
        cab.add(K.dial_mat(f"dial_{kind}_{cab.name}", img), K.disc(c, n, u, v, rad, lift=0.003), keep_uv=True)
        nd = K.Part(f"needle_{kind}", tuple(c + n * 0.006), cab)
        d0 = u * math.cos(math.radians(start)) + v * math.sin(math.radians(start))
        side = n.cross(d0).normalized()
        ln = rad * 0.82
        nd.add(M.needle, K.oriented_box(c + n * 0.006 + d0 * (ln / 2 - rad * 0.12), n, d0, side, ln + rad * 0.24, rad * 0.06, 0.002))
        nd.add(M.black, K.disc(c, n, u, v, rad * 0.12, lift=0.008))
        needles.append(nd)
    if lamps:
        for i, m in enumerate(M.lamps):
            cab.add(m, K.oriented_box(c0 + u * (-0.0625 + i * 0.025) + v * (-h / 2 + 0.02), n, u, v, 0.016, 0.012, 0.004))
    return needles


def screen(cab, M, center, eye, w=0.21, h=0.13):
    """The display the game draws on (material `screen`), in a bezel facing the eye."""
    c = Vector(center)
    n, u, v = K.frame_at(c, eye)
    cab.add(M.dash, K.oriented_box(c - n * 0.015, n, u, v, w + 0.04, h + 0.05, 0.03, r=0.012))
    cab.add(M.screen, K.quad(c, n, u, v, w, h, lift=0.001), keep_uv=True)
    for k in range(4):                                               # buttons under the screen
        cab.add(M.btn, K.oriented_box(c + u * (-w / 2 + 0.03 + k * (w - 0.06) / 3) + v * (-h / 2 - 0.015), n, u, v, 0.022, 0.012, 0.01, r=0.003))
    return n, u, v


def steering_wheel(cab, M, hub, tilt, r=0.17, column=0.35, spokes=(math.pi / 2, math.pi, -math.pi / 2), knob=True):
    """A steering wheel whose hub is the part's origin, face tilted `tilt` rad back toward the driver (the
    game turns it about its own column). The column runs forward-down into the dash."""
    H = Vector(hub)
    WX, WY, WZ = Vector((1, 0, 0)), Vector((0, math.cos(tilt), math.sin(tilt))), Vector((0, -math.sin(tilt), math.cos(tilt)))
    cab.add(M.dash, K.oriented_box(H + WZ * (0.04 + column / 2), WZ, WX, WY, 0.07, 0.07, column, r=0.025))      # column shroud
    cab.add(M.dash, K.oriented_box(H + WZ * (column + 0.04), WZ, WX, WY, 0.16, 0.12, 0.06, r=0.03))              # where it meets the dash
    sw = K.Part("steering_wheel", tuple(H), cab)
    sw.add(M.black, K.torus(H, (WX, WY, WZ), r, r * 0.1))
    for a in spokes:                                                 # angles from straight up, toward the driver's left
        d = WX * math.sin(a) + WY * math.cos(a)
        sw.add(M.dash, K.oriented_box(H + d * (r * 0.55) + WZ * 0.006, WZ, d, d.cross(WZ), r * 0.9, r * 0.14, 0.012, r=0.004))
    sw.add(M.dash, cyl(r * 0.3, 0.045, tuple(H + WZ * 0.012), seg=28, bevel=0.012, rot=K.rot_game(rx=tilt + math.pi / 2)))
    sw.add(M.accent, K.disc(H, -WZ, WX, WY, r * 0.08, lift=0.012))
    if knob:
        kp = H + (WX * math.sin(0.8) + WY * math.cos(0.8)) * r
        sw.add(M.black, K.oriented_box(kp - WZ * 0.02, WZ, WX, WY, 0.016, 0.016, 0.04, r=0.006))
        sw.add(M.black, cyl(0.016, 0.04, tuple(kp - WZ * 0.045), seg=14, bevel=0.006, rot=K.rot_game(rx=tilt + math.pi / 2)))
    return sw


def lever(cab, M, name, pivot, length=0.22, grip="joystick", boot=True):
    """A control lever: the part's origin is the pivot at its base. `grip` is 'joystick' (a moulded handle
    with buttons) or 'knob' (a gear lever ball)."""
    J = pivot
    if boot:
        cab.add(M.black, cyl(0.05, 0.06, (J[0], J[1] + 0.01, J[2]), seg=16, r2=0.035))
    js = K.Part(name, J, cab)
    js.add(M.chrome, cyl(0.012, length * 0.8, (J[0], J[1] + length * 0.4, J[2]), seg=10))
    if grip == "joystick":
        js.add(M.black, box(0.06, 0.12, 0.08, (J[0], J[1] + length + 0.04, J[2] + 0.005), r=0.025))
        js.add(M.accent, box(0.025, 0.02, 0.02, (J[0] + 0.012, J[1] + length + 0.105, J[2] + 0.02), r=0.006))
        js.add(M.btn, box(0.018, 0.014, 0.018, (J[0] - 0.015, J[1] + length + 0.1, J[2] + 0.03), r=0.005))
    else:
        js.add(M.black, cyl(0.035, 0.07, (J[0], J[1] + length, J[2]), seg=16, bevel=0.03))
    return js


def seat(cab, M, x, floor, z, cushion_y, back_tilt=-0.15, width=0.5, suspension=True, facing=1):
    """An operator seat centred on x, cushion top at cushion_y, front edge toward +z * facing."""
    f = facing
    if suspension:
        cab.add(M.iron, box(0.4, cushion_y - floor - 0.14, 0.42, (x, (cushion_y + floor - 0.14) / 2, z), r=0.03))
        cab.add(M.black, cyl(0.12, 0.08, (x, cushion_y - 0.16, z), seg=20))
    cab.add(M.fabric, box(width, 0.12, 0.48, (x, cushion_y - 0.06, z + f * 0.04), r=0.05, seg=4))
    cab.add(M.fabric, box(width, 0.62, 0.12, (x, cushion_y + 0.31, z - f * 0.26), r=0.05, seg=4, rot=K.rot_game(rx=back_tilt * f)))
    cab.add(M.fabric, box(0.3, 0.16, 0.1, (x, cushion_y + 0.72, z - f * 0.33), r=0.04, rot=K.rot_game(rx=back_tilt * f)))
    for sx in (-1, 1):
        cab.add(M.fabric, box(0.08, 0.4, 0.1, (x + sx * width * 0.5, cushion_y + 0.26, z - f * 0.22), r=0.035, rot=K.rot_game(rx=back_tilt * f)))
    cab.add(M.black, box(0.05, 0.5, 0.008, (x + width * 0.44, cushion_y + 0.2, z - f * 0.18), rot=K.rot_game(rz=0.25)))   # belt


def pedals(cab, M, x, floor, z, pairs=((0.13, 0.22), (-0.13, 0.26))):
    for sx, h in pairs:
        cab.add(M.black, box(0.1, h, 0.025, (x + sx, floor + 0.18, z), r=0.01, rot=K.rot_game(rx=-0.5)))
        for k in range(4):
            cab.add(M.floor, box(0.09, 0.006, 0.01, (x + sx, floor + 0.11 + k * 0.045, z - 0.02 + k * 0.022)))
