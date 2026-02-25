from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO


def draw_bubble(c, x, y, radius=6):
    c.setLineWidth(1)
    c.circle(x, y, radius)


def draw_black_square(c, x, y, size=18):
    c.setFillColorRGB(0, 0, 0)
    c.rect(x, y, size, size, fill=1)


def draw_alignment_markers(c, width, height):
    draw_black_square(c, 15, height - 35)
    draw_black_square(c, width - 35, height - 35)
    draw_black_square(c, 15, 15)
    draw_black_square(c, width - 35, 15)


def generate_pro_omr(exam):

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    total_pages = 1

    row_height = 16
    bubble_radius = 6

    # ================= FIRST PAGE =================
    draw_alignment_markers(c, width, height)

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 45, f"Exam: {exam.exam_name}")

    c.setFont("Helvetica", 10)
    c.drawString(60, height - 80, "Name: ______________________________")
    c.drawString(60, height - 100, "Date: ______________________________")


# ================= EXAM SET SECTION =================
    set_label_y = height - 145
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, set_label_y, "Exam Set")

    set_start_x = 90
    set_spacing = 24

    for i in range(1, exam.exam_set + 1):
        # Draw set number above bubble
        c.setFont("Helvetica", 9)
        c.drawCentredString(set_start_x, set_label_y - 8, str(i))

        # Draw bubble below number
        draw_bubble(c, set_start_x, set_label_y - 20, bubble_radius)

        set_start_x += set_spacing    

    # ================= ROLL SECTION =================
    roll_label_y = height - 185
    c.setFont("Helvetica-Bold", 11)
    c.drawString(60, roll_label_y, "Roll No")

    digit_spacing = 24
    row_spacing = 18

    roll_x = 70
    roll_start_y = roll_label_y - 50

    for digit_index in range(exam.roll_no_digit):
        x_center = roll_x + digit_index * digit_spacing
        for num in range(10):
            y_center = roll_start_y - num * row_spacing
            c.setFont("Helvetica", 8)
            c.drawRightString(x_center - 10, y_center - 3, str(num))
            draw_bubble(c, x_center, y_center, bubble_radius)

    roll_bottom = roll_start_y - (10 * row_spacing)

    # ================= QUESTION LAYOUT =================
    column_x = [70, 190, 310, 430]
    top_margin = height - 150
    bottom_margin = 50

    q_no = 1
    col_index = 0
    row_index = 0

    for subject in exam.subjects:
        for _ in range(subject.question_count):

            while True:

                # Calculate Y
                if total_pages == 1 and col_index == 0:
                    y = roll_bottom - 20 - (row_index * row_height)
                else:
                    y = top_margin - (row_index * row_height)

                # If bottom reached → move column/page
                if y < bottom_margin:
                    col_index += 1
                    row_index = 0

                    # If columns finished → new page
                    if col_index >= 4:
                        c.showPage()
                        total_pages += 1
                        draw_alignment_markers(c, width, height)
                        col_index = 0

                    continue  # recalc y without skipping question

                break  # valid position found

            x = column_x[col_index]

            if q_no % 5 == 0:
                draw_black_square(c, x - 14, y - 6, 8)

            c.setFont("Helvetica", 8)
            c.drawString(x, y - 3, str(q_no))

            bubble_x = x + 25
            for _ in range(4):
                draw_bubble(c, bubble_x, y, bubble_radius)
                bubble_x += 18

            row_index += 1
            q_no += 1

    c.save()
    buffer.seek(0)

    return buffer, total_pages











# # ##############################################working###########################################################

# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# def draw_bubble(c, x, y, radius=6):
#     c.setLineWidth(1)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=18):
#     c.setFillColorRGB(0, 0, 0)
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     draw_black_square(c, 15, height - 35)
#     draw_black_square(c, width - 35, height - 35)
#     draw_black_square(c, 15, 15)
#     draw_black_square(c, width - 35, 15)


# def generate_pro_omr(exam):

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1

#     row_height = 16
#     bubble_radius = 6

#     # ================= FIRST PAGE DESIGN =================
#     draw_alignment_markers(c, width, height)

#     # HEADER
#     c.setFont("Helvetica-Bold", 14)
#     c.drawCentredString(width / 2, height - 45, f"Exam: {exam.exam_name}")

#     c.setFont("Helvetica", 10)
#     c.drawString(60, height - 80, "Name: ______________________________")
#     c.drawString(60, height - 100, "Date: ______________________________")

#     # ================= ROLL SECTION =================
#     roll_label_y = height - 135
#     c.setFont("Helvetica-Bold", 11)
#     c.drawString(60, roll_label_y, "Roll No")

#     digit_spacing = 32
#     row_spacing = 18

#     roll_x = 70
#     roll_start_y = roll_label_y - 50

#     for digit_index in range(exam.roll_no_digit):
#         x_center = roll_x + digit_index * digit_spacing

#         for num in range(10):
#             y_center = roll_start_y - num * row_spacing

#             c.setFont("Helvetica", 8)
#             c.drawRightString(x_center - 10, y_center - 3, str(num))
#             draw_bubble(c, x_center, y_center, bubble_radius)

#     roll_bottom = roll_start_y - (10 * row_spacing)

#     # ================= QUESTION LAYOUT =================
#     column_x = [70, 190, 310, 430]
#     top_margin = height - 150
#     bottom_margin = 50

#     q_no = 1
#     col_index = 0
#     row_index = 0

