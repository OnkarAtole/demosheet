import cv2

img = cv2.imread(r"d:\LMSProject\3 march omr\omr\backend\last_processed_debug_pg0.png")
if img is not None:
    print(f"Debug image shape: {img.shape}")
else:
    print("Could not load debug image.")
