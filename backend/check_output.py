import cv2
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.services.omr_pipeline import detect_bubbles, OMR_LAYOUT_PAGE1, _group_into_rows, DYNAMIC_BIAS, ANSWER_GAP_MIN

thresh = cv2.imread("thresh_debug.png", cv2.IMREAD_GRAYSCALE)
warped = cv2.imread("warped_debug.png")

# Use ACTUAL image dimensions, not hardcoded ones
w_img, h_img = warped.shape[1], warped.shape[0]
print(f"Image size: {w_img}x{h_img}")

bubbles = detect_bubbles(thresh)
if not bubbles:
    print("NO BUBBLES")
    exit()

fill_values = [b["f"] for b in bubbles]
dyn_threshold = float(np.median(fill_values)) + DYNAMIC_BIAS
print(f"Dyn Threshold: {dyn_threshold:.3f}")

results = {}
for col in OMR_LAYOUT_PAGE1:
    x_min = col["roi"][0] * w_img
    x_max = col["roi"][1] * w_img
    y_min = col["y_start"] * h_img

    # Match pipeline: Col 1 uses special filter to skip roll-number bubbles
    y_min_filter = y_min
    if col["start"] == 1:
        y_min_filter = h_img * 0.724

    col_bubbles = [
        b for b in bubbles
        if x_min <= b["x"] <= x_max and b["y"] > y_min_filter
    ]

    rows = _group_into_rows(col_bubbles)

    # Gap-based row -> question mapping (same as pipeline)
    y_centers = []
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

    for i in range(col["count"]):
        cq = col["start"] + i
        q_num = str(cq)
        row = sorted(mapped_rows.get(cq, []), key=lambda b: b["x"])
        real_bubbles = [b for b in row if b.get("f", 0.0) >= 0.0 and b.get("x") > 0]

        if len(real_bubbles) < 4:
            results[q_num] = "EMPTY (len %d)" % len(real_bubbles)
            continue

        row = real_bubbles[-4:]
        ratios = [b["f"] for b in row]
        max_idx = int(np.argmax(ratios))
        top = ratios[max_idx]
        sorted_r = sorted(ratios, reverse=True)
        second = sorted_r[1] if len(sorted_r) > 1 else 0.0

        if top > dyn_threshold and (top - second) > ANSWER_GAP_MIN:
            results[q_num] = chr(65 + max_idx)
        else:
            results[q_num] = "EMPTY (t:%.2f)" % top

print("--- DETECTED ANSWERS ---")
answered_count = 0
for k, v in sorted(results.items(), key=lambda item: int(item[0])):
    if not v.startswith("EMPTY"):
        print("Q%s: %s" % (k, v))
        answered_count += 1
    else:
        if "len 0" not in v and "t:0.0" not in v:
            print("Q%s: %s" % (k, v))
print("Total questions answered: %d" % answered_count)
