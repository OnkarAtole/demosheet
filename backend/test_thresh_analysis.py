import cv2
import numpy as np
import math

thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
warped = cv2.imread("warped_debug.png", cv2.IMREAD_COLOR)

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

BUBBLE_AREA_MIN     = 80
BUBBLE_AREA_MAX     = 3000
BUBBLE_ASPECT_MIN   = 0.50
BUBBLE_ASPECT_MAX   = 2.0
BUBBLE_CIRC_MIN     = 0.20

valid_bubbles = []

for c in contours:
    area = cv2.contourArea(c)
    if not (BUBBLE_AREA_MIN < area < BUBBLE_AREA_MAX): continue
    
    perimeter = cv2.arcLength(c, True)
    if perimeter < 1: continue
    
    circularity = (4.0 * math.pi * area) / (perimeter * perimeter)
    if circularity < BUBBLE_CIRC_MIN: continue
    
    x_b, y_b, w_b, h_b = cv2.boundingRect(c)
    aspect = w_b / float(h_b) if h_b > 0 else 0
    if not (BUBBLE_ASPECT_MIN < aspect < BUBBLE_ASPECT_MAX): continue
    
    valid_bubbles.append((x_b, y_b, w_b, h_b, circularity, area, aspect))

print(f"Total loose valid bubbles: {len(valid_bubbles)}")

# Let's count how many fall in the OMR regions
OMR_LAYOUT_PAGE1 = [
    {"start":   1, "count": 23, "roi": (0.07, 0.26), "y_start": 0.48},
    {"start":  24, "count": 41, "roi": (0.28, 0.47), "y_start": 0.14},
    {"start":  65, "count": 41, "roi": (0.50, 0.69), "y_start": 0.14},
    {"start": 106, "count": 41, "roi": (0.72, 0.92), "y_start": 0.14},
]
h_img, w_img = thresh.shape[:2]

for i, col in enumerate(OMR_LAYOUT_PAGE1):
    count = 0
    x_min = col["roi"][0] * w_img
    x_max = col["roi"][1] * w_img
    y_min = col["y_start"] * h_img
    
    for b in valid_bubbles:
        x, y, _, _, _, _, _ = b
        if x_min <= x <= x_max and y > y_min:
            count += 1
    print(f"Col {i+1} count: {count} (expected {col['count'] * 4})")

# Let's check the roll area
roll_count = 0
for b in valid_bubbles:
    x, y, _, _, _, _, _ = b
    if 0.04 * w_img < x < 0.34 * w_img and 0.17 * h_img < y < 0.72 * h_img:  # From the code
        roll_count += 1
print(f"Roll count: {roll_count} (expected ~40)")

# Let's check exam set area
set_count = 0
for b in valid_bubbles:
    x, y, _, _, _, _, _ = b
    if 0.04 * w_img < x < 0.30 * w_img and 0.02 * h_img < y < 0.17 * h_img:
        set_count += 1
print(f"Set count: {set_count} (expected ~4)")

