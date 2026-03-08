import cv2
import sys
import os

# Ensure backend module can be imported
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles

thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
warped = cv2.imread("warped_debug.png", cv2.IMREAD_COLOR)

if thresh is None or warped is None:
    print("Could not load debug images.")
    exit()

h_img, w_img = warped.shape[:2]

bubbles = detect_bubbles(thresh)
print(f"Detected {len(bubbles)} bubbles.")

roll_area = [
    b for b in bubbles
    if 0.04 * w_img < b["x"] < 0.34 * w_img
    and 0.17 * h_img < b["y"] < 0.72 * h_img
]

set_area = [
    b for b in bubbles
    if 0.04 * w_img < b["x"] < 0.30 * w_img
    and 0.01 * h_img < b["y"] < 0.17 * h_img
]

print(f"Total in roll_area: {len(roll_area)}")
roll_area = sorted(roll_area, key=lambda b: b["x"])
x_tol    = w_img * 0.025
columns = []
if roll_area:
    current  = [roll_area[0]]
    for b in roll_area[1:]:
        if abs(b["x"] - current[0]["x"]) < x_tol:
            current.append(b)
        else:
            columns.append(current)
            current = [b]
    columns.append(current)

for i, col in enumerate(columns):
    col = sorted(col, key=lambda b: b["y"])
    print(f"Roll Col {i} has {len(col)} bubbles:")
    for b in col[:10]:
        print(f"  x={b['x']:.1f}, y={b['y']:.1f}, f={b['f']:.2f}, r={b['r']:.1f}")

print(f"\nTotal in set_area: {len(set_area)}")
set_area = sorted(set_area, key=lambda b: b["x"])
for i, b in enumerate(set_area):
    print(f"Set b {i}: x={b['x']:.1f}, y={b['y']:.1f}, f={b['f']:.2f}, r={b['r']:.1f}")
