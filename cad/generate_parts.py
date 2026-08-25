"""Parametric printable parts for SproutCam One v0.1.

All dimensions are millimetres. Edit the tank and printer-clearance constants,
then rerun this file. The script exports individual STL/STEP files plus an
assembled STEP reference model.
"""

from pathlib import Path
import cadquery as cq
from cadquery import exporters

ROOT = Path(__file__).resolve().parents[1]
STL = ROOT / "output" / "stl"
STEP = ROOT / "output" / "step"
STL.mkdir(parents=True, exist_ok=True)
STEP.mkdir(parents=True, exist_ok=True)

# Measure the widest outer rim of the purchased PP tank.
TANK_X = 180.0
TANK_Y = 120.0
TANK_CLEARANCE = 0.8
WALL = 3.0
LID_T = 4.0
NET_POT_HOLE = 46.0  # for nominal 50 mm net pots; measure before printing
MAST_W = 24.0
MAST_D = 18.0
LOWER_MAST_H = 170.0
UPPER_MAST_H = 190.0


def rounded_plate(x, y, z, radius=6):
    return cq.Workplane("XY").box(x, y, z).edges("|Z").fillet(radius)


def cradle():
    outer_x = TANK_X + 2 * (WALL + TANK_CLEARANCE)
    outer_y = TANK_Y + 2 * (WALL + TANK_CLEARANCE)
    base = rounded_plate(outer_x + 18, outer_y + 18, 4, 8)
    rim = (
        cq.Workplane("XY")
        .rect(outer_x, outer_y)
        .rect(TANK_X + 2 * TANK_CLEARANCE, TANK_Y + 2 * TANK_CLEARANCE)
        .extrude(18)
        .translate((0, 0, 2))
    )
    # Rear mast socket, separated from wet tank volume.
    socket = (
        cq.Workplane("XY")
        .box(MAST_W + 8, MAST_D + 8, 45)
        .translate((0, outer_y / 2 + 13, 22.5))
        .cut(
            cq.Workplane("XY")
            .box(MAST_W + 0.6, MAST_D + 0.6, 43)
            .translate((0, outer_y / 2 + 13, 24.5))
        )
    )
    return base.union(rim).union(socket)


def lid_half(left=True):
    # Two halves fit a 220 mm printer and are clamped by 4 M4 bolts.
    half_x = TANK_X / 2 + 5
    x0 = -TANK_X / 4 if left else TANK_X / 4
    plate = rounded_plate(half_x, TANK_Y + 8, LID_T, 3).translate((x0, 0, 0))
    pot_x = -TANK_X * 0.24 if left else TANK_X * 0.24
    plate = plate.cut(
        cq.Workplane("XY").circle(NET_POT_HOLE / 2).extrude(LID_T + 2).translate((pot_x, 0, -1))
    )
    # Tube notch at rear of each half.
    plate = plate.cut(
        cq.Workplane("XY").circle(4).extrude(LID_T + 2).translate((pot_x, TANK_Y / 2 - 7, -1))
    )
    # Bolt tabs bridge the centre seam.
    for y in (-38, 38):
        tab = cq.Workplane("XY").box(18, 16, LID_T).translate((0, y, 0))
        tab = tab.cut(cq.Workplane("XY").circle(2.2).extrude(LID_T + 2).translate((0, y, -1)))
        if left:
            plate = plate.union(tab)
        else:
            plate = plate.cut(cq.Workplane("XY").box(19, 17, LID_T + 1).translate((0, y, 0)))
    return plate


def mast_segment(height, lower=True):
    mast = cq.Workplane("XY").box(MAST_W, MAST_D, height)
    # Hollow cable channel, closed at front to keep splashes out.
    mast = mast.cut(
        cq.Workplane("XY").box(MAST_W - 7, MAST_D - 7, height - 12).translate((0, 1.5, 0))
    )
    if lower:
        tongue = cq.Workplane("XY").box(MAST_W - 5, MAST_D - 5, 35).translate((0, 0, height / 2 + 17.5))
        mast = mast.union(tongue)
    else:
        slot = cq.Workplane("XY").box(MAST_W - 4.4, MAST_D - 4.4, 37).translate((0, 0, -height / 2 + 18.5))
        mast = mast.cut(slot)
    # Cross holes for M4 height lock.
    for z in range(-60, 81, 20):
        if abs(z) < height / 2 - 12:
            mast = mast.cut(
                cq.Workplane("XZ").circle(2.15).extrude(MAST_D + 4).translate((0, 0, z))
            )
    return mast


