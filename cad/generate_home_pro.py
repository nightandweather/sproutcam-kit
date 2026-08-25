"""SproutCam HOME 12 / PRO 48 reference CAD and printable fixtures.

All dimensions are millimetres. The large cabinet parts are purchased aluminium
extrusion, sheet panels and waterproof trays. Only the small orange fixtures in
the concept drawing are intended for FDM printing.
"""

from pathlib import Path
import shutil
import tempfile
import cadquery as cq
from cadquery import exporters

ROOT = Path(__file__).resolve().parents[1]
STL = ROOT / "output" / "stl" / "home-pro"
STEP = ROOT / "output" / "step" / "home-pro"
STL.mkdir(parents=True, exist_ok=True)
STEP.mkdir(parents=True, exist_ok=True)


def rounded_box(x, y, z, radius=2.0):
    return cq.Workplane("XY").box(x, y, z).edges("|Z").fillet(radius)


def extrusion_clip(profile=20, rail=18):
    """Snap-over U clip with an M4 clearance hole for an LED rail."""
    wall = 3.0
    outer = cq.Workplane("XY").box(profile + 2 * wall, 24, 16)
    cavity = (
        cq.Workplane("XY")
        .box(profile + 0.7, 18, 14)
        .translate((0, -3, 2))
    )
    clip = outer.cut(cavity)
    saddle = (
        cq.Workplane("XY")
        .box(rail + 8, 24, 6)
        .translate((0, 0, 11))
        .cut(cq.Workplane("XY").box(rail + 0.6, 18, 5).translate((0, -3, 11)))
    )
    clip = clip.union(saddle)
    return clip.cut(cq.Workplane("XY").circle(2.2).extrude(30).translate((0, 0, -15)))


def camera_bracket(profile=20):
    """30 degree camera shelf for XIAO ESP32-S3 Sense in a small enclosure."""
    clamp = rounded_box(profile + 8, 26, 18, 2)
    clamp = clamp.cut(
        cq.Workplane("XY").box(profile + 0.8, 20, 16).translate((0, -3, 2))
    )
    arm = cq.Workplane("XY").box(34, 52, 5).translate((0, -30, 5))
    arm = arm.rotate((0, 0, 0), (1, 0, 0), -30)
    for x in (-11, 11):
        arm = arm.cut(
            cq.Workplane("XY")
            .circle(1.7)
            .extrude(12)
            .translate((x, -34, -2))
            .rotate((0, 0, 0), (1, 0, 0), -30)
        )
    return clamp.union(arm)


def sensor_guard():
    """Vented splash guard for a 20 x 16 mm SHT40 breakout board."""
    outer = rounded_box(34, 29, 18, 4)
    inner = rounded_box(28, 23, 15, 3).translate((0, 0, 3))
    guard = outer.cut(inner)
    for x in (-10, -5, 0, 5, 10):
        guard = guard.cut(
            cq.Workplane("XZ").box(2.2, 32, 8).translate((x, 0, 2))
        )
    return guard.cut(cq.Workplane("XY").circle(2.2).extrude(22).translate((0, 10, -11)))


def cable_clip(profile=20):
    """Snap clip for one 6 mm cable bundle on 2020 or 3030 extrusion."""
    wall = 2.8
    clip = cq.Workplane("XY").box(profile + 2 * wall, 15, 13)
    clip = clip.cut(
        cq.Workplane("XY").box(profile + 0.8, 11, 11).translate((0, -2, 2))
    )
    loop = (
        cq.Workplane("YZ")
        .circle(5.2)
        .circle(3.2)
        .extrude(6)
        .translate((profile / 2 + 3, 0, 0))
    )
    return clip.union(loop)


def tray_corner(profile=20):
    """Corner stop that keeps the removable wet tray 4 mm off the frame."""
    base = cq.Workplane("XY").box(38, 38, 5)
    walls = (
        cq.Workplane("XY").box(38, 5, 24).translate((0, 16.5, 9.5))
        .union(cq.Workplane("XY").box(5, 38, 24).translate((16.5, 0, 9.5)))
    )
    foot = cq.Workplane("XY").box(profile + 0.8, profile + 0.8, 5).translate((-6, -6, -5))
    return base.union(walls).union(foot)


PARTS = {
    "led_clip_2020": extrusion_clip(20, 18),
    "led_clip_3030": extrusion_clip(30, 24),
    "camera_bracket_2020_30deg": camera_bracket(20),
    "camera_bracket_3030_30deg": camera_bracket(30),
    "sht40_sensor_guard": sensor_guard(),
    "cable_clip_2020": cable_clip(20),
    "cable_clip_3030": cable_clip(30),
    "tray_corner_2020": tray_corner(20),
    "tray_corner_3030": tray_corner(30),
}

