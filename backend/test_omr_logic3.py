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

print(f"Detected {len(bubbles)} valid bubbles")

# Output bounding box of all bubbles
if bubbles:
    min_x = min(b['x'] for b in bubbles)
    max_x = max(b['x'] for b in bubbles)
    min_y = min(b['y'] for b in bubbles)
    max_y = max(b['y'] for b in bubbles)
    
    h_img, w_img = img.shape[:2]
    
    print(f"Overall bounding box:")
    print(f"X: {min_x} to {max_x} ({min_x/w_img:.2f} to {max_x/w_img:.2f})")
    print(f"Y: {min_y} to {max_y} ({min_y/h_img:.2f} to {max_y/h_img:.2f})")
    
    # Try horizontal strip grouping to see rows
    strip_w = w_img
    
    for row_y in range(0, 10, 2):
        roi_y_min = row_y / 10.0
        roi_y_max = (row_y + 2) / 10.0
        b_in_strip = [b for b in bubbles if roi_y_min * h_img < b['y'] < roi_y_max * h_img]
        print(f"Strip Y {roi_y_min:.1f}-{roi_y_max:.1f}: {len(b_in_strip)} bubbles")
        if b_in_strip:
            b_min_x = min(b['x'] for b in b_in_strip) / w_img
            b_max_x = max(b['x'] for b in b_in_strip) / w_img
            print(f"  X span: {b_min_x:.2f} to {b_max_x:.2f}")

