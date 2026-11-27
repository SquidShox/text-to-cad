"""iPhone SE (2020) mini-PC console: tower body, fan shroud backplate + base, reference assembly.

Build frame P (Part 1, tower): +Z points from the screen face into the rear, so printing Part 1 with its
screen face on the bed is Z-up as modelled. +Y is tower-up, and P is right-handed, so X is mirrored
against the viewer: the phone's right side (power button) is -X here.
Tower Y: bay bottom = 0, tower bottom = -3.05, tower top = 141.95. Tower Z (mm from the screen face):
lip 0-1.5, bay 1.5-9.3, Qi barrier 9.3-10.9, charger pocket 10.9-18.2, plenum 18.2-26.2, backplate 26.2-30.2.
"""
import math

import build123d as bd
from cad import model

TILT = 12.0
CY = 69.45  # bay mid-height, also the charger and fan centre
W, H = 126.0, 145.0
Y_BOT, Y_TOP = -3.05, 141.95
Z_LIP, Z_BAY, Z_BARRIER, Z_POCKET, Z_PLENUM, Z_BACK = 1.5, 9.3, 10.9, 18.2, 26.2, 30.2
BOSS_XY = [(sx * 56.0, y) for sx in (-1, 1) for y in (4.0, 135.0)]
BASE_TOP = -17.3  # world height of the base's top face, relative to the tower's front-bottom edge
BASE_T = 5.0
LIFT = -(BASE_TOP - BASE_T)  # puts the base's underside on the bed


def box(x0, x1, y0, y1, z0, z1):
    return bd.Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * bd.Box(x1 - x0, y1 - y0, z1 - z0)


def cylz(r, x, y, z0, z1):
    return bd.Pos(x, y, (z0 + z1) / 2) * bd.Cylinder(r, z1 - z0)


def prism(w, h, r, cx, cy, z0, z1):
    return bd.Pos(0, 0, z0) * bd.extrude(bd.Pos(cx, cy) * bd.RectangleRounded(w, h, r), amount=z1 - z0)


def tilt_location():
    s, c = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
    return bd.Location(bd.Plane(origin=(0, 0, 0), x_dir=(-1, 0, 0), z_dir=(0, c, -s)))


def to_world(shape):
    return bd.Pos(0, 0, LIFT) * (tilt_location() * shape)


def part1_body():
    body = prism(W, H, 5, 0, CY, 0, Z_PLENUM) - prism(120, 139, 2, 0, CY, Z_POCKET, Z_PLENUM + 0.1)
    for x, y in BOSS_XY:
        body += cylz(5, x, y, Z_POCKET - 0.1, Z_PLENUM)

    # Phone bay (open at the top so the phone slides in under the screen lip)
    body -= prism(67.8, 138.9, 10.5, 0, CY, Z_LIP, Z_BAY)
    body -= box(-33.9, 33.9, 128.4, Y_TOP + 1, Z_LIP, Z_BAY)
    # Screen window 106 x 60, Touch ID hole d12.5 centred 9.5 above the bay bottom
    body -= box(-30, 30, CY - 52.9, CY + 53.1, -0.1, Z_LIP + 0.1)  # +0.1 mm: keeps the web above the Touch ID hole at 0.8 mm
    body -= cylz(6.25, 0, 9.5, -0.1, Z_LIP + 0.1)
    # Bottom intake 35 x 5 through the bottom wall
    body -= box(-17.5, 17.5, Y_BOT - 1, 0.01, Z_BAY - 5.0, Z_BAY)
    # Side buttons: power on the phone's right (-X here), 32 mm from the top edge; volume 30-52 mm
    body -= box(-W / 2 - 1, -33.0, 138.9 - 32 - 7, 138.9 - 32 + 7, 2.9, 7.9)
    body -= box(33.0, W / 2 + 1, 138.9 - 52, 138.9 - 30, 2.9, 7.9)

    # Qi pocket, 1.6 mm barrier left in front of it, and its cable channel (5 wide x 4.5 deep)
    body -= cylz(50.3, 0, CY, Z_BARRIER, Z_POCKET + 0.1)
    body -= box(-2.5, 2.5, Y_BOT - 1, 20.0, Z_POCKET - 4.5, Z_POCKET + 0.1)
    # Vents outside the charger circle, bay to plenum
    for sx in (-1, 1):
        for y0, y1 in ((3, 14), (125, 136)):
            x0, x1 = sorted((sx * 7, sx * 27))
            body -= box(x0, x1, y0, y1, Z_BAY - 0.01, Z_POCKET + 0.1)
    # Side and bottom intake louvers in the plenum rim
    for i in range(12):
        yc = CY + (i - 5.5) * 9
        for sx in (-1, 1):
            x0, x1 = sorted((sx * 59, sx * 64))
            body -= box(x0, x1, yc - 1.75, yc + 1.75, 19.7, 24.7)
    for i in range(11):
        xc = (i - 5) * 9
        body -= box(xc - 1.75, xc + 1.75, Y_BOT - 1, 0.0, 19.7, 24.7)
    # M3 self-tapping pilot holes
    for x, y in BOSS_XY:
        body -= cylz(1.4, x, y, Z_PLENUM - 12, Z_PLENUM + 0.1)
    return body