def light_housing():
    body = rounded_plate(205, 52, 16, 6)
    # Bottom LED recess: accepts up to 190 x 32 x 8 mm bar.
    body = body.cut(cq.Workplane("XY").box(192, 35, 10).translate((0, 0, -5)))
    # Rear mast clamp.
    clamp = cq.Workplane("XY").box(MAST_W + 8, MAST_D + 9, 28).translate((0, 27, 2))
    clamp = clamp.cut(cq.Workplane("XY").box(MAST_W + 0.7, MAST_D + 0.7, 30).translate((0, 27, 2)))
    body = body.union(clamp)
    # Ventilation holes away from splash direction.
    for x in (-70, -35, 0, 35, 70):
        body = body.cut(cq.Workplane("XY").circle(2).extrude(20).translate((x, 19, -10)))
    return body


def camera_pod():
    outer = rounded_plate(46, 38, 24, 5)
    cavity = cq.Workplane("XY").box(35, 27, 19).translate((0, 0, 2))
    pod = outer.cut(cavity)
    pod = pod.cut(cq.Workplane("XY").circle(6.5).extrude(26).translate((0, -8, -13)))
    # USB-C access and cable exit.
    pod = pod.cut(cq.Workplane("XZ").box(12, 22, 8).translate((0, 0, -6)))
    clip = cq.Workplane("XY").box(24, 8, 18).translate((0, 22, 0))
    pod = pod.union(clip)
    return pod


def electronics_box():
    outer = rounded_plate(96, 64, 34, 5)
    inner = rounded_plate(90, 58, 31, 3).translate((0, 0, 4))
    box = outer.cut(inner)
    # Downward cable glands; holes are intentionally on the bottom.
    for x in (-28, 0, 28):
        box = box.cut(cq.Workplane("XY").circle(4).extrude(38).translate((x, 22, -19)))
    # Rear mounting holes.
    for z in (-12, 12):
        box = box.cut(cq.Workplane("XZ").circle(2.2).extrude(68).translate((0, 0, z)))
    return box


def electronics_lid():
    lid = rounded_plate(96, 64, 3, 5)
    lip = rounded_plate(89.4, 57.4, 3, 3).translate((0, 0, -2.7))
    return lid.union(lip)


PARTS = {
    "tank_cradle": cradle(),
    "lid_left": lid_half(True),
    "lid_right": lid_half(False),
    "mast_lower": mast_segment(LOWER_MAST_H, True),
    "mast_upper": mast_segment(UPPER_MAST_H, False),
    "light_housing": light_housing(),
    "camera_pod": camera_pod(),
    "electronics_box": electronics_box(),
    "electronics_lid": electronics_lid(),
}


for name, solid in PARTS.items():
    exporters.export(solid, str(STL / f"{name}.stl"), tolerance=0.08, angularTolerance=0.15)
    exporters.export(solid, str(STEP / f"{name}.step"))

# Reference assembly; not intended to print as one piece.
outer_y = TANK_Y + 2 * (WALL + TANK_CLEARANCE)
assembly = cq.Assembly(name="SproutCam One v0.1")
assembly.add(PARTS["tank_cradle"], name="cradle", color=cq.Color(0.93, 0.93, 0.90))
assembly.add(PARTS["lid_left"].translate((0, 0, 106)), name="lid_left", color=cq.Color(0.78, 0.86, 0.70))
assembly.add(PARTS["lid_right"].translate((0, 0, 106)), name="lid_right", color=cq.Color(0.78, 0.86, 0.70))
mast_y = outer_y / 2 + 13
assembly.add(PARTS["mast_lower"].translate((0, mast_y, 115)), name="mast_lower", color=cq.Color(0.25, 0.27, 0.25))
assembly.add(PARTS["mast_upper"].translate((0, mast_y, 275)), name="mast_upper", color=cq.Color(0.25, 0.27, 0.25))
assembly.add(PARTS["light_housing"].translate((0, mast_y - 56, 385)), name="light", color=cq.Color(0.93, 0.93, 0.90))
assembly.add(PARTS["camera_pod"].translate((0, mast_y - 28, 368)), name="camera", color=cq.Color(0.12, 0.13, 0.12))
assembly.add(PARTS["electronics_box"].translate((0, mast_y + 30, 245)), name="electronics", color=cq.Color(0.93, 0.93, 0.90))
assembly.save(str(STEP / "sproutcam_one_assembly.step"))

print(f"Exported {len(PARTS)} printable parts to {STL}")
