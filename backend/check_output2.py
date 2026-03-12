import sys
import os
import cv2

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import process_omr_image

img = cv2.imread("test_images/1.jpg") # Assuming standard test image
if img is not None:
    result = process_omr_image(img, dyn_threshold=0.08, page_number=1)
    
    print("--- ANSWERS ---")
    for k, v in result["answers"].items():
        if v != "EMPTY":
            print(f"Q{k}: {v}")
    
    print("\n--- STATS ---")
    print(f"Total Detected Answers: {result['total_questions_answered']}")
    print(f"Wrong Questions Count: {result.get('wrong_questions_count', 0)}")
    print(f"Unanswered Questions Count: {result.get('unanswered_questions_count', 0)}")
else:
    print("Error loading image")