#     for subject in exam.subjects:

#         for _ in range(subject.question_count):

#             # First column of first page starts below roll
#             if total_pages == 1 and col_index == 0:
#                 y = roll_bottom - 20 - (row_index * row_height)
#             else:
#                 y = top_margin - (row_index * row_height)

#             x = column_x[col_index]

#             # If bottom reached → move to next column
#             if y < bottom_margin:
#                 col_index += 1
#                 row_index = 0

#                 # If all 4 columns filled → NEW PAGE
#                 if col_index >= 4:
#                     c.showPage()
#                     total_pages += 1

#                     # Only alignment markers on next pages
#                     draw_alignment_markers(c, width, height)

#                     col_index = 0
#                     row_index = 0

#                 continue

#             # Mini square every 5 questions
#             if q_no % 5 == 0:
#                 draw_black_square(c, x - 14, y - 6, 8)

#             c.setFont("Helvetica", 8)
#             c.drawString(x, y - 3, str(q_no))

#             bubble_x = x + 25
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y, bubble_radius)
#                 bubble_x += 18

#             row_index += 1
#             q_no += 1

#     c.save()
#     buffer.seek(0)

#     return buffer, total_pages













# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# def draw_bubble(c, x, y, radius=6):
#     c.setLineWidth(1)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=18):
#     c.setFillColorRGB(0, 0, 0)
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     draw_black_square(c, 15, height - 35)
#     draw_black_square(c, width - 35, height - 35)
#     draw_black_square(c, 15, 15)
#     draw_black_square(c, width - 35, 15)


# def generate_pro_omr(exam):

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1

#     row_height = 16
#     bubble_radius = 6

#     draw_alignment_markers(c, width, height)

#     # ================= HEADER =================
#     c.setFont("Helvetica-Bold", 14)
#     c.drawCentredString(width / 2, height - 45, f"Exam: {exam.exam_name}")

#     c.setFont("Helvetica", 10)
#     c.drawString(60, height - 80, "Name: ______________________________")
#     c.drawString(60, height - 100, "Date: ______________________________")

#     # ================= ROLL SECTION =================
#     roll_label_y = height - 135
#     c.setFont("Helvetica-Bold", 11)
#     c.drawString(60, roll_label_y, "Roll No")

#     digit_spacing = 32
#     row_spacing = 18

#     roll_x = 70
#     roll_start_y = roll_label_y - 50

#     for digit_index in range(exam.roll_no_digit):
#         x_center = roll_x + digit_index * digit_spacing

#         for num in range(10):
#             y_center = roll_start_y - num * row_spacing

#             c.setFont("Helvetica", 8)
#             c.drawRightString(x_center - 10, y_center - 3, str(num))
#             draw_bubble(c, x_center, y_center, bubble_radius)

#     roll_bottom = roll_start_y - (10 * row_spacing)

#     # ================= QUESTION LAYOUT =================

#     column_x = [70, 190, 310, 430]
#     top_margin = height - 150
#     bottom_margin = 50

#     max_rows = int((top_margin - bottom_margin) / row_height)

#     q_no = 1

#     col_index = 0
#     row_index = 0

#     for subject in exam.subjects:

#         for _ in range(subject.question_count):

#             # Column 0 starts BELOW roll
#             if col_index == 0:
#                 y = roll_bottom - 20 - (row_index * row_height)
#             else:
#                 y = top_margin - (row_index * row_height)

#             x = column_x[col_index]

#             # If bottom reached → next column
#             if y < bottom_margin:
#                 col_index += 1
#                 row_index = 0

#                 if col_index >= 4:
#                     break

#                 continue

#             # Mini square every 5
#             if q_no % 5 == 0:
#                 draw_black_square(c, x - 14, y - 6, 8)

#             c.setFont("Helvetica", 8)
#             c.drawString(x, y - 3, str(q_no))

#             bubble_x = x + 18
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y, bubble_radius)
#                 bubble_x += 18

#             row_index += 1
#             q_no += 1

#     c.save()
#     buffer.seek(0)

#     return buffer, total_pages














































# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# # =============================
# # Drawing Helpers
# # =============================
# def draw_bubble(c, x, y, radius=6):
#     c.setLineWidth(1)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=12):
#     c.setFillColorRGB(0, 0, 0)
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     # 4 corner markers (DO NOT REMOVE – needed for scanning)
#     draw_black_square(c, 15, height - 35, 18)
#     draw_black_square(c, width - 35, height - 35, 18)
#     draw_black_square(c, 15, 15, 18)
#     draw_black_square(c, width - 35, 15, 18)


# # =============================
# # MAIN FUNCTION
# # =============================
# def generate_pro_omr(exam):

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1

#     row_height = 16
#     bubble_radius = 6

#     # ================= FIRST PAGE HEADER =================
#     def draw_first_page_header():

#         draw_alignment_markers(c, width, height)

#         c.setFont("Helvetica-Bold", 14)
#         c.drawCentredString(width / 2, height - 45, f"Exam: {exam.exam_name}")

#         c.setFont("Helvetica", 10)
#         c.drawString(60, height - 80, "Name: ______________________________")
#         c.drawString(60, height - 100, "Date: ______________________________")

#         # -------- ROLL NUMBER SECTION --------
#         roll_label_y = height - 135
#         c.setFont("Helvetica-Bold", 11)
#         c.drawString(60, roll_label_y, "Roll No")