def part2_plate():
    plate = prism(W, H, 5, 0, CY, Z_PLENUM, Z_BACK) + box(-63, 63, -15.5, Y_BOT + 0.5, Z_PLENUM, Z_BACK)
    slots = [(53.5, 57), (48, 51.5), (42.5, 46), (37, 40.5), (31.5, 35), (26, 29.5), (20.5, 24)]
    cut = None
    for ri, ro in slots:
        ring = cylz(ro, 0, CY, Z_PLENUM - 0.1, Z_BACK + 0.1) - cylz(ri, 0, CY, Z_PLENUM - 0.1, Z_BACK + 0.1)
        cut = ring if cut is None else cut + ring
    for a in (45, -45):
        cut -= bd.Pos(0, CY, 0) * bd.Rot(0, 0, a) * box(-60, 60, -2, 2, Z_PLENUM - 1, Z_BACK + 1)
    plate -= cut
    # Posts that hold the charger against its barrier (tips 0.1 mm off the charger's back)
    r = 41.5 / math.sqrt(2)
    for sx in (-1, 1):
        for sy in (-1, 1):
            plate += cylz(3, sx * r, CY + sy * r, 18.0, Z_PLENUM + 0.3)
    # ATX 120 fan screws, 105 x 105, d4.5; M3 clearance for the four corner screws
    for sx in (-1, 1):
        for sy in (-1, 1):
            plate -= cylz(2.25, sx * 52.5, CY + sy * 52.5, Z_PLENUM - 0.1, Z_BACK + 0.1)
    for x, y in BOSS_XY:
        plate -= cylz(1.7, x, y, Z_PLENUM - 0.1, Z_BACK + 0.1)
    # Cable exit: a 45-degree-roofed port in the skirt
    notch = bd.Pos(0, 0, Z_PLENUM - 1) * bd.extrude(
        bd.Polygon((-5, -16), (5, -16), (5, -9), (0, -4), (-5, -9), align=None), amount=6
    )
    return plate - notch


def part2_body():
    s, c = math.sin(math.radians(TILT)), math.cos(math.radians(TILT))
    shell = to_world(part2_plate())
    # World frame (X right, Y rear). Tower footprint spans Y -0.6 .. 80.9; the base is 130 x 85.
    base = bd.Pos(0, 40.1, BASE_TOP - BASE_T / 2 + LIFT) * bd.extrude(bd.RectangleRounded(130, 85, 6), amount=BASE_T)
    base = bd.Pos(0, 0, -BASE_T / 2) * base
    body = shell + base
    # Gussets from the base up the backplate, front (under the tower) and rear
    zb = BASE_TOP + LIFT
    y_face = Z_PLENUM * c + ((BASE_TOP + Z_PLENUM * s) / c) * s
    for x in (-45, 45):
        for pts in (
            [(y_face + 1, zb), (y_face - 23, zb), (y_face + 2.5, zb + 9)],
            [(y_face + 5, zb), (y_face + 33, zb), (y_face + 5, zb + 9)],
        ):
            g = bd.Pos(x, 0, 0) * bd.Rot(0, 90, 0) * bd.extrude(
                bd.Polygon(*[(-z, y) for y, z in pts], align=None), amount=3, both=True
            )
            body += g
    return body


def part1_print():
    return part1_body()


@model
def part1_tower_body():
    p = part1_body()
    p.label = "part1_tower_body"
    p.color = "#2f3a4a"
    return p


@model
def part2_fan_shroud_base():
    p = part2_body()
    p.label = "part2_fan_shroud_base"
    p.color = "#4a6fa5"
    return p


@model
def console_assembly():
    p1 = to_world(part1_body())
    p1.label = "part1_tower_body"
    p1.color = "#2f3a4a"
    p2 = part2_body()
    p2.label = "part2_fan_shroud_base"
    p2.color = "#4a6fa5"

    phone = prism(67.3, 138.4, 10.25, 0, CY, 2.0, 9.3)
    phone.label = "ref_iphone_se_2020"
    phone.color = "#d8d8d8"
    charger = cylz(50.0, 0, CY, Z_BARRIER, Z_BARRIER + 7.0)
    charger.label = "ref_qi_charger_100x7"
    charger.color = "#222222"
    fan = box(-60, 60, CY - 60, CY + 60, Z_BACK, Z_BACK + 25) - cylz(57, 0, CY, Z_BACK - 1, Z_BACK + 26)
    fan += cylz(20, 0, CY, Z_BACK, Z_BACK + 25)
    fan.label = "ref_fan_120x120x25"
    fan.color = "#555555"
    refs = [to_world(x) for x in (phone, charger, fan)]
    for r, src in zip(refs, (phone, charger, fan)):
        r.label, r.color = src.label, src.color
    return bd.Compound(label="console", children=[p1, p2, *refs])


if __name__ == "__main__":
    part1_tower_body()
    part2_fan_shroud_base()
    console_assembly()
