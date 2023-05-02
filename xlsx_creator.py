import xlsxwriter
from constants import SUBJECT_DICT


def create_base_schedule():
    """
    additional function, which helps build base schedule using SUBJECT_DICT constant and mixing its content
    notice:
     1) students can`t have more than 6 subjects per day
     2) you can`t add subjects, which isn`t specified in the subject table
    """
    workbook = xlsxwriter.Workbook('static/school_schedule.xlsx')
    for t in range(1, 12):
        worksheet = workbook.add_worksheet(f"{t} класс")
        data = SUBJECT_DICT[t]
        for i in range(4):
            for k, daily_schedule in enumerate(data):
                row = i * 7 + k
                # Перемешиваем расписание для разных классов
                # Если в день есть пара уроков, обычно их ставят подряд,
                # потому сдвигаем для Б класса порядок уроков на 2
                if i == 1:
                    daily_schedule = daily_schedule[-2:] + daily_schedule[:-2]
                # Для В класса сдвинем уроки на 1 день
                elif i == 2:
                    daily_schedule = data[(k + 1) % len(data)]
                # Для Г класса также как для В, только сдвигаем на 2
                elif i == 3:
                    daily_schedule = data[(k + 1) % len(data)]
                    daily_schedule = daily_schedule[-2:] + daily_schedule[:-2]
                # Таким образом, учитель сможет вести хотя бы у 2-х классов в параллели
                worksheet.write(row, 0,
                                ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота'][k])
                for j in range(len(daily_schedule)):
                    if not daily_schedule[j]:
                        break
                    worksheet.write(row, j + 1, daily_schedule[j])

    workbook.close()
