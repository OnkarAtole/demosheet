import cv2
import numpy as np

img = cv2.imread(r"d:\LMSProject\3 march omr\omr\backend\last_processed_debug_pg1.png")
if img is None: exit()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

thresh = cv2.adaptiveThreshold(
    gray, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY_INV,
    51, 10
)

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
markers = []

print("Analyzing contours for corner markers...")
for c in contours:
    area = cv2.contourArea(c)
    if area > 400:  # let's be generous
        x, y, w, h = cv2.boundingRect(c)
        aspect = w / float(h)
        if 0.6 <= aspect <= 1.4:
            print(f"Potential marker: Area={area:.1f}, Aspect={aspect:.2f}, X={x}, Y={y}")
            markers.append((x + w // 2, y + h // 2))

print(f"Total markers found: {len(markers)}")
