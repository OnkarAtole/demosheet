import cv2
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles

thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
warped = cv2.imread("warped_debug.png", cv2.IMREAD_COLOR)

h_img, w_img = warped.shape[:2]
bubbles = detect_bubbles(thresh)

print(f"Top bubbles (y < 450):")
for b in sorted([b for b in bubbles if b['y'] < 450], key=lambda b: b['y']):
    print(f"  x={b['x']:.1f}, y={b['y']:.1f}, f={b['f']:.2f}")

