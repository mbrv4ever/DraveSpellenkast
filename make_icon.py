# -*- coding: utf-8 -*-
"""Maakt het icoon van DraveSpellenkast (geldige .ico via Pillow)."""
import os
from PIL import Image, ImageDraw
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(HERE, "assets"); os.makedirs(A, exist_ok=True)
S = 512
im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
d.rounded_rectangle((16, 16, S - 16, S - 16), radius=90, fill=(22, 19, 31, 255), outline=(181, 156, 255, 255), width=20)
for i in range(5):                                   # punten van het bord
    x = 70 + i * 76
    d.polygon([(x, 440), (x + 64, 440), (x + 32, 250)], fill=(127, 119, 221, 255) if i % 2 == 0 else (88, 74, 128, 255))
def steen(cx, cy, wit):
    d.ellipse((cx - 52, cy - 52, cx + 52, cy + 52), fill=(244, 240, 230, 255) if wit else (40, 32, 56, 255),
              outline=(190, 180, 160, 255) if wit else (224, 184, 90, 255), width=8)
steen(170, 390, True); steen(290, 390, False)
d.rounded_rectangle((300, 70, 450, 220), radius=28, fill=(244, 240, 230, 255), outline=(224, 184, 90, 255), width=8)
for x, y in ((335, 105), (375, 145), (415, 185)):
    d.ellipse((x - 15, y - 15, x + 15, y + 15), fill=(30, 25, 45, 255))
im.save(os.path.join(A, "icon.png"))
im.save(os.path.join(A, "icon.ico"), format="ICO", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("icoon klaar")
