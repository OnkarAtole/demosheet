from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO


# =============================
# Drawing Helpers
# =============================
def draw_bubble(c, x, y, radius=7):
    c.setLineWidth(1.3)
    c.circle(x, y, radius)


def draw_black_square(c, x, y, size=15):
    c.rect(x, y, size, size, fill=1)


def draw_alignment_markers(c, width, height):
    draw_black_square(c, 10, height - 25)
    draw_black_square(c, width - 25, height - 25)
    draw_black_square(c, 10, 10)
    draw_black_square(c, width - 25, 10)


# =============================
# MAIN OMR GENERATOR
# =============================
def generate_pro_omr(exam):

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    total_pages = 1
    is_first_page = True

    # =============================
    # FIRST PAGE HEADER
    # =============================
    draw_alignment_markers(c, width, height)

    c.setFont("Helvetica-Bold", 15)
    c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

    c.setFont("Helvetica", 12)
    c.drawString(60, height - 70, "Name: ____________________________")
    c.drawString(60, height - 95, "Date: ____________________________")

    # Exam Set
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, height - 130, "Exam Set:")

    set_x = 160
    for i in range(1, exam.exam_set + 1):
        c.drawCentredString(set_x, height - 145, str(i))
        draw_bubble(c, set_x, height - 165)
        set_x += 35

    # Roll No
    c.setFont("Helvetica-Bold", 12)
    c.drawString(60, height - 200, "Roll No:")

    col_x = 160
    for _ in range(exam.roll_no_digit):
        y_roll = height - 225
        for num in range(10):
            c.setFont("Helvetica", 9)
            c.drawRightString(col_x - 12, y_roll - 3, str(num))
            draw_bubble(c, col_x, y_roll)
            y_roll -= 20
        col_x += 50

    # =============================
    # QUESTION GRID CONFIG
    # =============================
    left_x = 100
    right_x = width - 250

    first_page_start = height - 430
    next_page_start = height - 120

    bottom_limit = 60
    row_height = 28
    number_width = 25
    bubble_spacing = 35

    current_x = left_x
    y = first_page_start
    q_no = 1

    # =============================
    # DRAW QUESTIONS
    # =============================
    for subject in exam.subjects:

        # Handle subject title placement
        if y < bottom_limit:

            if current_x == left_x:
                current_x = right_x
                y = first_page_start if is_first_page else next_page_start
            else:
                c.showPage()
                total_pages += 1
                draw_alignment_markers(c, width, height)
                is_first_page = False
                current_x = left_x
                y = next_page_start

        # Draw subject title
        c.setFont("Helvetica-Bold", 12)
        c.drawString(current_x, y, f"Subject: {subject.sub_name}")
        y -= 30

        for _ in range(subject.question_count):

            if y < bottom_limit:

                if current_x == left_x:
                    current_x = right_x
                    y = first_page_start if is_first_page else next_page_start
                else:
                    c.showPage()
                    total_pages += 1
                    draw_alignment_markers(c, width, height)
                    is_first_page = False
                    current_x = left_x
                    y = next_page_start

            # Draw question number
            c.setFont("Helvetica", 11)
            c.drawRightString(current_x + number_width, y - 3, str(q_no))

            # Draw bubbles
            bubble_x = current_x + number_width + 20
            for _ in range(4):
                draw_bubble(c, bubble_x, y)
                bubble_x += bubble_spacing

            y -= row_height
            q_no += 1

        y -= 20

    # =============================
    # FINISH
    # =============================
    c.save()
    buffer.seek(0)

    return buffer, total_pages

# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# def draw_bubble(c, x, y, radius=7):
#     c.setLineWidth(1.3)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=15):
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     draw_black_square(c, 10, height - 25)
#     draw_black_square(c, width - 25, height - 25)
#     draw_black_square(c, 10, 10)
#     draw_black_square(c, width - 25, 10)

# def generate_pro_omr(exam):
#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1

#     # ================= FIRST PAGE =================
#     draw_alignment_markers(c, width, height)

#     c.setFont("Helvetica-Bold", 15)
#     c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

#     c.setFont("Helvetica", 12)
#     c.drawString(60, height - 70, "Name: ____________________________")
#     c.drawString(60, height - 95, "Date: ____________________________")

#     c.setFont("Helvetica-Bold", 12)
#     c.drawString(60, height - 130, "Exam Set:")

