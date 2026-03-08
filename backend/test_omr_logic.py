import cv2
import numpy as np

img = cv2.imread(r"d:\LMSProject\3 march omr\omr\backend\last_processed_debug_pg0.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (3, 3), 0)
thresh = cv2.adaptiveThreshold(
    blur, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY_INV,
    31, 7
)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

bubbles = []
for c in contours:
    area = cv2.contourArea(c)
    perimeter = cv2.arcLength(c, True)
    if perimeter == 0: continue
    circularity = 4 * np.pi * area / (perimeter * perimeter)
    if 300 < area < 1200 and circularity > 0.6:
        (xc, yc), radius = cv2.minEnclosingCircle(c)
        bubbles.append((int(xc), int(yc), int(radius * 2)))

print(f"Detected {len(bubbles)} bubbles based on size and circularity.")

# Check roll area
h_img, w_img = img.shape[:2]
roll_area = [
    b for b in bubbles
    if 0.05 * w_img < b[0] < 0.25 * w_img
    and 0.18 * h_img < b[1] < 0.50 * h_img
]
print(f"Roll area bubbles: {len(roll_area)}")

set_area = [
    b for b in bubbles
    if 0.05 * w_img < b[0] < 0.25 * w_img
    and b[1] < 0.15 * h_img
]
print(f"Set area bubbles: {len(set_area)}")
