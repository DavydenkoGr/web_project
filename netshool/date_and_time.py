'''
В этом файле перечислены основные функции для работы со временем
'''
import datetime


def get_year():
    now = datetime.datetime.now()
    if now.month < 7:
        now -= datetime.timedelta(days=365)
    return now.year


def first_september():
    # Попытаемся разобраться со школьным календарем
    # Для этого нам необходимо узнать день недели на 1 сентября, начиная с 0
    year = get_year()
    return datetime.date(year, 9, 1).weekday()


def holidays():
    # Функция возвращает выходные дни в формате номер недели/день недели начиная с 0
    lines = open('static/holidays.txt').readlines()
    year = get_year()
    res = list()
    for i in lines:
        day, month = i.split('.')
        if not (int(month) in range(8, 13)):
            year += 1
        now = datetime.date(year, int(month), int(day))
        weekday = now.weekday()
        for i in week_list:
            f_d, s_d = i.split('/')[1].split('-')
            f_d, s_d = f_d.split('.'), s_d.split('.')
            if datetime.date(int(f_d[2]), int(f_d[1]), int(f_d[0])) <= now and \
                    datetime.date(int(s_d[2]), int(s_d[1]), int(s_d[0])) >= now:
                res.append(f"{i.split('/')[0]}/{weekday}")
        if not (int(month) in range(8, 13)):
            year -= 1
    return res


def create_week_list(first_day):
    # Возвратим список недель для убобной работы с дневником
    year = get_year()
    res = list()
    if first_day == 0:
        first_date = datetime.date(year, 9, 1)
    elif first_day == 6:
        first_date = datetime.date(year, 9, 2)
    else:
        first_date = datetime.date(year, 8, 32 - first_day)
    a = datetime.date(year, first_date.month, first_date.day)
    for i in range(53):
        b = datetime.timedelta(days=7)
        # Номер недели/первый день неди-последний день недели, включая воскресенье
        res.append(f"{i + 1}/{a.day}.{a.month}.{a.year}-"
                   f"{(a + b).day}.{(a + b).month}.{(a + b).year}")
        a = a + b
    return res


def to_now_week():
    # Функция возвращает номер ближайшей учебной недели
    now = datetime.datetime.now()
    now = datetime.date(now.year, now.month, now.day)
    if now.month in range(6, 8):
        return '53'
    elif now.month == 8:
        return '1'
    else:
        for i in week_list:
            f_d, s_d = i.split('/')[1].split('-')
            f_d, s_d = f_d.split('.'), s_d.split('.')
            if datetime.date(int(f_d[2]), int(f_d[1]), int(f_d[0])) <= now and \
                    datetime.date(int(s_d[2]), int(s_d[1]), int(s_d[0])) >= now:
                return i.split('/')[0]
    return '1'


week_list = create_week_list(first_september())
holidays = holidays()