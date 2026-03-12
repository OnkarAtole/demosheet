import cv2
import numpy as np
import math

thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
warped = cv2.imread("warped_debug.png", cv2.IMREAD_COLOR)

# BUBBLE PARAMS
BUBBLE_AREA_MIN     = 100
BUBBLE_AREA_MAX     = 2500
BUBBLE_ASPECT_MIN   = 0.60
BUBBLE_ASPECT_MAX   = 1.40
BUBBLE_CIRC_MIN     = 0.45

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for c in contours:
    area = cv2.contourArea(c)
    if area < 50: continue
    
    perimeter = cv2.arcLength(c, True)
    if perimeter < 1: continue
    
    circularity = (4.0 * math.pi * area) / (perimeter * perimeter)
    x_b, y_b, w_b, h_b = cv2.boundingRect(c)
    aspect = w_b / float(h_b) if h_b > 0 else 0
    
    (cx, cy), radius = cv2.minEnclosingCircle(c)
    
    is_valid = (
        BUBBLE_AREA_MIN < area < BUBBLE_AREA_MAX and
        BUBBLE_ASPECT_MIN < aspect < BUBBLE_ASPECT_MAX and
        circularity > BUBBLE_CIRC_MIN
    )
    
    color = (0, 255, 0) if is_valid else (0, 0, 255)
    thick = 2 if is_valid else 1
    cv2.circle(warped, (int(cx), int(cy)), int(radius), color, thick)
    if not is_valid and area > 100:
        cv2.putText(warped, f"C:{circularity:.2f} A:{area:.0f}", (int(cx), int(cy)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

cv2.imwrite("contour_debug.png", warped)
print("Finished saving contour_debug.png")
