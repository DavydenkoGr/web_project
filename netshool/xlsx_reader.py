def get_class_schedule(number, letter):
    import openpyxl
    wb = openpyxl.load_workbook("static/school_schedule.xlsx")
    sheet = wb.get_sheet_by_name(f"{number} класс")
    n = ['А', 'Б', 'В', 'Г'].index(letter)
    table = []
    for i in range(7 * n + 1, 7 * (n + 1)):
        row = []
        for j in range(2, 8):
            value = sheet.cell(row=i, column=j).value
            if not value:
                break
            row.append(value)
        if row:
            table.append(row)
    return table
