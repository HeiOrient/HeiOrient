#!/usr/bin/env python3
"""Generate the GitHub social preview image (1280x640) for HeiOrient."""

from PIL import Image, ImageDraw, ImageFont
import math
import os

W, H = 1280, 640
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "social-preview.png")

canvas = Image.new("RGB", (W, H), (26, 31, 58))
draw = ImageDraw.Draw(canvas)

# Gradient background
cx, cy = W // 2, H // 2
for r in range(500, 0, -2):
    frac = r / 500
    c1 = int(26 + (15 - 26) * (1 - frac))
    c2 = int(31 + (19 - 31) * (1 - frac))
    c3 = int(58 + (40 - 58) * (1 - frac))
    draw.ellipse([cx - r * 1.6, cy - r, cx + r * 1.6, cy + r], fill=(c1, c2, c3))

bg = (26, 31, 58)
node_fill = (30, 41, 59)  # #1e293b

# Colors matching DynDeltaOrientation style
green = (74, 222, 128)      # #4ade80 - low out-degree arrows
orange = (245, 158, 11)     # #f59e0b - high out-degree arrows
blue_stroke = (96, 165, 250)  # #60a5fa - low out-degree node stroke
text_light = (226, 232, 240)

# Graph: planar layout, 3 rows
#   A(80,100)    B(220,100)    C(360,100)    D(500,100)
#      E(150,260)    F(290,260)    G(430,260)
#   H(80,420)    I(220,420)    J(360,420)    K(500,420)
#                   L(290,540)

nodes = [
    (80, 100),   # 0: A
    (220, 100),  # 1: B
    (360, 100),  # 2: C
    (500, 100),  # 3: D
    (150, 260),  # 4: E
    (290, 260),  # 5: F
    (430, 260),  # 6: G
    (80, 420),   # 7: H
    (220, 420),  # 8: I
    (360, 420),  # 9: J
    (500, 420),  # 10: K
    (290, 540),  # 11: L
]

# Directed edges (from, to)
# High out-degree nodes: B(1) out=3, F(5) out=3 -> orange
# Others: low out-degree -> green
directed_edges = [
    (0, 1),   # A->B  green
    (1, 2),   # B->C  orange (B out=3)
    (2, 3),   # C->D  green
    (0, 4),   # A->E  green
    (1, 4),   # B->E  orange
    (1, 5),   # B->F  orange
    (3, 6),   # D->G  green
    (2, 5),   # C->F  green
    (4, 7),   # E->H  green
    (5, 4),   # F->E  orange (F out=3)
    (5, 8),   # F->I  orange
    (5, 9),   # F->J  orange
    (6, 10),  # G->K  green
    (6, 9),   # G->J  green
    (7, 8),   # H->I  green
    (8, 11),  # I->L  green
    (9, 11),  # J->L  green
    (10, 9),  # K->J  green
]

# Compute out-degrees
out_deg = {i: 0 for i in range(len(nodes))}
for i, j in directed_edges:
    out_deg[i] += 1

# High out-degree threshold
max_out = max(out_deg.values())
high_out_nodes = {i for i, d in out_deg.items() if d == max_out}


def draw_arrow(x1, y1, x2, y2, color, width=2, head_size=12, shorten=14):
    """Draw a line with arrowhead, shortened to not overlap nodes."""
    angle = math.atan2(y2 - y1, x2 - x1)
    x1s = x1 + shorten * math.cos(angle)
    y1s = y1 + shorten * math.sin(angle)
    x2s = x2 - shorten * math.cos(angle)
    y2s = y2 - shorten * math.sin(angle)

    draw.line([(x1s, y1s), (x2s, y2s)], fill=color, width=width)

    for da in [-0.4, 0.4]:
        ax = x2s - head_size * math.cos(angle + da)
        ay = y2s - head_size * math.sin(angle + da)
        draw.line([(x2s, y2s), (ax, ay)], fill=color, width=width)


# Draw nodes first (so arrows render on top)
node_r = 12
for idx, (x, y) in enumerate(nodes):
    # Glow
    glow_color = orange if idx in high_out_nodes else blue_stroke
    for r in range(22, node_r, -1):
        af = 1 - (r - node_r) / 10
        gc = tuple(int(glow_color[k] * 0.08 * af + (1 - 0.08 * af) * bg[k]) for k in range(3))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=gc)

    stroke_c = orange if idx in high_out_nodes else blue_stroke
    stroke_w = 3 if idx in high_out_nodes else 2
    draw.ellipse([x - node_r, y - node_r, x + node_r, y + node_r],
                 fill=node_fill, outline=stroke_c, width=stroke_w)

# Draw arrows on top of nodes, shortened so heads sit outside node circles
for i, j in directed_edges:
    x1, y1 = nodes[i]
    x2, y2 = nodes[j]
    if i in high_out_nodes:
        draw_arrow(x1, y1, x2, y2, orange, width=2, head_size=11, shorten=node_r + 4)
    else:
        draw_arrow(x1, y1, x2, y2, green, width=2, head_size=11, shorten=node_r + 4)

# Fonts
try:
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 72)
    font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 26)
    font_tag = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
    font_legend = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
except OSError:
    font_title = font_sub = font_tag = font_legend = ImageFont.load_default()

text_x = 660

# Title
draw.text((text_x, 150), "Hei", fill=blue_stroke, font=font_title)
hei_bbox = draw.textbbox((text_x, 150), "Hei", font=font_title)
draw.text((hei_bbox[2], 150), "Orient", fill=text_light, font=font_title)

# Separator
draw.line([(text_x, 245), (text_x + 520, 245)], fill=(60, 80, 110), width=2)

# Subtitle
draw.text((text_x, 268), "Engineering Edge", fill=(148, 163, 184), font=font_sub)
draw.text((text_x, 304), "Orientation Algorithms", fill=(148, 163, 184), font=font_sub)

# Tagline
draw.text((text_x, 370), "Orient undirected edges to minimize", fill=(110, 130, 160), font=font_tag)
draw.text((text_x, 400), "the maximum out-degree", fill=(110, 130, 160), font=font_tag)

# Legend
legend_y = 490
draw_arrow(text_x, legend_y, text_x + 40, legend_y, green, width=2, head_size=8, shorten=0)
draw.text((text_x + 50, legend_y - 10), "Low out-degree", fill=(148, 163, 184), font=font_legend)

draw_arrow(text_x + 260, legend_y, text_x + 300, legend_y, orange, width=2, head_size=8, shorten=0)
draw.text((text_x + 310, legend_y - 10), "High out-degree", fill=(148, 163, 184), font=font_legend)

canvas.save(OUT_PATH, "PNG", quality=95)
print(f"Saved {OUT_PATH}")
