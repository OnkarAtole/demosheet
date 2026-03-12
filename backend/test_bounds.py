import cv2
import numpy as np

# Use updated layout directly to avoid any import hang
OMR_LAYOUT_PAGE1 = [
    {"start":   1, "count": 23, "roi": (0.06, 0.26), "y_start": 0.50},
    {"start":  24, "count": 41, "roi": (0.28, 0.48), "y_start": 0.12},
    {"start":  65, "count": 41, "roi": (0.50, 0.70), "y_start": 0.12},
    {"start": 106, "count": 41, "roi": (0.72, 0.94), "y_start": 0.12},
]

warped = cv2.imread("warped_debug.png")
if warped is None:
    print("Error: warped_debug.png not found")
    exit(1)

h_img, w_img = warped.shape[:2]
print(f"Dim: {w_img}x{h_img}")

for i, col in enumerate(OMR_LAYOUT_PAGE1):
    x_min = int(col["roi"][0] * w_img)
    x_max = int(col["roi"][1] * w_img)
    y_min = int(col["y_start"] * h_img)
    
    cv2.rectangle(warped, (x_min, y_min), (x_max, h_img-1), (255, 0, 0), 2)
    cv2.putText(warped, f"Col {i+1} start Q{col['start']}", (x_min, y_min-10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

cv2.imwrite("bounds_debug.png", warped)
print("Saved bounds_debug.png")
