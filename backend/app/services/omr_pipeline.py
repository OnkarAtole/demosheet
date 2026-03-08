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
import traceback
import itertools
import logging
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

logger = logging.getLogger("omr_pipeline")

# ─────────────────────────────────────────────────────────────
# CONSTANTS — tuned for 4:3, ≥1600 px wide images
# ─────────────────────────────────────────────────────────────

CANONICAL_WIDTH     = 1600   # Warped image is ALWAYS resized to this width
                             # so bubble-area filters work at any capture distance

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

DEBUG_PATH = "last_processed_debug.png"  # Fallback; overridden per-page below

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
# STAGE 4 — Paper / sheet detection (distance-robust)
# ─────────────────────────────────────────────────────────────

def _order_corners(pts: np.ndarray) -> np.ndarray:
    """
    Order 4 points as [top-left, top-right, bottom-right, bottom-left].
    """
    rect = np.zeros((4, 2), dtype="float32")
    # pts shape is (4, 2)
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    
    rect[0] = pts[np.argmin(s)]    # top-left
    rect[2] = pts[np.argmax(s)]    # bottom-right
    rect[1] = pts[np.argmin(diff)] # top-right
    rect[3] = pts[np.argmax(diff)] # bottom-left
    return rect


def _is_valid_quadrilateral(pts: np.ndarray, img_h: int, img_w: int) -> bool:
    """
    Sanity-check for OMR-sheet rectangle.
    """
    if len(pts) != 4:
        return False
        
    ordered = _order_corners(pts)
    
    # 1. Bounds check
    for p in ordered:
        if not (-10 <= p[0] <= img_w + 10 and -10 <= p[1] <= img_h + 10):
            return False

    # 2. Area check (Relative to image)
    # Using 0.05 (5%) to allow very distant captures
    quad_area = cv2.contourArea(ordered.astype(np.int32))
    img_area = img_h * img_w
    if quad_area < img_area * 0.05:
        return False

    # 3. Aspect Ratio check
    w1 = np.linalg.norm(ordered[0] - ordered[1])
    w2 = np.linalg.norm(ordered[2] - ordered[3])
    h1 = np.linalg.norm(ordered[0] - ordered[3])
    h2 = np.linalg.norm(ordered[1] - ordered[2])
    avg_w = (w1 + w2) / 2
    avg_h = (h1 + h2) / 2
    
    if avg_h == 0: return False
    aspect = avg_w / avg_h
    # OMR is usually portrait (~0.7) or landscape (~1.4). Allow 0.4 to 2.5
    if not (0.35 <= aspect <= 2.8):
        return False

    return True