#         digit_spacing = 36   # reduced so it doesn't reach right margin
#         row_spacing = 18

#         start_x = 120        # shifted slightly right
#         start_y = roll_label_y - 55  # extra spacing below label

#         # 1️⃣ Empty digit boxes
#         box_size = 16
#         for i in range(exam.roll_no_digit):
#             box_x = start_x + (i * digit_spacing) - (box_size / 2)
#             box_y = roll_label_y - 30
#             c.rect(box_x, box_y, box_size, box_size)

#         # 2️⃣ Roll number bubble grid
#         for digit_index in range(exam.roll_no_digit):

#             x_center = start_x + (digit_index * digit_spacing)

#             for num in range(10):

#                 y_center = start_y - (num * row_spacing)

#                 c.setFont("Helvetica", 8)
#                 c.drawRightString(x_center - 10, y_center - 3, str(num))

#                 draw_bubble(c, x_center, y_center, bubble_radius)

#         # 3️⃣ Border around roll section
#         roll_width = exam.roll_no_digit * digit_spacing + 40
#         roll_height = (10 * row_spacing) + 40

#         c.rect(90,
#                start_y - (10 * row_spacing) - 20,
#                roll_width,
#                roll_height)

#         return start_y - (10 * row_spacing) - 35


#     # ================= OTHER PAGE HEADER =================
#     def draw_other_page_header():
#         draw_alignment_markers(c, width, height)
#         return height - 60


#     # Start first page
#     top_margin = draw_first_page_header()

#     bottom_margin = 50
#     usable_height = top_margin - bottom_margin
#     max_rows_per_column = int(usable_height / row_height)

#     # Keep original UI column spacing
#     column_x = [70, 200, 330, 460]

#     number_gap = 20
#     bubble_spacing = 18

#     q_no = 1
#     col_index = 0
#     row_index = 0

#     for subject in exam.subjects:

#         # SUBJECT TITLE
#         if row_index + 2 >= max_rows_per_column:
#             col_index += 1
#             row_index = 0

#             if col_index >= 4:
#                 c.showPage()
#                 total_pages += 1
#                 top_margin = draw_other_page_header()
#                 usable_height = top_margin - bottom_margin
#                 max_rows_per_column = int(usable_height / row_height)
#                 col_index = 0
#                 row_index = 0

#         x = column_x[col_index]
#         y = top_margin - (row_index * row_height)

#         c.setFont("Helvetica-Bold", 9)
#         c.drawString(x, y, subject.sub_name)
#         c.line(x, y - 2, x + 110, y - 2)

#         row_index += 2

#         # QUESTIONS
#         for _ in range(subject.question_count):

#             if row_index >= max_rows_per_column:
#                 col_index += 1
#                 row_index = 0

#                 if col_index >= 4:
#                     c.showPage()
#                     total_pages += 1
#                     top_margin = draw_other_page_header()
#                     usable_height = top_margin - bottom_margin
#                     max_rows_per_column = int(usable_height / row_height)
#                     col_index = 0
#                     row_index = 0

#             x = column_x[col_index]
#             y = top_margin - (row_index * row_height)

#             # Mini square every 5 questions (but NOT at question 1)
#             if q_no % 5 == 0:
#                 draw_black_square(c, x - 14, y - 5, 8)

#             c.setFont("Helvetica", 8)
#             c.drawString(x, y - 3, str(q_no))

#             bubble_x = x + number_gap
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y, bubble_radius)
#                 bubble_x += bubble_spacing

#             row_index += 1
#             q_no += 1

#     c.save()
#     buffer.seek(0)

#     return buffer, total_pages








# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# # =============================
# # Drawing Helpers
# # =============================
# def draw_bubble(c, x, y, radius=6):
#     c.setLineWidth(1)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=8):
#     c.setFillColorRGB(0, 0, 0)
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     draw_black_square(c, 15, height - 30)
#     draw_black_square(c, width - 30, height - 30)
#     draw_black_square(c, 15, 15)
#     draw_black_square(c, width - 30, 15)


# # =============================
# # MAIN FUNCTION
# # =============================
# def generate_pro_omr(exam):

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1

#     row_height = 16
#     bubble_radius = 6

#     # ================= FIRST PAGE HEADER =================
#     def draw_first_page_header():

#         draw_alignment_markers(c, width, height)

#         c.setFont("Helvetica-Bold", 14)
#         c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

#         c.setFont("Helvetica", 10)
#         c.drawString(60, height - 70, "Name: ______________________________")
#         c.drawString(60, height - 90, "Date: ______________________________")

#         # -------- ROLL NUMBER SECTION --------
#         roll_top = height - 120
#         c.setFont("Helvetica-Bold", 11)
#         c.drawString(60, roll_top, "Roll No")

#         digit_spacing = 45
#         row_spacing = 18

#         start_x = 90
#         start_y = roll_top - 35

#         # 1️⃣ Empty boxes above roll grid
#         box_size = 16
#         for i in range(exam.roll_no_digit):
#             box_x = start_x + (i * digit_spacing) - 8
#             box_y = roll_top - 15
#             c.rect(box_x, box_y, box_size, box_size)

#         # 2️⃣ Roll number grid
#         for digit_index in range(exam.roll_no_digit):

#             x_center = start_x + (digit_index * digit_spacing)

#             for num in range(10):

#                 y_center = start_y - (num * row_spacing)

