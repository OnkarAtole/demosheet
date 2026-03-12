import cv2
import numpy as np

img = cv2.imread(r"d:\LMSProject\3 march omr\omr\backend\last_processed_debug_pg1.png")
if img is None: exit()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

blur = cv2.GaussianBlur(gray, (5, 5), 0)

# Try Otsu alone
_, t_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
cnts, _ = cv2.findContours(t_otsu, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
valid = sum(1 for c in cnts if 150 < cv2.contourArea(c) < 2000 and cv2.arcLength(c, True) > 0 and 0.5 < (4.0 * np.pi * cv2.contourArea(c)) / (cv2.arcLength(c, True)**2))
print(f"Otsu alone: Valid = {valid}")

for bs in [71, 101, 121, 151]:
    for C in [5, 7, 10]:
        t = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, bs, C)
        combined = cv2.bitwise_or(t, t_otsu)
        kernel = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(combined, cv2.MORPH_OPEN, kernel, iterations=1)
        cnts, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        valid = 0
        for c in cnts:
            a = cv2.contourArea(c)
            if 150 < a < 2500:
                p = cv2.arcLength(c, True)
                if p > 0:
                    circ = (4.0 * np.pi * a) / (p*p)
                    if circ > 0.5:
                        x,y,w,h = cv2.boundingRect(c)
                        asp = w / float(h)
                        if 0.7 < asp < 1.3:
                            valid += 1
        print(f"BlockSize={bs}, C={C} + Otsu: Valid Bubbles = {valid}")

