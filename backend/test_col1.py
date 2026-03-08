import sys
import os
import cv2

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles, OMR_LAYOUT_PAGE1

warped = cv2.imread("warped_debug.png", cv2.IMREAD_COLOR)
thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)

bubbles = detect_bubbles(thresh)
w_img = warped.shape[1]
h_img = warped.shape[0]

# Print bubble Y values for the 1st column
col = OMR_LAYOUT_PAGE1[0]
x_min = col["roi"][0] * w_img
x_max = col["roi"][1] * w_img
y_min = col["y_start"] * h_img

print(f"Col 1 bounds: x({x_min:.0f}-{x_max:.0f}), y(> {y_min:.0f})")

col_bubbles = [
    b for b in bubbles
    if x_min <= b["x"] <= x_max
]

print(f"Bubbles in Col 1 X bounds: {len(col_bubbles)}")

# Let's see the first few y's
col_bubbles.sort(key=lambda b: b['y'])
print("Top Bubbles in Col 1 X bound:")
for b in col_bubbles[:30]:
    print(f"  y={b['y']} (above y_min? {b['y'] > y_min})")

# Let's adjust y_start based on the roll number section end
roll_bubbles = [
    b for b in bubbles
    if 0.04 * w_img < b["x"] < 0.34 * w_img
    and 0.20 * h_img < b["y"] < 0.72 * h_img
]
roll_bottom = max(b['y'] for b in roll_bubbles) if roll_bubbles else 0
print(f"Bottom of roll bubbles: {roll_bottom}")
print(f"Roll bottom as fraction: {roll_bottom / h_img:.3f}")

# Look for the first question bubble under roll
q_bubbles = [b for b in col_bubbles if b['y'] > roll_bottom + 10]
if q_bubbles:
    first_q_y = min(b['y'] for b in q_bubbles)
    print(f"First question bubble y: {first_q_y}")
    print(f"Suggested y_start fraction: {(first_q_y - 10) / h_img:.3f}")