#                 # Number LEFT aligned to bubble
#                 c.setFont("Helvetica", 8)
#                 c.drawRightString(x_center - 12, y_center - 3, str(num))

#                 # Bubble
#                 draw_bubble(c, x_center, y_center, bubble_radius)

#         # 3️⃣ Separator square at right edge
#         separator_x = start_x + (exam.roll_no_digit * digit_spacing) + 10
#         separator_y = start_y - (4 * row_spacing)
#         draw_black_square(c, separator_x, separator_y, 10)

#         return start_y - (10 * row_spacing) - 30


#     # ================= OTHER PAGE HEADER =================
#     def draw_other_page_header():
#         draw_alignment_markers(c, width, height)
#         return height - 60


#     # Start first page
#     top_margin = draw_first_page_header()

#     bottom_margin = 50
#     usable_height = top_margin - bottom_margin
#     max_rows_per_column = usable_height // row_height

#     column_x = [70, 200, 330, 460]

#     number_gap = 20
#     bubble_spacing = 18

#     q_no = 1
#     col_index = 0
#     row_index = 0

#     for subject in exam.subjects:

#         # SUBJECT TITLE
#         if row_index + 2 >= max_rows_per_column:
#             col_index += 1
#             row_index = 0

#             if col_index >= 4:
#                 c.showPage()
#                 total_pages += 1
#                 top_margin = draw_other_page_header()
#                 usable_height = top_margin - bottom_margin
#                 max_rows_per_column = usable_height // row_height
#                 col_index = 0
#                 row_index = 0

#         x = column_x[col_index]
#         y = top_margin - (row_index * row_height)

#         c.setFont("Helvetica-Bold", 9)
#         c.drawString(x, y, subject.sub_name)
#         c.line(x, y - 2, x + 110, y - 2)

#         row_index += 2

#         # QUESTIONS
#         for _ in range(subject.question_count):

#             if row_index >= max_rows_per_column:
#                 col_index += 1
#                 row_index = 0

#                 if col_index >= 4:
#                     c.showPage()
#                     total_pages += 1
#                     top_margin = draw_other_page_header()
#                     usable_height = top_margin - bottom_margin
#                     max_rows_per_column = usable_height // row_height
#                     col_index = 0
#                     row_index = 0

#             x = column_x[col_index]
#             y = top_margin - (row_index * row_height)

#             if (q_no - 1) % 5 == 0:
#                 draw_black_square(c, x - 14, y - 5, 6)

#             c.setFont("Helvetica", 8)
#             c.drawString(x, y - 3, str(q_no))

#             bubble_x = x + number_gap
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y, bubble_radius)
#                 bubble_x += bubble_spacing

#             row_index += 1
#             q_no += 1

#     c.save()
#     buffer.seek(0)

#     return buffer, total_pages


# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# # =============================
# # Drawing Helpers
# # =============================
# def draw_bubble(c, x, y, radius=6):
#     c.setLineWidth(1)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=8):
#     c.setFillColorRGB(0, 0, 0)
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     draw_black_square(c, 15, height - 30)
#     draw_black_square(c, width - 30, height - 30)
#     draw_black_square(c, 15, 15)
#     draw_black_square(c, width - 30, 15)


# # =============================
# # MAIN FUNCTION
# # =============================
# def generate_pro_omr(exam):

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1

#     row_height = 16
#     bubble_radius = 6

#     # ================= FIRST PAGE HEADER =================
#     def draw_first_page_header():

#         draw_alignment_markers(c, width, height)

#         c.setFont("Helvetica-Bold", 14)
#         c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

#         c.setFont("Helvetica", 10)
#         c.drawString(60, height - 70, "Name: ______________________________")
#         c.drawString(60, height - 90, "Date: ______________________________")

#         # Roll No Section
#         roll_top = height - 120
#         c.setFont("Helvetica-Bold", 11)
#         c.drawString(60, roll_top, "Roll No")

#         col_x = 60
#         max_depth = 0

#         for _ in range(exam.roll_no_digit):

#             y_roll = roll_top - 25
#             depth = 0

#             for num in range(10):
#                 c.setFont("Helvetica", 8)

#                 # Number LEFT of bubble
#                 c.drawRightString(col_x + 12, y_roll + 2, str(num))

#                 # Bubble
#                 draw_bubble(c, col_x + 25, y_roll, 6)

#                 y_roll -= 16
#                 depth += 16

#             max_depth = max(max_depth, depth)
#             col_x += 45   # clean spacing

#         return roll_top - max_depth - 30


#     # ================= OTHER PAGE HEADER =================
#     def draw_other_page_header():
#         draw_alignment_markers(c, width, height)
#         return height - 60


#     # Start first page
#     top_margin = draw_first_page_header()

#     bottom_margin = 50
#     usable_height = top_margin - bottom_margin
#     max_rows_per_column = usable_height // row_height

#     # Fixed 4 clean columns
#     column_x = [70, 200, 330, 460]

#     number_gap = 20
#     bubble_spacing = 18

#     q_no = 1
#     col_index = 0
#     row_index = 0

#     for subject in exam.subjects:

#         # ================= SUBJECT TITLE =================
#         if row_index + 2 >= max_rows_per_column:
#             col_index += 1
#             row_index = 0

#             if col_index >= 4:
#                 c.showPage()
#                 total_pages += 1
#                 top_margin = draw_other_page_header()

#                 usable_height = top_margin - bottom_margin
#                 max_rows_per_column = usable_height // row_height

