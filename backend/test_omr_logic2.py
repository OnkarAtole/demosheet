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

data = []
for c in contours:
    area = cv2.contourArea(c)
    perimeter = cv2.arcLength(c, True)
    if perimeter == 0: continue
    circularity = 4 * np.pi * area / (perimeter * perimeter)
    data.append((area, circularity))

data.sort(key=lambda x: x[0], reverse=True)
print(f"Top 20 areas: {[d[0] for d in data[:20]]}")
print(f"Circularity for top 20: {[d[1] for d in data[:20]]}")

bubbles = [d for d in data if 100 < d[0] < 2000]
print(f"Bubbles between 100 and 2000 area: {len(bubbles)}")
print(f"Circularity > 0.5: {len([b for b in bubbles if b[1] > 0.5])}")