def _find_square_markers(thresh: np.ndarray, min_area: int) -> list:
    """
    Find square-like contours. Returns list of (area, x, y, contour).
    """
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
            
        # Aspect ratio of the marker itself
        x, y, w, h = cv2.boundingRect(c)
        aspect = w / float(h) if h > 0 else 0
        # Relaxed aspect ratio for markers (perspective makes squares look like rectangles)
        if not (0.4 <= aspect <= 2.5):
            continue
            
        # Solidity check
        hull = cv2.convexHull(c)
        hull_area = cv2.contourArea(hull)
        if hull_area > 0 and (area / hull_area) > 0.7:
            candidates.append({"area": area, "center": (x + w // 2, y + h // 2), "contour": c})
            
    return candidates


def _get_best_4_markers(candidates: list, img_h: int, img_w: int) -> Optional[np.ndarray]:
    """
    If multiple markers found, pick the 4 that best form a large rectangle.
    """
    if len(candidates) < 4:
        return None
        
    # Sort by area descending
    candidates.sort(key=lambda x: x["area"], reverse=True)
    
    # Try combinations of the top 10 candidates
    import itertools
    best_pts = None
    max_score = -1
    
    top_n = candidates[:min(len(candidates), 10)]
    for quad_indices in itertools.combinations(range(len(top_n)), 4):
        subset = [top_n[i] for i in quad_indices]
        pts = np.array([s["center"] for s in subset], dtype="float32")
        
        if _is_valid_quadrilateral(pts, img_h, img_w):
            # Scoring: Area of combination * Similarity of marker areas
            area = cv2.contourArea(_order_corners(pts).astype(np.int32))
            
            marker_areas = [s["area"] for s in subset]
            area_var = np.std(marker_areas) / (np.mean(marker_areas) + 1e-6)
            
            # Score favors large area and low variance in marker sizes
            score = area * (1.0 / (1.0 + area_var))
            
            if score > max_score:
                max_score = score
                best_pts = pts
                
    return best_pts


def _find_largest_quad(gray: np.ndarray,
                       img_h: int, img_w: int) -> Optional[np.ndarray]:
    """
    Fallback: find the largest 4-sided contour that looks like an OMR sheet.
    Used when corner markers can't be found (e.g. distance capture).
    """
    # Try multiple threshold methods
    methods = []

    # Method 1: Canny edge detection
    edges = cv2.Canny(gray, 30, 120)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    edges = cv2.dilate(edges, kernel, iterations=2)
    methods.append(edges)

    # Method 2: Otsu thresholding
    _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    methods.append(otsu)

    best_quad = None
    best_area = 0

    for binary in methods:
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        for c in contours[:10]:  # Only check the 10 largest
            area = cv2.contourArea(c)
            if area < img_h * img_w * 0.05:
                continue

            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            if len(approx) == 4:
                pts = approx.reshape(4, 2).astype("float32")
                if _is_valid_quadrilateral(pts, img_h, img_w) and area > best_area:
                    best_quad = pts
                    best_area = area

    return best_quad


def detect_paper(blurred_gray: np.ndarray, original_img: np.ndarray) -> Optional[np.ndarray]:
    """Robust multi-strategy paper detection."""
    img_h, img_w = blurred_gray.shape[:2]
    
    # 1. Dynamic area threshold
    # For a 1600px image, marker is usually ~1000px area.
    # At extreme distance, it might be 100px.
    dynamic_min_area = max(60, int((img_w * 0.005) ** 2))
    
    # Strategy A: Adaptive Thresholding
    thresh_adp = cv2.adaptiveThreshold(
        blurred_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 51, 10
    )
    candidates = _find_square_markers(thresh_adp, dynamic_min_area)
    
    best_pts = _get_best_4_markers(candidates, img_h, img_w)
    if best_pts is not None:
        logger.info("detect_paper: Found via Adaptive Markers (count: %d)", len(candidates))
        return _order_corners(best_pts)

    # Strategy B: Otsu Thresholding (better for high contrast)
    _, thresh_otsu = cv2.threshold(blurred_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    candidates_otsu = _find_square_markers(thresh_otsu, dynamic_min_area)
    
    best_pts = _get_best_4_markers(candidates_otsu, img_h, img_w)
    if best_pts is not None:
        logger.info("detect_paper: Found via Otsu Markers (count: %d)", len(candidates_otsu))
        return _order_corners(best_pts)

    # Strategy C: Global Edge Quad Fallback
    logger.info("detect_paper: Falling back to Largest Quad strategy")
    quad = _find_largest_quad(blurred_gray, img_h, img_w)
    if quad is not None:
        return _order_corners(quad)

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


def normalize_warped_size(img: np.ndarray,
                          target_width: int = CANONICAL_WIDTH) -> np.ndarray:
    """
    Resize the warped image so its width is exactly `target_width`, preserving
    aspect ratio.  This guarantees that bubble areas stay in the same pixel
    range regardless of how close or far the camera was when the shot was taken.
    """
    h, w = img.shape[:2]
    if w == target_width:
        return img
    scale = target_width / w
    new_h = int(h * scale)
    resized = cv2.resize(img, (target_width, new_h), interpolation=cv2.INTER_LINEAR)
    logger.info("normalize_warped_size: %dx%d → %dx%d (scale %.2f)",
                w, h, target_width, new_h, scale)
    return resized


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
                  debug_path: str = None) -> Dict:
    # Build per-page debug path if not explicitly provided
    if debug_path is None:
        debug_path = f"last_processed_debug_pg{page_number}.png"

    result = {
        "answers": {}, "roll_number": "EMPTY", "exam_set": "EMPTY",
        "blur_score": 0.0, "bubble_count": 0, "dyn_threshold": 0.22, "error": None,
    }

    try:
        img = decode_image(image_bytes)
        logger.info("Input image: %dx%d", img.shape[1], img.shape[0])

        score, is_blurry = detect_blur(img)
        result["blur_score"] = score
        logger.info("Blur score: %.1f (blurry=%s)", score, is_blurry)

        # Stages
        blurred_gray = normalize_lighting(img)

        corners = detect_paper(blurred_gray, img)
        if corners is not None:
            logger.info("Paper detected — corners: %s", corners.tolist())
            warped = perspective_transform(img, corners)
            logger.info("Warped size (before normalize): %dx%d",
                        warped.shape[1], warped.shape[0])
        else:
            logger.warning("Paper detection FAILED — using full camera frame as fallback")
            # Save a debug image showing what detection saw
            cv2.imwrite("contour_debug.png", img)
            warped = img

        # ── CRITICAL: Normalize to a canonical width ──────────────
        # Without this, images captured from far away produce tiny
        # bubbles that fall below BUBBLE_AREA_MIN and get rejected.
        warped = normalize_warped_size(warped, CANONICAL_WIDTH)
        logger.info("Warped size (after normalize): %dx%d",
                    warped.shape[1], warped.shape[0])

        warped = gamma_correction(warped, GAMMA)
        warped_gray = cv2.cvtColor(warped, cv2.COLOR_BGR2GRAY)
        thresh = dual_threshold(warped_gray)

        cv2.imwrite("thresh_debug.png", thresh)
        cv2.imwrite("warped_debug.png", warped)

        bubbles = detect_bubbles(thresh)
        result["bubble_count"] = len(bubbles)
        logger.info("Bubbles detected: %d", len(bubbles))

        if not bubbles:
            logger.warning("No bubbles detected — returning empty result")
            # Still write debug image for diagnosis
            cv2.imwrite(debug_path, warped)
            return result

        dyn_threshold = _compute_dynamic_threshold([b["f"] for b in bubbles])
        result["dyn_threshold"] = dyn_threshold
        logger.info("Dynamic threshold: %.4f", dyn_threshold)

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
        debug_img = _draw_debug(warped, bubbles, answers, roll, exam_set, dyn_threshold, page_number)
        cv2.imwrite(debug_path, debug_img)
        logger.info("Debug image written to %s", debug_path)

        non_empty = sum(1 for v in answers.values() if v != "EMPTY")
        logger.info("Scan complete: roll=%s set=%s answers=%d/%d non-empty",
                    roll, exam_set, non_empty, len(answers))

    except Exception as e:
        logger.error("scan_omr_page failed: %s", traceback.format_exc())
        result["error"] = str(e)

    return result