#                 col_index = 0
#                 row_index = 0

#         x = column_x[col_index]
#         y = top_margin - (row_index * row_height)

#         c.setFont("Helvetica-Bold", 9)
#         c.drawString(x, y, subject.sub_name)
#         c.line(x, y - 2, x + 110, y - 2)

#         row_index += 2

#         # ================= QUESTIONS =================
#         for _ in range(subject.question_count):

#             if row_index >= max_rows_per_column:
#                 col_index += 1
#                 row_index = 0

#                 if col_index >= 4:
#                     c.showPage()
#                     total_pages += 1
#                     top_margin = draw_other_page_header()

#                     usable_height = top_margin - bottom_margin
#                     max_rows_per_column = usable_height // row_height

#                     col_index = 0
#                     row_index = 0

#             x = column_x[col_index]
#             y = top_margin - (row_index * row_height)

#             # Mini square every 5 questions
#             if (q_no - 1) % 5 == 0:
#                 draw_black_square(c, x - 14, y - 5, 6)

#             # Question number
#             c.setFont("Helvetica", 8)
#             c.drawString(x, y - 3, str(q_no))

#             # Bubbles A B C D
#             bubble_x = x + number_gap
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y, bubble_radius)
#                 bubble_x += bubble_spacing

#             row_index += 1
#             q_no += 1

#     c.save()
#     buffer.seek(0)

#     return buffer, total_pages



# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# def draw_bubble(c, x, y, radius=6):
#     c.setLineWidth(1.2)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=8):
#     c.setFillColorRGB(0, 0, 0)
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     draw_black_square(c, 15, height - 30)
#     draw_black_square(c, width - 30, height - 30)
#     draw_black_square(c, 15, 15)
#     draw_black_square(c, width - 30, 15)


# def generate_pro_omr(exam):

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1

#     row_height = 16
#     bubble_radius = 6

#     # ================= FIRST PAGE HEADER =================
#     def draw_first_page_header():
#         draw_alignment_markers(c, width, height)

#         c.setFont("Helvetica-Bold", 14)
#         c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

#         c.setFont("Helvetica", 10)
#         c.drawString(60, height - 70, "Name: ______________________________")
#         c.drawString(60, height - 90, "Date: ______________________________")

#         roll_top = height - 120
#         c.setFont("Helvetica-Bold", 10)
#         c.drawString(60, roll_top, "Roll No")

#         col_x = 60
#         max_depth = 0

#         for _ in range(exam.roll_no_digit):
#             y_roll = roll_top - 20
#             depth = 0
#             for num in range(10):
#                 c.setFont("Helvetica", 7)
#                 c.drawCentredString(col_x + 6, y_roll + 6, str(num))
#                 draw_bubble(c, col_x + 6, y_roll, 5)
#                 y_roll -= 12
#                 depth += 12
#             max_depth = max(max_depth, depth)
#             col_x += 22

#         return roll_top - max_depth - 30


#     # ================= OTHER PAGE HEADER =================
#     def draw_other_page():
#         draw_alignment_markers(c, width, height)
#         return height - 60


#     # Start First Page
#     top_margin = draw_first_page_header()

#     bottom_margin = 50
#     usable_height = top_margin - bottom_margin
#     max_rows_per_column = usable_height // row_height

#     column_x = [70, 200, 330, 460]

#     number_width = 18
#     bubble_gap = 10
#     bubble_spacing = 18

#     q_no = 1
#     col_index = 0
#     row_index = 0

#     for subject in exam.subjects:

#         # ===== SUBJECT TITLE =====
#         if row_index + 2 >= max_rows_per_column:
#             col_index += 1
#             row_index = 0

#             if col_index >= 4:
#                 c.showPage()
#                 total_pages += 1
#                 top_margin = draw_other_page()
#                 usable_height = top_margin - bottom_margin
#                 max_rows_per_column = usable_height // row_height
#                 col_index = 0
#                 row_index = 0

#         x = column_x[col_index]
#         y = top_margin - (row_index * row_height)

#         c.setFont("Helvetica-Bold", 9)
#         c.drawString(x, y, subject.sub_name)
#         c.line(x, y - 2, x + 100, y - 2)

#         row_index += 2

#         # ===== QUESTIONS =====
#         for _ in range(subject.question_count):

#             if row_index >= max_rows_per_column:
#                 col_index += 1
#                 row_index = 0

#                 if col_index >= 4:
#                     c.showPage()
#                     total_pages += 1
#                     top_margin = draw_other_page()
#                     usable_height = top_margin - bottom_margin
#                     max_rows_per_column = usable_height // row_height
#                     col_index = 0

#             x = column_x[col_index]
#             y = top_margin - (row_index * row_height)

#             if (q_no - 1) % 5 == 0:
#                 draw_black_square(c, x - 12, y - 5, 6)

#             c.setFont("Helvetica", 8)
#             c.drawString(x, y - 3, str(q_no))

#             bubble_x = x + number_width + bubble_gap
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y, bubble_radius)
#                 bubble_x += bubble_spacing

#             row_index += 1
#             q_no += 1

#     c.save()
#     buffer.seek(0)

#     return buffer, total_pages






# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# # =============================
# # Drawing Helpers
# # =============================
# def draw_bubble(c, x, y, radius=6):
#     c.setLineWidth(1.2)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=10):
#     c.setFillColorRGB(0, 0, 0)
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     draw_black_square(c, 15, height - 30)
#     draw_black_square(c, width - 30, height - 30)
#     draw_black_square(c, 15, 15)
#     draw_black_square(c, width - 30, 15)


