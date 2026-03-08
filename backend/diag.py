import cv2, sys, os, numpy as np
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles, OMR_LAYOUT_PAGE1, _group_into_rows, DYNAMIC_BIAS, ANSWER_GAP_MIN, detect_roll_number, detect_exam_set

warped = cv2.imread("warped_debug.png")
thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
w_img, h_img = warped.shape[1], warped.shape[0]
print(f"Image size: {w_img}x{h_img}")

bubbles = detect_bubbles(thresh)
fill_values = [b["f"] for b in bubbles]
dyn_threshold = float(np.median(fill_values)) + DYNAMIC_BIAS
print(f"Dyn Threshold: {dyn_threshold:.3f}\n")

# Test Roll Number
roll = detect_roll_number(bubbles, w_img, h_img, dyn_threshold)
print(f"Detected Roll Number: {roll}")

# Test Exam Set
exam_set = detect_exam_set(bubbles, w_img, h_img, dyn_threshold)
print(f"Detected Exam Set: {exam_set}")

results = {}
for col in OMR_LAYOUT_PAGE1:
    x_min = col["roi"][0] * w_img
    x_max = col["roi"][1] * w_img
    y_min = col["y_start"] * h_img

    y_min_filter = y_min # Now reflects the updated 0.50 for Col 1
    
    col_bubbles = [b for b in bubbles if x_min <= b["x"] <= x_max and b["y"] > y_min_filter]
    rows = _group_into_rows(col_bubbles)
    
    # Gap-based loop
    if len(rows) > 0:
        y_centers = [float(np.mean([b["y"] for b in r])) for r in rows]
        gaps = [y_centers[i] - y_centers[i-1] for i in range(1, len(y_centers))]
        valid_gaps = [g for g in gaps if 25 < g < 55]
        median_gap = float(np.median(valid_gaps)) if valid_gaps else 38.0
    else:
        median_gap = 38.0
    
    max_q = col["start"] + col["count"]
    mapped_rows = {}
    current_q = col["start"]
    last_y = None
    for r in rows:
        y_c = float(np.mean([b["y"] for b in r]))
        if last_y is not None:
            gap = y_c - last_y
            if gap > (median_gap * 1.5):
                skipped = int(round(gap / median_gap)) - 1
                current_q += max(0, skipped)
        if current_q < max_q:
            mapped_rows[current_q] = r
        current_q += 1
        last_y = y_c

    for cq in range(col["start"], col["start"] + col["count"]):
        q_num = str(cq)
        row = sorted(mapped_rows.get(cq, []), key=lambda b: b["x"])
        real_bubbles = [b for b in row if b.get("f", 0.0) >= 0.0 and b.get("x") > 0]
        
        if len(real_bubbles) < 4:
            if len(real_bubbles) > 0:
                results[q_num] = f"EMPTY (len {len(real_bubbles)})"
            continue
        
        row = real_bubbles[-4:]
        ratios = [b["f"] for b in row]
        max_idx = int(np.argmax(ratios))
        top = ratios[max_idx]
        sorted_r = sorted(ratios, reverse=True)
        second = sorted_r[1] if len(sorted_r) > 1 else 0.0
        
        if top > dyn_threshold and (top - second) > ANSWER_GAP_MIN:
            results[q_num] = chr(65 + max_idx)

print("\n--- ANSWERS ---")
answered = 0
for k, v in sorted(results.items(), key=lambda x: int(x[0])):
    print(f"Q{k}: {v}")
    if not v.startswith("EMPTY"):
        answered += 1
print(f"\nTotal answered: {answered}")