#     set_x = 160
#     for i in range(1, exam.exam_set + 1):
#         c.drawCentredString(set_x, height - 145, str(i))
#         draw_bubble(c, set_x, height - 165)
#         set_x += 35

#     c.setFont("Helvetica-Bold", 12)
#     c.drawString(60, height - 200, "Roll No:")

#     col_x = 160
#     for _ in range(exam.roll_no_digit):
#         y_roll = height - 225
#         for num in range(10):
#             c.setFont("Helvetica", 9)
#             c.drawRightString(col_x - 12, y_roll - 3, str(num))
#             draw_bubble(c, col_x, y_roll)
#             y_roll -= 20
#         col_x += 50

#     # ================= QUESTION GRID =================
#     left_x = 100
#     right_x = width - 250

#     first_page_start = height - 430
#     next_page_start = height - 120   # No empty space

#     bottom_limit = 70
#     row_height = 28
#     number_width = 25
#     bubble_spacing = 35

#     current_x = left_x
#     y = first_page_start
#     q_no = 1

#     for subject in exam.subjects:

#         # If no space for subject title
#         if y < bottom_limit:
#             if current_x == left_x:
#                 current_x = right_x
#                 y = first_page_start
#             else:
#                 c.showPage()
#                 total_pages += 1
#                 draw_alignment_markers(c, width, height)
#                 current_x = left_x
#                 y = next_page_start   # Start higher on new page

#         c.setFont("Helvetica-Bold", 12)
#         c.drawString(current_x, y, f"Subject: {subject.sub_name}")
#         y -= 30

#         for _ in range(subject.question_count):

#             if y < bottom_limit:
#                 if current_x == left_x:
#                     current_x = right_x
#                     y = first_page_start
#                 else:
#                     c.showPage()
#                     total_pages += 1
#                     draw_alignment_markers(c, width, height)
#                     current_x = left_x
#                     y = next_page_start

#             c.setFont("Helvetica", 11)
#             c.drawRightString(current_x + number_width, y - 3, str(q_no))

#             bubble_x = current_x + number_width + 20
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y)
#                 bubble_x += bubble_spacing

#             y -= row_height
#             q_no += 1

#         y -= 20

#     c.save()
#     buffer.seek(0)

#     return buffer, total_pages

# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# def draw_bubble(c, x, y, radius=7):
#     c.setLineWidth(1.3)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=15):
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     draw_black_square(c, 10, height - 25)
#     draw_black_square(c, width - 25, height - 25)
#     draw_black_square(c, 10, 10)
#     draw_black_square(c, width - 25, 10)


# def generate_pro_omr(exam):
#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4

#     # ===============================
#     # PAGE 1 HEADER
#     # ===============================
#     draw_alignment_markers(c, width, height)

#     c.setFont("Helvetica-Bold", 15)
#     c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

#     c.setFont("Helvetica", 12)
#     c.drawString(60, height - 70, "Name: ____________________________")
#     c.drawString(60, height - 95, "Date: ____________________________")

#     c.setFont("Helvetica-Bold", 12)
#     c.drawString(60, height - 130, "Exam Set:")

#     set_x = 160
#     for i in range(1, exam.exam_set + 1):
#         c.drawCentredString(set_x, height - 145, str(i))
#         draw_bubble(c, set_x, height - 165)
#         set_x += 35

#     c.setFont("Helvetica-Bold", 12)
#     c.drawString(60, height - 200, "Roll No:")

#     col_x = 160
#     for _ in range(exam.roll_no_digit):
#         y_roll = height - 225
#         for num in range(10):
#             c.setFont("Helvetica", 9)
#             c.drawRightString(col_x - 12, y_roll - 3, str(num))
#             draw_bubble(c, col_x, y_roll)
#             y_roll -= 20
#         col_x += 50

#     # ===============================
#     # QUESTION LAYOUT
#     # ===============================
#     left_col_x = 100
#     right_col_x = width - 250

#     first_page_start = height - 430
#     other_page_start = height - 120

#     bottom_limit = 70
#     row_height = 28
#     number_width = 25
#     bubble_spacing = 35

#     current_x = left_col_x
#     y = first_page_start
#     q_no = 1

#     for subject in exam.subjects:

#         # ---- Check before subject title ----
#         if y < bottom_limit:
#             if current_x == left_col_x:
#                 current_x = right_col_x
#                 y = first_page_start
#             else:
#                 c.showPage()
#                 draw_alignment_markers(c, width, height)
#                 current_x = left_col_x
#                 y = other_page_start