# # =============================
# # MAIN OMR GENERATOR
# # =============================
# def generate_pro_omr(exam):

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1

#     QUESTIONS_PER_PAGE = 130
#     row_height = 16
#     bubble_radius = 6

#     # ================= HEADER =================
#     def draw_header(include_roll=True):
#         draw_alignment_markers(c, width, height)

#         c.setFont("Helvetica-Bold", 14)
#         c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

#         c.setFont("Helvetica", 10)
#         c.drawString(60, height - 70, "Name: ______________________________")
#         c.drawString(60, height - 90, "Date: ______________________________")

#         if include_roll:
#             roll_top = height - 120
#             c.setFont("Helvetica-Bold", 10)
#             c.drawString(60, roll_top, "Roll No")

#             col_x = 60
#             max_depth = 0

#             for _ in range(exam.roll_no_digit):
#                 y_roll = roll_top - 20
#                 depth = 0
#                 for num in range(10):
#                     c.setFont("Helvetica", 7)
#                     c.drawCentredString(col_x + 7, y_roll + 7, str(num))
#                     draw_bubble(c, col_x + 7, y_roll, 5)
#                     y_roll -= 13
#                     depth += 13
#                 max_depth = max(max_depth, depth)
#                 col_x += 22

#             return roll_top - max_depth - 25  # Return start Y for questions

#         return height - 80


#     # First Page Header
#     top_margin = draw_header(include_roll=True)

#     bottom_margin = 50
#     usable_height = top_margin - bottom_margin
#     max_rows_per_column = usable_height // row_height

#     # ===== FIXED COLUMN POSITIONS (NO FLOATING WIDTH) =====
#     column_x = [70, 200, 330, 460]

#     number_width = 18
#     bubble_gap = 10
#     bubble_spacing = 18

#     q_no = 1
#     questions_on_page = 0
#     col_index = 0
#     row_index = 0

#     for subject in exam.subjects:

#         for _ in range(subject.question_count):

#             # ================= NEW PAGE AFTER 130 =================
#             if questions_on_page >= QUESTIONS_PER_PAGE:
#                 c.showPage()
#                 total_pages += 1
#                 top_margin = draw_header(include_roll=False)

#                 usable_height = top_margin - bottom_margin
#                 max_rows_per_column = usable_height // row_height

#                 col_index = 0
#                 row_index = 0
#                 questions_on_page = 0

#             # ================= NEW COLUMN =================
#             if row_index >= max_rows_per_column:
#                 col_index += 1
#                 row_index = 0

#                 if col_index >= 4:
#                     c.showPage()
#                     total_pages += 1
#                     top_margin = draw_header(include_roll=False)
#                     col_index = 0

#             x = column_x[col_index]
#             y = top_margin - (row_index * row_height)

#             # ===== Mini square every 5 questions =====
#             if (q_no - 1) % 5 == 0:
#                 draw_black_square(c, x - 15, y - 5, 6)

#             # ===== Question Number (LEFT FIXED ALIGNMENT) =====
#             c.setFont("Helvetica", 8)
#             c.drawString(x, y - 3, str(q_no))

#             # ===== Bubbles A B C D =====
#             bubble_x = x + number_width + bubble_gap
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y, bubble_radius)
#                 bubble_x += bubble_spacing

#             row_index += 1
#             q_no += 1
#             questions_on_page += 1

#     c.save()
#     buffer.seek(0)

#     return buffer, total_pages



# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# def draw_bubble(c, x, y, radius=6):
#     c.setLineWidth(1.2)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=14):
#     c.setFillColorRGB(0, 0, 0)
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     draw_black_square(c, 15, height - 30)
#     draw_black_square(c, width - 30, height - 30)
#     draw_black_square(c, 15, 15)
#     draw_black_square(c, width - 30, 15)


# def generate_pro_omr(exam):

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1

#     QUESTIONS_PER_PAGE = 130
#     row_height = 15

#     # ================= HEADER =================
#     draw_alignment_markers(c, width, height)

#     c.setFont("Helvetica-Bold", 14)
#     c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

#     c.setFont("Helvetica", 10)
#     c.drawString(60, height - 70, "Name: ____________________")
#     c.drawString(60, height - 90, "Date: ____________________")

#     # ===== Roll Number Grid =====
#     roll_top = height - 120
#     c.setFont("Helvetica-Bold", 10)
#     c.drawString(60, roll_top, "Roll No")

#     col_x = 60
#     max_roll_depth = 0

#     for _ in range(exam.roll_no_digit):
#         y_roll = roll_top - 20
#         depth = 0
#         for num in range(10):
#             c.setFont("Helvetica", 7)
#             c.drawCentredString(col_x + 7, y_roll + 8, str(num))
#             draw_bubble(c, col_x + 7, y_roll)
#             y_roll -= 13
#             depth += 13
#         max_roll_depth = max(max_roll_depth, depth)
#         col_x += 22

#     # 🔥 START QUESTIONS AFTER ROLL SECTION
#     top_margin = roll_top - max_roll_depth - 20
#     bottom_margin = 50

#     usable_height = top_margin - bottom_margin
#     max_rows_per_column = int(usable_height / row_height)

#     # Equal 4 column spacing
#     left_margin = 60
#     right_margin = 40
#     usable_width = width - left_margin - right_margin
#     column_width = usable_width / 4

