import cv2
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles, _group_into_rows, OMR_LAYOUT_PAGE1

thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
w_img, h_img = 1237, 1778  # typically the size of the generated one

bubbles = detect_bubbles(thresh)
for col in OMR_LAYOUT_PAGE1:
    x_min = col["roi"][0] * w_img
    x_max = col["roi"][1] * w_img
    y_min = col["y_start"] * h_img

    col_bubbles = [b for b in bubbles if x_min <= b["x"] <= x_max and b["y"] > y_min]
    rows = _group_into_rows(col_bubbles)
    
    if len(rows) > 0:
        for r in rows:
            print(f"Row y={r[0]['y']} -> num bubbles: {len(r)}")
            for b in sorted(r, key=lambda b: b['x']):
                print(f"  x={b['x']:.1f}, f={b['f']:.2f}")
    break # Just first column