#         c.setFont("Helvetica-Bold", 12)
#         c.drawString(current_x, y, f"Subject: {subject.sub_name}")
#         y -= 30

#         for _ in range(subject.question_count):

#             # ---- Check before drawing question ----
#             if y < bottom_limit:
#                 if current_x == left_col_x:
#                     current_x = right_col_x
#                     y = first_page_start if q_no <= 20 else other_page_start
#                 else:
#                     c.showPage()
#                     draw_alignment_markers(c, width, height)
#                     current_x = left_col_x
#                     y = other_page_start

#             c.setFont("Helvetica", 11)
#             c.drawRightString(current_x + number_width, y - 3, str(q_no))

#             bubble_x = current_x + number_width + 20
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y)
#                 bubble_x += bubble_spacing

#             y -= row_height
#             q_no += 1

#         y -= 20

#     c.save()
#     buffer.seek(0)
#     return buffer





# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# # -----------------------------
# # Drawing Helpers
# # -----------------------------
# def draw_bubble(c, x, y, radius=7):
#     c.setLineWidth(1.3)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=15):
#     c.rect(x, y, size, size, fill=1)


# # -----------------------------
# # Main OMR Generator
# # -----------------------------
# def generate_pro_omr(exam):
#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4

#     # -----------------------------
#     # HEADER
#     # -----------------------------
#     def draw_header():
#         draw_black_square(c, 10, height - 25)
#         draw_black_square(c, width - 25, height - 25)
#         draw_black_square(c, 10, 10)
#         draw_black_square(c, width - 25, 10)

#         c.setFont("Helvetica-Bold", 15)
#         c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

#         c.setFont("Helvetica", 12)
#         c.drawString(60, height - 70, "Name: ____________________________")
#         c.drawString(60, height - 95, "Date: ____________________________")

#         # Exam Set
#         c.setFont("Helvetica-Bold", 12)
#         c.drawString(60, height - 130, "Exam Set:")

#         set_x = 160
#         for i in range(1, exam.exam_set + 1):
#             c.setFont("Helvetica", 11)
#             c.drawCentredString(set_x, height - 145, str(i))
#             draw_bubble(c, set_x, height - 165)
#             set_x += 35

#         # Roll No
#         c.setFont("Helvetica-Bold", 12)
#         c.drawString(60, height - 200, "Roll No:")

#         col_x = 160
#         for _ in range(exam.roll_no_digit):
#             y_roll = height - 225
#             for num in range(10):
#                 c.setFont("Helvetica", 9)
#                 c.drawRightString(col_x - 12, y_roll - 3, str(num))
#                 draw_bubble(c, col_x, y_roll)
#                 y_roll -= 20
#             col_x += 50

#     draw_header()

#     # -----------------------------
#     # QUESTION GRID CONFIG
#     # -----------------------------
#     left_col_x = 100
#     right_col_x = width - 250

#     start_y = height - 430
#     bottom_limit = 70

#     row_height = 28
#     number_width = 25
#     bubble_spacing = 35

#     current_x = left_col_x
#     y = start_y
#     q_no = 1

#     # -----------------------------
#     # Draw Questions
#     # -----------------------------
#     for subject in exam.subjects:

#         if y < bottom_limit:
#             if current_x == left_col_x:
#                 current_x = right_col_x
#                 y = start_y
#             else:
#                 c.showPage()
#                 draw_header()
#                 current_x = left_col_x
#                 y = start_y

#         c.setFont("Helvetica-Bold", 12)
#         c.drawString(current_x, y, f"Subject: {subject.sub_name}")
#         y -= 30

#         for _ in range(subject.question_count):

#             if y < bottom_limit:
#                 if current_x == left_col_x:
#                     current_x = right_col_x
#                     y = start_y
#                 else:
#                     c.showPage()
#                     draw_header()
#                     current_x = left_col_x
#                     y = start_y

#             # 🔥 PERFECT TEXT ALIGNMENT (FIXED)
#             c.setFont("Helvetica", 11)
#             c.drawRightString(current_x + number_width, y - 3, str(q_no))

#             # Bubbles
#             bubble_x = current_x + number_width + 20
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y)
#                 bubble_x += bubble_spacing

#             y -= row_height
#             q_no += 1

#         y -= 20

#     c.save()
#     buffer.seek(0)
#     return buffer





