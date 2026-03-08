import cv2
import sys
import os
import numpy as np
import math

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles, OMR_LAYOUT_PAGE1

warped = cv2.imread("warped_debug.png")
thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
w_img, h_img = warped.shape[1], warped.shape[0]

bubbles = detect_bubbles(thresh)

if not bubbles:
    print("No bubbles found.")
    exit()

print(f"Total bubbles: {len(bubbles)}")
areas = [b["area"] for b in bubbles]
print(f"Median Area: {np.median(areas)}")
print(f"Min Area: {min(areas)}")
print(f"Max Area: {max(areas)}")

# Sort by area and show top/bottom 10
sorted_by_area = sorted(bubbles, key=lambda b: b["area"])

print("\nSmallest 10 bubbles:")
for b in sorted_by_area[:10]:
    print(f"  x={b['x']}, y={b['y']}, area={b['area']:.1f}, circ={(b['area'] * 4 * math.pi) / (b['h'] * b['h'] * 4):.2f}") # Approx circ

print("\nLargest 10 bubbles:")
for b in sorted_by_area[-10:]:
    print(f"  x={b['x']}, y={b['y']}, area={b['area']:.1f}")