#     column_x = [
#         left_margin + (i * column_width)
#         for i in range(4)
#     ]

#     number_offset = 15
#     bubble_spacing = 14

#     q_no = 1
#     questions_on_page = 0
#     col_index = 0
#     row_index = 0

#     for subject in exam.subjects:

#         for _ in range(subject.question_count):

#             # NEW PAGE AFTER 130 QUESTIONS
#             if questions_on_page >= QUESTIONS_PER_PAGE:
#                 c.showPage()
#                 total_pages += 1
#                 draw_alignment_markers(c, width, height)

#                 top_margin = height - 80
#                 usable_height = top_margin - bottom_margin
#                 max_rows_per_column = int(usable_height / row_height)

#                 col_index = 0
#                 row_index = 0
#                 questions_on_page = 0

#             # NEW COLUMN
#             if row_index >= max_rows_per_column:
#                 col_index += 1
#                 row_index = 0

#                 if col_index >= 4:
#                     c.showPage()
#                     total_pages += 1
#                     draw_alignment_markers(c, width, height)

#                     col_index = 0

#             x = column_x[col_index]
#             y = top_margin - (row_index * row_height)

#             # Mini square every 5 questions
#             if q_no % 5 == 1:
#                 draw_black_square(c, x - 10, y - 4, 7)

#             # Question number
#             c.setFont("Helvetica", 7)
#             c.drawRightString(x + number_offset, y + 3, str(q_no))

#             # Bubbles
#             bubble_x = x + number_offset + 5
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y)
#                 bubble_x += bubble_spacing

#             row_index += 1
#             q_no += 1
#             questions_on_page += 1

#     c.save()
#     buffer.seek(0)

#     return buffer, total_pages





# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# def draw_bubble(c, x, y, radius=6):
#     c.setLineWidth(1.2)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=14):
#     c.setFillColorRGB(0, 0, 0)
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     draw_black_square(c, 15, height - 30)
#     draw_black_square(c, width - 30, height - 30)
#     draw_black_square(c, 15, 15)
#     draw_black_square(c, width - 30, 15)


# def generate_pro_omr(exam):

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1

#     QUESTIONS_PER_PAGE = 130
#     row_height = 16

#     # ================= HEADER =================
#     def draw_header():
#         draw_alignment_markers(c, width, height)

#         c.setFont("Helvetica-Bold", 14)
#         c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

#         c.setFont("Helvetica", 10)
#         c.drawString(60, height - 70, "Name: ____________________")
#         c.drawString(60, height - 90, "Date: ____________________")

#     draw_header()

#     # ================= GRID SETTINGS =================
#     top_margin = height - 120
#     bottom_margin = 60

#     usable_height = top_margin - bottom_margin
#     max_rows_per_column = int(usable_height / row_height)

#     column_x = [60, 190, 320, 450]
#     number_offset = 16
#     bubble_spacing = 16

#     q_no = 1
#     questions_on_page = 0

#     col_index = 0
#     row_index = 0

#     for subject in exam.subjects:

#         for _ in range(subject.question_count):

#             # NEW PAGE
#             if questions_on_page >= QUESTIONS_PER_PAGE:
#                 c.showPage()
#                 total_pages += 1
#                 draw_alignment_markers(c, width, height)

#                 col_index = 0
#                 row_index = 0
#                 questions_on_page = 0

#             # NEW COLUMN
#             if row_index >= max_rows_per_column:
#                 col_index += 1
#                 row_index = 0

#                 if col_index >= 4:
#                     c.showPage()
#                     total_pages += 1
#                     draw_alignment_markers(c, width, height)
#                     col_index = 0

#             x = column_x[col_index]
#             y = top_margin - (row_index * row_height)

#             # Mini block markers every 5 questions
#             if q_no % 5 == 1:
#                 draw_black_square(c, x - 18, y - 5, 8)

#             # Question number
#             c.setFont("Helvetica", 7)
#             c.drawRightString(x + number_offset, y + 3, str(q_no))

#             # Bubbles
#             bubble_x = x + number_offset + 6
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y)
#                 bubble_x += bubble_spacing

#             row_index += 1
#             q_no += 1
#             questions_on_page += 1

#     c.save()
#     buffer.seek(0)
#     return buffer, total_pages









# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# # =============================
# # Drawing Helpers
# # =============================
# def draw_bubble(c, x, y, radius=6):
#     c.setLineWidth(1.2)
#     c.circle(x, y, radius)


# def draw_black_square(c, x, y, size=16):
#     c.setFillColorRGB(0, 0, 0)
#     c.rect(x, y, size, size, fill=1)


# def draw_alignment_markers(c, width, height):
#     draw_black_square(c, 15, height - 30)
#     draw_black_square(c, width - 30, height - 30)
#     draw_black_square(c, 15, 15)
#     draw_black_square(c, width - 30, 15)


# # =============================
# # MAIN GENERATOR
# # =============================
# def generate_pro_omr(exam):

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1

#     QUESTIONS_PER_PAGE = 130
#     q_no = 1
#     questions_on_page = 0

#     # =============================
#     # HEADER (ONLY FIRST PAGE)
#     # =============================
#     draw_alignment_markers(c, width, height)

#     c.setFont("Helvetica-Bold", 14)
#     c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

