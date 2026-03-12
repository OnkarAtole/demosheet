import cv2
import numpy as np
import math

# Use the saved warped image directly since thresh_debug is already thresholded
gray = cv2.imread("warped_debug.png", cv2.IMREAD_GRAYSCALE)
if gray is None: exit()

# Our current dual threshold logic:
t_adaptive = cv2.adaptiveThreshold(
    gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 101, 5
)
_, t_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
combined = cv2.bitwise_or(t_adaptive, t_otsu)

# Morphological open to remove speckle noise
kernel = np.ones((3, 3), np.uint8)
# Dilation first then erosion (closing) might be better to connect broken bubble edges!
# wait, morph_close is better for bubbles that might have small gaps in their lines!
cleaned = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel, iterations=1)

# Let's try finding bubbles on cleaned
cnts_cleaned, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

cleaned_close = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=1)
cnts_close, _ = cv2.findContours(cleaned_close, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

def get_valid_bubbles(cnts):
    valid = []
    for c in cnts:
        area = cv2.contourArea(c)
        if 80 < area < 3000:
            perimeter = cv2.arcLength(c, True)
            if perimeter > 0:
                circularity = (4.0 * math.pi * area) / (perimeter * perimeter)
                if circularity > 0.3:
                    x,y,w,h = cv2.boundingRect(c)
                    if 0.5 < w/float(h) < 2.0:
                        valid.append(c)
    return valid

print(f"Valid bubbles OPEN: {len(get_valid_bubbles(cnts_cleaned))}")
print(f"Valid bubbles CLOSE: {len(get_valid_bubbles(cnts_close))}")

# Let's find why there might be less. Is there a big bounding box issue? Let's check the size of the image.
print(f"Image shape: {gray.shape}")
