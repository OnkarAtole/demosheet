import cv2
import numpy as np

img = cv2.imread("warped_debug.png")
if img is None:
    print("Could not load warped_debug.png")
else:
    print(f"warped_debug.png size: {img.shape}")
