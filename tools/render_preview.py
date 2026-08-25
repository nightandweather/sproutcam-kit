"""Render a lightweight isometric preview from the exported assembly STEP."""
from pathlib import Path
import math
import cadquery as cq
from cadquery import importers
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
shape = importers.importStep(str(ROOT / "output/step/sproutcam_one_assembly.step")).val()
verts, tris = shape.tessellate(1.2)

ca, sa = math.cos(math.radians(35)), math.sin(math.radians(35))
cb, sb = math.cos(math.radians(28)), math.sin(math.radians(28))

def project(v):
    x, y, z = v.x, v.y, v.z
    xr, yr = x * ca - y * sa, x * sa + y * ca
    return xr, z * cb - yr * sb, yr * cb + z * sb

pv = [project(v) for v in verts]
minx, maxx = min(v[0] for v in pv), max(v[0] for v in pv)
miny, maxy = min(v[1] for v in pv), max(v[1] for v in pv)
W, H, M = 1400, 1400, 110
scale = min((W-2*M)/(maxx-minx), (H-2*M)/(maxy-miny))

def screen(p):
    return (M+(p[0]-minx)*scale, H-M-(p[1]-miny)*scale)

img = Image.new("RGB", (W,H), "#f4f1e8")
draw = ImageDraw.Draw(img)
faces=[]
for t in tris:
    p=[pv[t[0]],pv[t[1]],pv[t[2]]]
    depth=sum(x[2] for x in p)/3
    a,b,c=[verts[i] for i in t]
    ux,uy,uz=b.x-a.x,b.y-a.y,b.z-a.z
    vx,vy,vz=c.x-a.x,c.y-a.y,c.z-a.z
    nz=ux*vy-uy*vx
    shade=max(105,min(225,int(175+nz/120)))
    faces.append((depth,[screen(x) for x in p],shade))
for _,pts,shade in sorted(faces,key=lambda x:x[0]):
    draw.polygon(pts,fill=(shade,shade,min(235,shade+8)),outline=(44,44,40))

draw.text((55,45),"SPROUTCAM ONE / CAD PREVIEW v0.1",fill="#111111",stroke_width=0)
out=ROOT/"output/preview/sproutcam-one-isometric.png"
out.parent.mkdir(parents=True,exist_ok=True)
img.save(out)
print(out)

