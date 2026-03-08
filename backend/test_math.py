import cv2
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles

img = cv2.imread("warped_debug.png", cv2.IMREAD_COLOR)
thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
h_img, w_img = img.shape[:2]

print("w_img =", w_img)
print("h_img =", h_img)
print("0.17 * h_img =", 0.17 * h_img)
print("0.17 * w_img =", 0.17 * w_img)

bubbles = detect_bubbles(thresh)
roll_area = [
    b for b in bubbles
    if 0.04 * w_img < b["x"] < 0.34 * w_img
    and 0.17 * h_img < b["y"] < 0.72 * h_img
]
print(f"Num in roll_area: {len(roll_area)}")
for b in [b for b in roll_area if b['y'] < 350]:
    print(b)