#     c.setFont("Helvetica", 11)
#     c.drawString(60, height - 70, "Name: ____________________________")
#     c.drawString(60, height - 90, "Date: ____________________________")

#     # Roll Number Grid (Compact Like Image)
#     c.setFont("Helvetica-Bold", 11)
#     c.drawString(60, height - 120, "Roll No")

#     col_x = 60
#     for _ in range(exam.roll_no_digit):
#         y_roll = height - 140
#         for num in range(10):
#             c.setFont("Helvetica", 8)
#             c.drawCentredString(col_x + 8, y_roll + 12, str(num))
#             draw_bubble(c, col_x + 8, y_roll)
#             y_roll -= 15
#         col_x += 25

#     # =============================
#     # QUESTION GRID SETTINGS
#     # =============================
#     column_positions = [60, 200, 340, 480]  # 4 compact columns
#     start_y = height - 300
#     bottom_limit = 50
#     row_height = 16
#     number_offset = 18
#     bubble_spacing = 18

#     col_index = 0
#     y = start_y

#     # =============================
#     # DRAW QUESTIONS
#     # =============================
#     for subject in exam.subjects:

#         for _ in range(subject.question_count):

#             # Move to next page if 130 reached
#             if questions_on_page >= QUESTIONS_PER_PAGE:
#                 c.showPage()
#                 total_pages += 1
#                 draw_alignment_markers(c, width, height)

#                 col_index = 0
#                 y = height - 80
#                 questions_on_page = 0

#             # Move to next column
#             if y < bottom_limit:
#                 col_index += 1
#                 y = start_y

#                 if col_index >= 4:
#                     c.showPage()
#                     total_pages += 1
#                     draw_alignment_markers(c, width, height)
#                     col_index = 0
#                     y = height - 80
#                     questions_on_page = 0

#             x = column_positions[col_index]

#             # Draw small black square marker beside blocks
#             if q_no % 5 == 1:
#                 draw_black_square(c, x - 20, y - 5, 8)

#             # Draw question number
#             c.setFont("Helvetica", 8)
#             c.drawRightString(x + number_offset, y + 3, str(q_no))

#             # Draw A B C D bubbles
#             bubble_x = x + number_offset + 8
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y)
#                 bubble_x += bubble_spacing

#             y -= row_height
#             q_no += 1
#             questions_on_page += 1

#     c.save()
#     buffer.seek(0)

#     return buffer, total_pages

































# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from io import BytesIO


# # =============================
# # Drawing Helpers
# # =============================
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


# # =============================
# # MAIN OMR GENERATOR
# # =============================
# def generate_pro_omr(exam):

#     buffer = BytesIO()
#     c = canvas.Canvas(buffer, pagesize=A4)

#     width, height = A4
#     total_pages = 1
#     is_first_page = True

#     # =============================
#     # FIRST PAGE HEADER
#     # =============================
#     draw_alignment_markers(c, width, height)

#     c.setFont("Helvetica-Bold", 15)
#     c.drawCentredString(width / 2, height - 40, f"Exam: {exam.exam_name}")

#     c.setFont("Helvetica", 12)
#     c.drawString(60, height - 70, "Name: ____________________________")
#     c.drawString(60, height - 95, "Date: ____________________________")

#     # Exam Set
#     c.setFont("Helvetica-Bold", 12)
#     c.drawString(60, height - 130, "Exam Set:")

#     set_x = 160
#     for i in range(1, exam.exam_set + 1):
#         c.drawCentredString(set_x, height - 145, str(i))
#         draw_bubble(c, set_x, height - 165)
#         set_x += 35

#     # Roll No
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

#     # =============================
#     # QUESTION GRID CONFIG
#     # =============================
#     left_x = 100
#     right_x = width - 250

#     first_page_start = height - 430
#     next_page_start = height - 120

#     bottom_limit = 60
#     row_height = 28
#     number_width = 25
#     bubble_spacing = 35

#     current_x = left_x
#     y = first_page_start
#     q_no = 1

#     # =============================
#     # DRAW QUESTIONS
#     # =============================
#     for subject in exam.subjects:

#         # Handle subject title placement
#         if y < bottom_limit:

#             if current_x == left_x:
#                 current_x = right_x
#                 y = first_page_start if is_first_page else next_page_start
#             else:
#                 c.showPage()
#                 total_pages += 1
#                 draw_alignment_markers(c, width, height)
#                 is_first_page = False
#                 current_x = left_x
#                 y = next_page_start

#         # Draw subject title
#         c.setFont("Helvetica-Bold", 12)
#         c.drawString(current_x, y, f"Subject: {subject.sub_name}")
#         y -= 30

#         for _ in range(subject.question_count):

#             if y < bottom_limit:

#                 if current_x == left_x:
#                     current_x = right_x
#                     y = first_page_start if is_first_page else next_page_start
#                 else:
#                     c.showPage()
#                     total_pages += 1
#                     draw_alignment_markers(c, width, height)
#                     is_first_page = False
#                     current_x = left_x
#                     y = next_page_start

#             # Draw question number
#             c.setFont("Helvetica", 11)
#             c.drawRightString(current_x + number_width, y - 3, str(q_no))

#             # Draw bubbles
#             bubble_x = current_x + number_width + 20
#             for _ in range(4):
#                 draw_bubble(c, bubble_x, y)
#                 bubble_x += bubble_spacing

#             y -= row_height
#             q_no += 1

#         y -= 20

#     # =============================
#     # FINISH
#     # =============================
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