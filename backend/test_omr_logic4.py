import cv2
import numpy as np

img = cv2.imread(r"d:\LMSProject\3 march omr\omr\backend\last_processed_debug_pg0.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (3, 3), 0)
thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 7)
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

bubbles = []
for c in contours:
    area = cv2.contourArea(c)
    perimeter = cv2.arcLength(c, True)
    if perimeter == 0: continue
    circularity = 4 * np.pi * area / (perimeter * perimeter)
    if 100 < area < 1500 and circularity > 0.5:
        (xc, yc), radius = cv2.minEnclosingCircle(c)
        bubbles.append({'x': int(xc), 'y': int(yc), 'r': int(radius)})

h_img, w_img = img.shape[:2]

print("Top Left (Likely Exam Set):")
top_left = [b for b in bubbles if b['x'] < 0.4 * w_img and b['y'] < 0.25 * h_img]
print(f"Count: {len(top_left)}")
if top_left:
    min_x = min(b['x'] for b in top_left) / w_img
    max_x = max(b['x'] for b in top_left) / w_img
    min_y = min(b['y'] for b in top_left) / h_img
    max_y = max(b['y'] for b in top_left) / h_img
    print(f"X range: {min_x:.3f} to {max_x:.3f}")
    print(f"Y range: {min_y:.3f} to {max_y:.3f}")

print("\nMid Left (Likely Roll Number):")
mid_left = [b for b in bubbles if b['x'] < 0.4 * w_img and 0.25 * h_img < b['y'] < 0.6 * h_img]
print(f"Count: {len(mid_left)}")
if mid_left:
    min_x = min(b['x'] for b in mid_left) / w_img
    max_x = max(b['x'] for b in mid_left) / w_img
    min_y = min(b['y'] for b in mid_left) / h_img
    max_y = max(b['y'] for b in mid_left) / h_img
    print(f"X range: {min_x:.3f} to {max_x:.3f}")
    print(f"Y range: {min_y:.3f} to {max_y:.3f}")

print("\nQuestion Column 1 (Likely Q1-Q23):")
col_1 = [b for b in bubbles if b['x'] < 0.4 * w_img and b['y'] > 0.6 * h_img]
print(f"Count: {len(col_1)}")
if col_1:
    min_x = min(b['x'] for b in col_1) / w_img
    max_x = max(b['x'] for b in col_1) / w_img
    min_y = min(b['y'] for b in col_1) / h_img
    max_y = max(b['y'] for b in col_1) / h_img
    print(f"X range: {min_x:.3f} to {max_x:.3f}")
    print(f"Y range: {min_y:.3f} to {max_y:.3f}")

print("\nQuestion Column 2 (Likely Q24-Q64):")
col_2 = [b for b in bubbles if 0.4 * w_img < b['x'] < 0.65 * w_img]
print(f"Count: {len(col_2)}")
if col_2:
    min_x = min(b['x'] for b in col_2) / w_img
    max_x = max(b['x'] for b in col_2) / w_img
    min_y = min(b['y'] for b in col_2) / h_img
    max_y = max(b['y'] for b in col_2) / h_img
    print(f"X range: {min_x:.3f} to {max_x:.3f}")
    print(f"Y range: {min_y:.3f} to {max_y:.3f}")

print("\nQuestion Column 3 (Likely Q65-Q100):")
col_3 = [b for b in bubbles if b['x'] > 0.65 * w_img]
print(f"Count: {len(col_3)}")
if col_3:
    min_x = min(b['x'] for b in col_3) / w_img
    max_x = max(b['x'] for b in col_3) / w_img
    min_y = min(b['y'] for b in col_3) / h_img
    max_y = max(b['y'] for b in col_3) / h_img
    print(f"X range: {min_x:.3f} to {max_x:.3f}")
    print(f"Y range: {min_y:.3f} to {max_y:.3f}")

