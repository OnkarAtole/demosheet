import sys
import os
import cv2
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles, OMR_LAYOUT_PAGE1, _group_into_rows

warped = cv2.imread("warped_debug.png", cv2.IMREAD_COLOR)
thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)

bubbles = detect_bubbles(thresh)
w_img = warped.shape[1]
h_img = warped.shape[0]

# check col 1 again
col = OMR_LAYOUT_PAGE1[0]
x_min = col["roi"][0] * w_img
x_max = col["roi"][1] * w_img
y_min = col["y_start"] * h_img

col_bubbles = [
    b for b in bubbles
    if x_min <= b["x"] <= x_max and b["y"] > y_min
]
col_bubbles.sort(key=lambda b: b['y'])

print(f"Total bubbles in Col 1: {len(col_bubbles)}")
rows = _group_into_rows(col_bubbles)

for i, r in enumerate(rows):
    y_center = np.mean([b['y'] for b in r])
    sys.stdout.write(f"V[{i}] Y={y_center:.0f} (len={len(r)}) -> ")
    for b in r:
        sys.stdout.write(f"[{b['x']:.0f}:{b['f']:.2f}] ")
    print()
