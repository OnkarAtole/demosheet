import cv2
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles, OMR_LAYOUT_PAGE1, _group_into_rows

warped = cv2.imread("warped_debug.png")
thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
w_img, h_img = warped.shape[1], warped.shape[0]

bubbles = detect_bubbles(thresh)

for i, col in enumerate(OMR_LAYOUT_PAGE1):
    x_min = col["roi"][0] * w_img
    x_max = col["roi"][1] * w_img
    col_bubbles = [b for b in bubbles if x_min <= b["x"] <= x_max]
    rows = _group_into_rows(col_bubbles)
    
    if rows:
        # Pick a middle row to check sample X coordinates
        mid_row = sorted(rows[len(rows)//2], key=lambda b: b['x'])
        xs = [round(b['x']) for b in mid_row]
        fracs = [round((x - x_min)/(x_max - x_min), 3) for x in xs]
        print(f"Col {i+1} (starts Q{col['start']}): ROI({col['roi']}) -> Width {x_max-x_min:.1f}px")
        print(f"  Sample Xs: {xs}")
        print(f"  Sample Fractions within ROI: {fracs}")
