"""
=============================================================
 OMR Pipeline  —  Production-Level Computer Vision Engine
=============================================================
Pipeline stages
---------------
1. decode_image        — bytes → BGR ndarray
2. detect_blur         — Laplacian variance check
3. normalize_lighting  — CLAHE + GaussianBlur
4. detect_paper        — Canny + contour → 4-corner sheet crop
5. perspective_transform — warpPerspective to canonical rectangle
6. gamma_correction    — brightness stabilisation (day/night)
7. dual_threshold      — adaptive OR Otsu + morphology open
8. detect_bubbles      — area / aspect / circularity filters
9. detect_roll_number  — column-based digit extraction
10. detect_exam_set    — 4-bubble row near top-left
11. detect_answers     — ROI columns, dynamic fill threshold
12. draw_debug         — annotated PNG written to disk

Author  : Antigravity / Google Deepmind
Version : 2.0.0  (2026-03-07)
=============================================================
"""

from __future__ import annotations

import math
import os
import logging
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger("omr_pipeline")

# ─────────────────────────────────────────────────────────────
# CONSTANTS — tuned for 4:3, ≥1600 px wide images
# ─────────────────────────────────────────────────────────────

BLUR_THRESHOLD      = 80.0   # Laplacian variance; below → blurry
CLAHE_CLIP_LIMIT    = 2.0
CLAHE_GRID          = (8, 8)
CANNY_LOW           = 50
CANNY_HIGH          = 150
MIN_PAPER_AREA_FRAC = 0.10   # sheet must cover at least 10 % of frame

# Bubble geometry filters
BUBBLE_AREA_MIN     = 60
BUBBLE_AREA_MAX     = 2500
BUBBLE_ASPECT_MIN   = 0.50
BUBBLE_ASPECT_MAX   = 1.50
BUBBLE_CIRC_MIN     = 0.65   # Circles are 1.0, Squares are ~0.78; 0.65 ignores text bits.
INNER_RADIUS_FRAC   = 0.60   # inner masking circle = 60 % of enclosing radius

# Fill scoring
DYNAMIC_BIAS        = 0.05   # Tuned for stable fill detection
ANSWER_GAP_MIN      = 0.05   # top fill must exceed 2nd by this margin

# Roll-number specifics
ROLL_GAP_MIN        = 0.06   # top fill must exceed 2nd by this margin for digits

# Gamma for night / day stability
GAMMA               = 1.2

# Page layout — fractions of (warped_width, warped_height)
# Each column: start question number, max_count, x-ROI (x_min%, x_max%), y_start%
OMR_LAYOUT: List[dict] = [
    {"start":   1, "count": 23, "roi": (0.13, 0.28), "y_start": 0.50},
    {"start":  24, "count": 41, "roi": (0.34, 0.49), "y_start": 0.12},
    {"start":  65, "count": 41, "roi": (0.56, 0.71), "y_start": 0.12},
    {"start": 106, "count": 41, "roi": (0.77, 0.94), "y_start": 0.12},
]

DEBUG_PATH = "last_processed_debug.png"

# ─────────────────────────────────────────────────────────────
# STAGE 1 — Decode
# ─────────────────────────────────────────────────────────────

def decode_image(image_bytes: bytes) -> np.ndarray:
    """Convert raw bytes → BGR ndarray."""
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("decode_image: invalid or corrupt image bytes")
    return img


# ─────────────────────────────────────────────────────────────
# STAGE 2 — Blur detection
# ─────────────────────────────────────────────────────────────

def detect_blur(img: np.ndarray) -> Tuple[float, bool]:
    """
    Returns (variance_of_laplacian, is_blurry).
    is_blurry is True when variance < BLUR_THRESHOLD.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    score = cv2.Laplacian(gray, cv2.CV_64F).var()
    return score, score < BLUR_THRESHOLD


# ─────────────────────────────────────────────────────────────
# STAGE 3 — Lighting normalisation
# ─────────────────────────────────────────────────────────────

def normalize_lighting(img: np.ndarray) -> np.ndarray:
    """
    Convert to grayscale, apply CLAHE for contrast equalisation
    (works in low-light and high-light), then GaussianBlur for noise
    reduction.  Returns a single-channel uint8 image.
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_GRID)
    eq = clahe.apply(gray)
    blurred = cv2.GaussianBlur(eq, (5, 5), 0)
    return blurred


