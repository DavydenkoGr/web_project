from datetime import datetime, timedelta, date


def get_year():
    """return current year"""
    now = datetime.now()
    if now.month < 7:
        now -= timedelta(days=365)
    return now.year


def first_september():
    """return first september date"""
    year = get_year()
    return date(year, 9, 1).weekday()


def holidays():
    """return holidays list in format week_number/weekday (starting from 0)"""
    lines = open('static/holidays.txt').readlines()
    year = get_year()
    res = list()
    for i in lines:
        day, month = i.split('.')
        if not (int(month) in range(8, 13)):
            year += 1
        now = date(year, int(month), int(day))
        weekday = now.weekday()
        for j in week_list:
            first_day, last_day = j.split('/')[1].split('-')
            first_day, last_day = first_day.split('.'), last_day.split('.')
            if date(int(first_day[2]), int(first_day[1]), int(first_day[0])) <= now \
                    <= date(int(last_day[2]), int(last_day[1]), int(last_day[0])):
                res.append([int(j.split('/')[0]), weekday])
        if not (int(month) in range(8, 13)):
            year -= 1
    return res


def create_week_list(first_day):
    """return week list for convenient work with diary"""
    year = get_year()
    res = list()
    if first_day == 0:
        first_date = date(year, 9, 1)
    elif first_day == 6:
        first_date = date(year, 9, 2)
    else:
        first_date = date(year, 8, 32 - first_day)
    a = date(year, first_date.month, first_date.day)
    for i in range(40):
        b = timedelta(days=6)
        # Номер недели/первый день недели-последний день недели, включая воскресенье
        res.append(f"{i + 1}/{a.day}.{a.month}.{a.year}-"
                   f"{(a + b).day}.{(a + b).month}.{(a + b).year}")
        a = a + b + timedelta(days=1)
    return res


def to_now_week():
    """return the next school week, it helps the user to find his schedule"""
    now = datetime.now()
    now = date(now.year, now.month, now.day)
    if now.month in range(6, 8):
        return '40'
    elif now.month == 8:
        return '1'
    else:
        for i in week_list:
            first_day, last_day = i.split('/')[1].split('-')
            first_day, last_day = first_day.split('.'), last_day.split('.')
            if date(int(first_day[2]), int(first_day[1]), int(first_day[0])) <= now \
                    <= date(int(last_day[2]), int(last_day[1]), int(last_day[0])):
                return i.split('/')[0]
    return '1'


week_list = create_week_list(first_september())
holidays = holidays()
