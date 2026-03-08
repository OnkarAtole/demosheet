import cv2
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles, OMR_LAYOUT_PAGE1, _group_into_rows

warped = cv2.imread("warped_debug.png")
thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
w_img, h_img = warped.shape[1], warped.shape[0]

# CRITICAL: Detect bubbles
bubbles = detect_bubbles(thresh)

col = OMR_LAYOUT_PAGE1[0]
x_min = col["roi"][0] * w_img
x_max = col["roi"][1] * w_img

# Get ALL bubbles in the horizontal ROI of Column 1
col_bubbles = [b for b in bubbles if x_min <= b["x"] <= x_max]
rows = _group_into_rows(col_bubbles)

print(f"Total rows in Col 1 X-range: {len(rows)}")
for i, r in enumerate(rows):
    yc = np.mean([b['y'] for b in r])
    fills = ",".join(str(round(b["f"], 2)) for b in sorted(r, key=lambda b: b['x']))
    print(f"  Row {i:2}: y={yc:4.0f} ({yc/h_img:.3f} height), len={len(r)}, fills=[{fills}]")