# ─────────────────────────────────────────────────────────────
# STAGE 4 — Paper / sheet detection
# ─────────────────────────────────────────────────────────────

def _order_corners(pts: np.ndarray) -> np.ndarray:
    """
    Order 4 points as [top-left, top-right, bottom-right, bottom-left].
    """
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(s)]    # top-left
    rect[2] = pts[np.argmax(s)]    # bottom-right
    rect[1] = pts[np.argmin(diff)] # top-right
    rect[3] = pts[np.argmax(diff)] # bottom-left
    return rect


def detect_paper(blurred_gray: np.ndarray,
                  original_img: np.ndarray) -> Optional[np.ndarray]:
    """
    Detect the 4 corner markers (black squares) to find the OMR sheet bounds.
    Returns the ordered 4x2 float32 corner array or None.
    """
    thresh = cv2.adaptiveThreshold(
        blurred_gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        51, 10
    )

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    squares = []
    
    for c in contours:
        area = cv2.contourArea(c)
        if area > 400:
            x, y, w, h = cv2.boundingRect(c)
            aspect = w / float(h)
            if 0.75 <= aspect <= 1.25:
                hull = cv2.convexHull(c)
                hull_area = cv2.contourArea(hull)
                if hull_area > 0 and (area / hull_area) > 0.8:
                    squares.append((area, x + w // 2, y + h // 2))

    if len(squares) >= 4:
        squares.sort(key=lambda s: s[0], reverse=True)
        top_4 = squares[:4]
        markers = [(pt[1], pt[2]) for pt in top_4]
        pts = np.array(markers, dtype="float32")
        return _order_corners(pts)

    logger.warning("detect_paper: Found %d square markers, expected 4.", len(squares))
    return None

# ─────────────────────────────────────────────────────────────
# STAGE 5 — Perspective transform
# ─────────────────────────────────────────────────────────────

def perspective_transform(img: np.ndarray,
                          corners: np.ndarray) -> np.ndarray:
    """
    Warp the detected paper region from the 4 corner markers to a flat rectangle.
    """
    tl, tr, br, bl = corners
    widthA = np.linalg.norm(br - bl)
    widthB = np.linalg.norm(tr - tl)
    heightA = np.linalg.norm(tr - br)
    heightB = np.linalg.norm(tl - bl)

    maxWidth = int(max(widthA, widthB))
    maxHeight = int(max(heightA, heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(corners, dst)
    return cv2.warpPerspective(img, M, (maxWidth, maxHeight))


# ─────────────────────────────────────────────────────────────
# STAGE 6 — Gamma correction (day/night brightness balance)
# ─────────────────────────────────────────────────────────────

def gamma_correction(img: np.ndarray, gamma: float = GAMMA) -> np.ndarray:
    inv_gamma = 1.0 / gamma
    lut = np.array(
        [((i / 255.0) ** inv_gamma) * 255 for i in range(256)],
        dtype="uint8"
    )
    return cv2.LUT(img, lut)


# ─────────────────────────────────────────────────────────────
# STAGE 7 — Dual thresholding + morphology clean-up
# ─────────────────────────────────────────────────────────────

def dual_threshold(gray: np.ndarray) -> np.ndarray:
    t_adaptive = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        101, 5
    )
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(t_adaptive, cv2.MORPH_CLOSE, kernel, iterations=1)
    return cleaned


# ─────────────────────────────────────────────────────────────
# STAGE 8 — Bubble detection
# ─────────────────────────────────────────────────────────────

BubbleInfo = Dict  # {x, y, f (fill ratio), h (diameter), r (radius)}


def _fill_ratio(thresh: np.ndarray, cx: int, cy: int,
                radius: float) -> float:
    inner = max(1, int(radius * INNER_RADIUS_FRAC))
    mask  = np.zeros(thresh.shape, dtype="uint8")
    cv2.circle(mask, (cx, cy), inner, 255, -1)
    filled = cv2.countNonZero(cv2.bitwise_and(thresh, thresh, mask=mask))
    total  = math.pi * inner * inner
    return filled / total if total > 0 else 0.0


def detect_bubbles(thresh: np.ndarray) -> List[BubbleInfo]:
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    bubbles: List[BubbleInfo] = []

    for c in contours:
        area = cv2.contourArea(c)
        if not (BUBBLE_AREA_MIN < area < BUBBLE_AREA_MAX):
            continue

        perimeter = cv2.arcLength(c, True)
        if perimeter < 1:
            continue

        circularity = (4.0 * math.pi * area) / (perimeter * perimeter)
        if circularity < BUBBLE_CIRC_MIN:
            continue

        x_b, y_b, w_b, h_b = cv2.boundingRect(c)
        aspect = w_b / float(h_b) if h_b > 0 else 0
        if not (BUBBLE_ASPECT_MIN < aspect < BUBBLE_ASPECT_MAX):
            continue

        (cx, cy), radius = cv2.minEnclosingCircle(c)
        cx, cy = int(cx), int(cy)

        fill = _fill_ratio(thresh, cx, cy, radius)

        bubbles.append({
            "x": cx,
            "y": cy,
            "f": fill,
            "h": int(radius * 2),
            "r": radius,
            "area": area,
        })

    if bubbles:
        med_area = float(np.median([b["area"] for b in bubbles]))
        bubbles = [b for b in bubbles if b["area"] > med_area * 0.70] # Relaxed area filter

    return bubbles


# ─────────────────────────────────────────────────────────────
# STAGE 9 — Row grouping helper
# ─────────────────────────────────────────────────────────────

def _group_into_rows(bubbles: List[BubbleInfo]) -> List[List[BubbleInfo]]:
    if not bubbles:
        return []
    bubbles = sorted(bubbles, key=lambda b: b["y"])
    median_h = float(np.median([b["h"] for b in bubbles])) if bubbles else 24
    y_tol    = median_h * 0.80

    rows: List[List[BubbleInfo]] = []
    current = [bubbles[0]]
    for b in bubbles[1:]:
        if abs(b["y"] - current[0]["y"]) < y_tol:
            current.append(b)
        else:
            rows.append(sorted(current, key=lambda x: x["x"]))
            current = [b]
    rows.append(sorted(current, key=lambda x: x["x"]))
    return rows


def _compute_dynamic_threshold(fill_values: List[float]) -> float:
    if not fill_values:
        return 0.22
    return float(np.median(fill_values)) + DYNAMIC_BIAS


# ─────────────────────────────────────────────────────────────
# STAGE 10 — Answer extraction per page
# ─────────────────────────────────────────────────────────────

def detect_answers(bubbles: List[BubbleInfo],
                   w_img: int,
                   h_img: int,
                   dyn_threshold: float) -> Dict[str, str]:
    """
    For each layout column, group bubbles into question rows and pick
    the selected answer using the dynamic threshold + gap rule.
    """
    results: Dict[str, str] = {}

    for col in OMR_LAYOUT:
        x_min, x_max = col["roi"][0] * w_img, col["roi"][1] * w_img
        y_min = col["y_start"] * h_img

        col_bubbles = [b for b in bubbles if x_min <= b["x"] <= x_max and b["y"] > y_min]
        rows = _group_into_rows(col_bubbles)
        
        median_gap = 38.0
        if len(rows) > 0:
            y_centers = [float(np.mean([b["y"] for b in r])) for r in rows]
            gaps = [y_centers[i] - y_centers[i-1] for i in range(1, len(y_centers))]
            valid_gaps = [g for g in gaps if 25 < g < 55]
            median_gap = float(np.median(valid_gaps)) if valid_gaps else 38.0
            
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
            current_q = col["start"] + i
            q_num = str(current_q)
            row = sorted(mapped_rows.get(current_q, []), key=lambda b: b["x"])

            real_bubbles = [b for b in row if b.get("x", 0) > 0]
            if 1 < len(real_bubbles) < 4:
                roi_x_min, roi_width = x_min, (x_max - x_min)
                expected_xs = [roi_x_min + (f * roi_width) for f in [0.12, 0.38, 0.62, 0.88]]
                padded_row = []
                for exp_x in expected_xs:
                    closest = next((b for b in row if abs(b["x"]-exp_x) < roi_width*0.15), None)
                    padded_row.append(closest if closest else {"x": int(exp_x), "f": 0.0, "r": 12})
                row = padded_row
            elif len(real_bubbles) <= 1:
                row = [{"x": 0, "f": 0.0}] * 4

            row = row[-4:]
            ratios = [b.get("f", 0.0) for b in row]
            max_idx = int(np.argmax(ratios))
            top, sorted_r = ratios[max_idx], sorted(ratios, reverse=True)
            second  = sorted_r[1] if len(sorted_r) > 1 else 0.0

            if top > dyn_threshold and (top - second) > ANSWER_GAP_MIN:
                results[q_num] = chr(65 + max_idx)
            else:
                results[q_num] = "EMPTY"

    return results


# ─────────────────────────────────────────────────────────────
# STAGE 11 — Roll number detection
# ─────────────────────────────────────────────────────────────

def detect_roll_number(bubbles: List[BubbleInfo],
                       w_img: int,
                       h_img: int,
                       dyn_threshold: float) -> str:
    roll_area = [
        b for b in bubbles
        if 0.08 * w_img < b["x"] < 0.34 * w_img
        and 0.21 * h_img < b["y"] < 0.49 * h_img
    ]
    if not roll_area:
        return "EMPTY"

    roll_area = sorted(roll_area, key=lambda b: b["x"])
    x_tol = w_img * 0.025
    columns: List[List[BubbleInfo]] = []
    current = [roll_area[0]]
    for b in roll_area[1:]:
        if abs(b["x"] - current[0]["x"]) < x_tol:
            current.append(b)
        else:
            columns.append(current)
            current = [b]
    columns.append(current)

    all_rows = _group_into_rows(roll_area)
    if len(all_rows) > 10:
        # Sort vertically and take the bottom-most 10 rows (the grid)
        all_rows = sorted(all_rows, key=lambda r: np.mean([b["y"] for b in r]))[-10:]
    
    row_y_centers = sorted([float(np.mean([b["y"] for b in r])) for r in all_rows])
    
    digits: List[str] = []
    for col_bubbles in columns:
        grid = [None] * 10
        for b in col_bubbles:
            best_r, min_d = -1, float('inf')
            for r_idx, ry in enumerate(row_y_centers):
                d = abs(b["y"] - ry)
                if d < min_d:
                    min_d, best_r = d, r_idx
            if best_r != -1 and min_d < 25:
                grid[best_r] = b
        
        ratios = [b["f"] if b else 0.0 for b in grid]
        max_idx = int(np.argmax(ratios))
        top, sorted_r = ratios[max_idx], sorted(ratios, reverse=True)
        second = sorted_r[1] if len(sorted_r) > 1 else 0.0

        if top > dyn_threshold and (top - second) > ROLL_GAP_MIN:
            digits.append(str(max_idx))
        else:
            digits.append("X")

    return "".join(digits)


# ─────────────────────────────────────────────────────────────
# STAGE 11b — Exam set detection
# ─────────────────────────────────────────────────────────────

def detect_exam_set(bubbles: List[BubbleInfo],
                    w_img: int,
                    h_img: int,
                    dyn_threshold: float) -> str:
    set_area = [
        b for b in bubbles
        if 0.04 * w_img < b["x"] < 0.30 * w_img
        and 0.02 * h_img < b["y"] < 0.20 * h_img
    ]
    if not set_area:
        return "EMPTY"

    set_area = sorted(set_area, key=lambda b: b["x"])[:4]
    ratios   = [b["f"] for b in set_area]
    max_idx  = int(np.argmax(ratios))
    top      = ratios[max_idx]
    second   = sorted(ratios, reverse=True)[1] if len(ratios) > 1 else 0.0

    if top > dyn_threshold and (top - second) > ANSWER_GAP_MIN:
        return str(max_idx + 1)
    return "EMPTY"


# ─────────────────────────────────────────────────────────────
# Debug image writer
# ─────────────────────────────────────────────────────────────

def _draw_debug(img: np.ndarray,
                bubbles: List[BubbleInfo],
                answers: Dict[str, str],
                roll: str,
                exam_set: str,
                dyn_threshold: float,
                page: int) -> np.ndarray:
    """
    Annotate markers on image.
    """
    debug = img.copy()
    # 2. Draw Bubbles & Question Mapping
    for b in bubbles:
        is_filled = b["f"] > dyn_threshold
        color = (0, 200, 0) if is_filled else (0, 0, 220)
        cv2.circle(debug, (int(b["x"]), int(b["y"])), 12, color, 2)
        if is_filled:
            cv2.circle(debug, (int(b["x"]), int(b["y"])), 4, color, -1)

    h, w = debug.shape[:2]
    overlay = [f"Roll: {roll}", f"Set: {exam_set}", f"Pg: {page}"]
    for i, txt in enumerate(overlay):
        cv2.putText(debug, txt, (15, 30 + i*30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    return debug


# ─────────────────────────────────────────────────────────────
# PUBLIC ENTRY POINT
# ─────────────────────────────────────────────────────────────

def scan_omr_page(image_bytes: bytes,
                  page_number: int,
                  debug_path: str = DEBUG_PATH) -> Dict:
    result = {
        "answers": {}, "roll_number": "EMPTY", "exam_set": "EMPTY",
        "blur_score": 0.0, "bubble_count": 0, "dyn_threshold": 0.22, "error": None,
    }

    try:
        img = decode_image(image_bytes)
        score, is_blurry = detect_blur(img)
        result["blur_score"] = score
        
        # Stages
        blurred_gray = normalize_lighting(img)
        corners = detect_paper(blurred_gray, img)
        if corners is not None:
            warped = perspective_transform(img, corners)
        else:
            warped = img
            
        warped = gamma_correction(warped, GAMMA)
        warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        thresh = dual_threshold(warped_gray)
        
        cv2.imwrite("thresh_debug.png", thresh)
        cv2.imwrite("warped_debug.png", warped)

        bubbles = detect_bubbles(thresh)
        result["bubble_count"] = len(bubbles)
        if not bubbles:
            return result

        dyn_threshold = _compute_dynamic_threshold([b["f"] for b in bubbles])
        result["dyn_threshold"] = dyn_threshold
        
        h_img, w_img = warped.shape[:2]
        # Answers
        answers = detect_answers(bubbles, warped.shape[1], warped.shape[0], dyn_threshold)
        result["answers"] = answers

        # Roll number (optional Stage 9)
        roll = detect_roll_number(bubbles, warped.shape[1], warped.shape[0], dyn_threshold)
        result["roll_number"] = roll

        # Exam set (optional Stage 10)
        exam_set = detect_exam_set(bubbles, warped.shape[1], warped.shape[0], dyn_threshold)
        result["exam_set"] = exam_set

        # Draw debug
        debug_img = _draw_debug(warped, bubbles, answers, roll, exam_set, dyn_threshold, 1)
        cv2.imwrite(debug_path, debug_img)

    except Exception as e:
        logger.error("scan_omr_page failed: %s", traceback.format_exc())
        result["error"] = str(e)

    return result