for name, solid in PARTS.items():
    exporters.export(solid, str(STL / f"{name}.stl"), tolerance=0.08, angularTolerance=0.15)
    exporters.export(solid, str(STEP / f"{name}.step"))


def add_frame(assembly, width, depth, height, profile, shelf_zs, name_prefix):
    frame_color = cq.Color(0.30, 0.32, 0.33)
    for i, x in enumerate((-width / 2 + profile / 2, width / 2 - profile / 2)):
        for j, y in enumerate((-depth / 2 + profile / 2, depth / 2 - profile / 2)):
            post = cq.Workplane("XY").box(profile, profile, height)
            assembly.add(post.translate((x, y, height / 2)), name=f"{name_prefix}_post_{i}_{j}", color=frame_color)
    for level, z in enumerate([profile / 2, height - profile / 2] + shelf_zs):
        for side, y in enumerate((-depth / 2 + profile / 2, depth / 2 - profile / 2)):
            beam = cq.Workplane("XY").box(width - 2 * profile, profile, profile)
            assembly.add(beam.translate((0, y, z)), name=f"{name_prefix}_w_{level}_{side}", color=frame_color)
        for side, x in enumerate((-width / 2 + profile / 2, width / 2 - profile / 2)):
            beam = cq.Workplane("XY").box(profile, depth - 2 * profile, profile)
            assembly.add(beam.translate((x, 0, z)), name=f"{name_prefix}_d_{level}_{side}", color=frame_color)


def add_pots(assembly, cols, rows, pitch_x, pitch_y, z, prefix):
    pot_color = cq.Color(0.86, 0.55, 0.26)
    plant_color = cq.Color(0.25, 0.60, 0.28)
    for row in range(rows):
        for col in range(cols):
            x = (col - (cols - 1) / 2) * pitch_x
            y = (row - (rows - 1) / 2) * pitch_y
            pot = cq.Workplane("XY").circle(36).circle(29).extrude(70)
            crown = cq.Workplane("XY").sphere(25).translate((x, y, z + 92))
            assembly.add(pot.translate((x, y, z)), name=f"{prefix}_pot_{row}_{col}", color=pot_color)
            assembly.add(crown, name=f"{prefix}_plant_{row}_{col}", color=plant_color)


# HOME 12 reference assembly: 560 W x 400 D x 600 H.
home = cq.Assembly(name="SproutCam HOME 12 v0.1")
add_frame(home, 560, 400, 600, 20, [130, 540], "home")
home.add(cq.Workplane("XY").box(520, 340, 35).translate((0, 0, 148)), name="home_wet_tray", color=cq.Color(0.87, 0.91, 0.91))
home.add(cq.Workplane("XY").box(520, 320, 16).translate((0, 0, 520)), name="home_led", color=cq.Color(0.95, 0.72, 0.10))
home.add(cq.Workplane("XY").box(220, 330, 90).translate((0, 0, 65)), name="home_service_drawer", color=cq.Color(0.78, 0.80, 0.79))
add_pots(home, 4, 3, 105, 95, 165, "home")
with tempfile.TemporaryDirectory(prefix="sproutcam-step-") as temp_dir:
    temp_path = Path(temp_dir) / "sproutcam_home12_reference.step"
    home.save(str(temp_path))
    shutil.copyfile(temp_path, STEP / temp_path.name)

# PRO 48 reference assembly: 680 W x 560 D x 1700 H, two independent zones.
pro = cq.Assembly(name="SproutCam PRO 48 v0.1")
add_frame(pro, 680, 560, 1700, 30, [280, 930, 1610], "pro")
for zone, base_z in enumerate((300, 950)):
    pro.add(cq.Workplane("XY").box(610, 470, 40).translate((0, 0, base_z + 20)), name=f"pro_tray_{zone}", color=cq.Color(0.87, 0.91, 0.91))
    pro.add(cq.Workplane("XY").box(600, 420, 18).translate((0, 0, base_z + 570)), name=f"pro_led_{zone}", color=cq.Color(0.95, 0.72, 0.10))
    add_pots(pro, 6, 4, 92, 100, base_z + 42, f"pro_z{zone}")
pro.add(cq.Workplane("XY").box(580, 450, 220).translate((0, 0, 140)), name="pro_service_bay", color=cq.Color(0.78, 0.80, 0.79))
with tempfile.TemporaryDirectory(prefix="sproutcam-step-") as temp_dir:
    temp_path = Path(temp_dir) / "sproutcam_pro48_reference.step"
    pro.save(str(temp_path))
    shutil.copyfile(temp_path, STEP / temp_path.name)

print(f"Exported {len(PARTS)} printable fixtures and 2 reference assemblies")
