import cv2
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles, OMR_LAYOUT_PAGE1

warped = cv2.imread("warped_debug.png")
thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
w_img, h_img = warped.shape[1], warped.shape[0]

bubbles = detect_bubbles(thresh)

col = OMR_LAYOUT_PAGE1[0]
x_min = col["roi"][0] * w_img
x_max = col["roi"][1] * w_img
y_min = col["y_start"] * h_img

# Find bubbles in Col 1 that are to the LEFT of the first expected bubble column (x~180)
# Let's look for x < 160
left_noise = [b for b in bubbles if x_min <= b["x"] < 165 and b["y"] > y_min]

print(f"Total left noise bubbles in Col 1 ROI: {len(left_noise)}")
for b in left_noise:
    print(f"  x={b['x']}, y={b['y']}, area={b['area']:.1f}, fill={b['f']:.2f}")
