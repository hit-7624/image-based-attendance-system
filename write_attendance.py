import openpyxl
import os

def initialize_sheet_if_needed(path):
    if not os.path.exists(path):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Sheet1"
        ws.cell(row=1, column=1, value="Roll Number")
        for i in range(1, 101):
            ws.cell(row=i+1, column=1, value=i)
        wb.save(path)

def mark_attendance(path, roll_numbers, date_str):
    initialize_sheet_if_needed(path)
    wb = openpyxl.load_workbook(path)
    ws = wb.active

    # Check if date column exists
    date_column = None
    for col in range(2, ws.max_column + 1):
        if ws.cell(row=1, column=col).value == date_str:
            date_column = col
            break

    # If not found, add new column
    if not date_column:
        date_column = ws.max_column + 1
        ws.cell(row=1, column=date_column, value=date_str)

    # Mark 'P' for present roll numbers and 'A' for absent
    for row in range(2, ws.max_row + 1):
        roll_no = ws.cell(row=row, column=1).value
        if str(roll_no) in roll_numbers:
            ws.cell(row=row, column=date_column, value='P')
        else:
            ws.cell(row=row, column=date_column, value='A')

    wb.save(path)