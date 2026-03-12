import cv2
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles, OMR_LAYOUT_PAGE1, _group_into_rows

thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
w_img, h_img = 1237, 1778

bubbles = detect_bubbles(thresh)

results = {}
for col in OMR_LAYOUT_PAGE1:
    x_min = col["roi"][0] * w_img
    x_max = col["roi"][1] * w_img
    y_min = col["y_start"] * h_img

    col_bubbles = [
        b for b in bubbles
        if x_min <= b["x"] <= x_max and b["y"] > y_min
    ]

    rows = _group_into_rows(col_bubbles)
    if not rows: continue
    
    rows = sorted(rows, key=lambda r: float(np.mean([b["y"] for b in r])))
    
    if len(rows) > 1:
        y_centers = [float(np.mean([b["y"] for b in r])) for r in rows]
        gaps = [y_centers[i] - y_centers[i-1] for i in range(1, len(y_centers))]
        valid_gaps = [g for g in gaps if 15 < g < 60]
        if valid_gaps:
            median_gap = float(np.median(valid_gaps))
        else:
            median_gap = max(15.0, float(np.median(gaps)))
            
        print(f"Col {col['start']}: median gap: {median_gap:.2f}")
        
        padded_rows = []
        expected_y = y_centers[0]
        
        for r, y_c in zip(rows, y_centers):
            steps = int(round((y_c - expected_y) / median_gap))
            if steps > 0:
                for _ in range(steps):
                    padded_rows.append([])
                    expected_y += median_gap
            padded_rows.append(r)
            expected_y += median_gap
            
        print(f"  Padded rows count: {len(padded_rows)} (Old: {len(rows)})")
        rows = padded_rows
        
    rows = rows[: col["count"]]
    print(f"  Final rows count for col: {len(rows)}")
