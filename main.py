from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api
import sqlalchemy
from wtforms import SelectField, FieldList
import os
from data import db_session
from data.mark import Marks
from data.school_class import SchoolClass
from data.student import Student
from data.subject import Subject
from data.teacher import Teacher
from data.homework import Homework
from forms.registration import RegisterStudentForm, RegisterTeacherForm, LoginForm
from forms.set_marks import MarksSettingForm
from forms.settings import SettingsForm
from xlsx_reader import get_class_schedule
from date_and_time import to_now_week, week_list, holidays

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'davydenkogrigory_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    if db_sess.query(Teacher).get(user_id):
        return db_sess.query(Teacher).get(user_id)
    elif db_sess.query(Student).get(user_id):
        return db_sess.query(Student).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    if current_user.is_authenticated:
        background_color = current_user.background_color
        if current_user.__class__ == Teacher:
            diary_link = f"/teacherdiary/{to_now_week()}"
            report_link = "/"
        else:
            diary_link = f"/studentdiary/{to_now_week()}"
            report_link = "/studentreport/1"
    else:
        background_color = 0
        diary_link = "/"
        report_link = "/"
    return render_template("index.html", title='Объявления', dont_add_container=True,
                           diary_link=diary_link, report_link=report_link,
                           background_color=["#D1B280", "#C292FA", "#7AB996"][background_color],
                           current_page=1)


@app.route("/studentreport/<int:semester>")
@login_required
def report(semester):
    if current_user.__class__ != Student:
        return redirect('/')
    # Отчёты показываются по полугодиям
    # Учитель смотреть отчёты не может !!!!!
    if semester not in range(1, 3):
        return redirect(f"/studentdiary/{to_now_week()}")
    db_sess = db_session.create_session()
    # Для того чтобы не вывелись те уроки, которых у ученика нет, пройдёмся по урокам данного класса
    school_class = db_sess.query(SchoolClass).filter(SchoolClass.id == current_user.school_class_id
                                                     ).first()
    table = list()
    for subject in school_class.subjects:
        marks = db_sess.query(Marks).filter(Marks.student_id == current_user.id,
                                            Marks.subject_id == subject.id).first()
        # [предмет, кол-во 5, 4, 3, 2, средний балл]
        s = [subject.name, 0, 0, 0, 0, 0]
        if not marks or not marks.marks:
            table.append(s)
            continue
        marks_list = marks.marks.split()
        for mark in marks_list:
            if semester == 2 and int(mark.split('/')[0]) > 19 or\
                    semester == 1 and int(mark.split('/')[0]) < 19:
                s[6 - int(mark.split('/')[-1])] += 1
        if s[1] + s[2] + s[3] + s[4] == 0:
            table.append(s)
            continue
        # Нарисуем красивое среднее арифметическое
        s[-1] = str(round(((5 * s[1] + 4 * s[2] + 3 * s[3] + 2 * s[4]) / (s[1] + s[2] + s[3] + s[4])), 2))
        s[-1] = ','.join(s[-1].split('.'))
        if len(s[-1]) == 3:
            s[-1] += '0'
        table.append(s)
    total = [sum(table[i][j] for i in range(len(table))) for j in range(1, 5)]
    return render_template("report.html", title='Отчёты', dont_add_container=True, current_page=2,
                           diary_link=f"/studentdiary/{to_now_week()}",
                           background_color=["#D1B280", "#C292FA", "#7AB996"][current_user.background_color],
                           table=table, total=total, semester=semester)


@app.route("/studentdiary/<int:week>")
@login_required
def studentdiary(week):
    if current_user.__class__ != Student:
        return redirect('/')
    if week not in range(1, 41):
        return redirect(f"/studentdiary/{to_now_week()}")
    db_sess = db_session.create_session()
    school_class = db_sess.query(SchoolClass).filter(current_user.school_class_id == SchoolClass.id
                                                     ).first()
    table = get_class_schedule(school_class.number, school_class.letter)

    # Выберем среди оценок ученика оценки на эту неделю
    mark_table = [['' for _ in range(6)] for _ in range(6)]
    all_student_marks = db_sess.query(Marks).filter(Marks.student_id == current_user.id).all()
    for subject_marks in all_student_marks:
        sm = subject_marks.marks.split()
        for mark in sm:
            mark_week, weekday, lesson_number, mark = list(map(int, mark.split('/')))
            if mark_week == week:
                mark_table[weekday][lesson_number - 1] = mark
    # Заполнение таблицы с домашними заданиями
    homework_table = [['' for _ in range(6)] for _ in range(6)]
    for i in range(len(table)):
        for j in range(len(table[i])):
            subject = db_sess.query(Subject).filter(Subject.name == table[i][j]
                                                    ).first()
            homework = db_sess.query(Homework).filter(Homework.subject_id == subject.id,
                                                      Homework.class_id == school_class.id,
                                                      Homework.date_info ==
                                                      f"{week}/{i}/{j + 1}"
                                                      ).first()
            if homework:
                homework_table[i][j] = homework.task

    return render_template("studentdiary.html", title='Электронный дневник', current_page=3,
                           dont_add_container=True, table=table,
                           diary_link=f"/studentdiary/{to_now_week()}", report_link="/studentreport/1",
                           background_color=["#D1B280", "#C292FA", "#7AB996"][current_user.background_color],
                           sizes=[len(table), [len(table[i]) for i in range(len(table))]],
                           week=week, week_list=week_list, holidays=holidays, mark_table=mark_table,
                           homework_table=homework_table)


@app.route("/teacherdiary/<int:week>")
@login_required
def teacherdiary(week):
    if current_user.__class__ != Teacher:
        return redirect('/')
    if week not in range(1, 41):
        return redirect(f"/teacherdiary/{to_now_week()}")
    db_sess = db_session.create_session()
    # Создадим все необходимые таблички для работы с дневником
    teacher_schedule = [[[None for _ in range(6)] for _ in range(6)] for _ in range(2)]
    id_table = [[[None for _ in range(6)] for _ in range(6)] for _ in range(2)]
    homework_table = [[['' for _ in range(6)] for _ in range(6)] for _ in range(2)]
    subject = db_sess.query(Subject).filter(Subject.id == current_user.subject_id
                                            ).first()
    teacher = db_sess.query(Teacher).filter(Teacher.id == current_user.id).first()
    # Заполняем таблицы
    for school_class in teacher.school_classes:
        table = get_class_schedule(school_class.number, school_class.letter)
        for i in range(len(table)):
            for j in range(len(table[i])):
                if table[i][j] == subject.name:
                    teacher_schedule[(school_class.number + 1) % 2][i][j] = \
                        f"{school_class.number} {school_class.letter}"
                    id_table[(school_class.number + 1) % 2][i][j] = school_class.id
                    # Если этот класс имеет урок в этот день, возможно у него есть домашнее задание
                    homework = db_sess.query(Homework).filter(Homework.subject_id == subject.id,
                                                              Homework.class_id == school_class.id,
                                                              Homework.date_info ==
                                                              f"{week}/{i}/{j + 1}"
                                                              ).first()
                    if homework:
                        homework_table[(school_class.number + 1) % 2][i][j] = homework.task
    return render_template("teacherdiary.html", title='Электронный журнал', dont_add_container=True,
                           diary_link=f"/teacherdiary/{to_now_week()}",
                           background_color=["#D1B280", "#C292FA", "#7AB996"][current_user.background_color],
                           current_page=3, table=teacher_schedule, id_table=id_table,
                           week=week, week_list=week_list, holidays=holidays,
                           homework_table=homework_table)


@app.route("/teacherdiary/<int:week>/<int:weekday>/<int:lesson_number>", methods=['GET', 'POST'])
@login_required
def set_marks(week, weekday, lesson_number):
    if current_user.__class__ != Teacher:
        return redirect('/')
    # Проверяем существование класса, номера урока и недели
    if not (lesson_number in range(1, 12) and weekday in range(0, 6) and week in range(1, 41)):
        return redirect(f"/teacherdiary/{to_now_week()}")
    # Проверка на выходной день
    if [week, weekday] in holidays:
        return redirect(f"/teacherdiary/{to_now_week()}")
    # Проверяем существует ли класс у учителя, который имеет урок в данный день
    # Если да, находим его id
    class_id = None
    db_sess = db_session.create_session()
    teacher = db_sess.query(Teacher).filter(Teacher.id == current_user.id).first()
    subject = db_sess.query(Subject).filter(Subject.id == current_user.subject_id
                                            ).first()
    for school_class in teacher.school_classes:
        if not(lesson_number > 6 and school_class.number % 2 == 0 or
               lesson_number < 6 and school_class.number % 2 == 1):
            continue
        if lesson_number > 6 and school_class.number % 2 == 0:
            lesson_number -= 6
        table = get_class_schedule(school_class.number, school_class.letter)
        if len(table) > weekday and len(table[weekday]) > lesson_number - 1 and\
                table[weekday][lesson_number - 1] == subject.name:
            class_id = school_class.id
    if not class_id:
        return redirect(f"/teacherdiary/{to_now_week()}")
    # Создаем поля оценок для каждого ученика из данного класса
    # К сожалению оценки задать как не получится, в отличии от домашней работы
    # если учитель решит изменить оценки в этот день, менять придется всем
    students = db_sess.query(Student).filter(Student.school_class_id == class_id).all()
    MarksSettingForm.marks = FieldList(SelectField("Оценка", choices=['', 5, 4, 3, 2]),
                                       min_entries=len(students))
    form = MarksSettingForm()
    # Если имеется домашняя работа на этот день, выведем её
    if request.method != 'POST':
        homework = db_sess.query(Homework).filter(Homework.subject_id == subject.id,
                                                  Homework.class_id == class_id,
                                                  Homework.date_info ==
                                                  f"{week}/{weekday}/{lesson_number}"
                                                  ).first()
        if homework:
            form.homework.data = homework.task
    if request.method == 'POST':
        # Сохранение оценок
        # Оценки ученика представляют собой строку вида
        # "номер недели/день недели/номер урока/оценка номер недели/день недели/номер урока/оценка..."
        # Удобней бы было сохранять каждую оценку с указанием даты, однако, если брать в расчет
        # количество учеников в школе и количество оценок каждого ученика,
        # поиск может длиться слишком долго
        for i, mark in enumerate(form.marks.data):
            student_marks = db_sess.query(Marks).filter(Marks.student_id == students[i].id,
                                                        Marks.subject_id == subject.id
                                                        ).first()
            # Если нет оценки, проверяем убирает ли её учитель или не просто не поставил
            if not mark:
                if student_marks and f"{week}/{weekday}/{lesson_number}" in student_marks.marks:
                    sm = student_marks.marks.split()
                    for m in sm:
                        if f"{week}/{weekday}/{lesson_number}" in m:
                            sm.remove(m)
                            sm = ' '.join(sm)
                            student_marks.marks = sm
                            break
                continue
            # Если оценка есть, то её либо выставляют, либо редактируют
            mark_string = f"{week}/{weekday}/{lesson_number}/{mark}"
            # Проверяем есть ли у ученика оценки по этому предмету
            if not student_marks:
                marks = Marks(
                    subject_id=subject.id,
                    student_id=students[i].id,
                    marks=mark_string
                )
                db_sess.add(marks)
                continue
            # Если оценки были, но их убрали
            elif not student_marks.marks:
                student_marks.marks = mark_string
                continue
            # Если оценки есть
            # Если оценка редактируется удаляем её
            if f"{week}/{weekday}/{lesson_number}" in student_marks.marks:
                sm = student_marks.marks.split()
                for m in sm:
                    if f"{week}/{weekday}/{lesson_number}" in m:
                        sm.remove(m)
                        sm = ' '.join(sm)
                        student_marks.marks = sm
                        break
            # Заносим оценку в конец
            student_marks.marks += f" {mark_string}"
        db_sess.commit()
        # Сохранение домашнего задания не может производиться аналогично сохранению оценок
        # из-за возможности наличия любого символа в домашнем задании,
        # однако домашних заданий будет примерно в 30 раз меньше чем учеников,
        # что даст нам более быстрый поиск
        homework = db_sess.query(Homework).filter(Homework.subject_id == subject.id,
                                                  Homework.class_id == class_id,
                                                  Homework.date_info ==
                                                  f"{week}/{weekday}/{lesson_number}"
                                                  ).first()
        if not form.homework.data:
            if homework and f"{week}/{weekday}/{lesson_number}" == homework.date_info:
                homework.task = ""
        else:
            if not homework:
                homework = Homework(
                    subject_id=subject.id,
                    class_id=class_id,
                    task=form.homework.data,
                    date_info=f"{week}/{weekday}/{lesson_number}"
                )
                db_sess.add(homework)
            else:
                homework.task = form.homework.data
        db_sess.commit()
        return redirect(f"/teacherdiary/{week}")
    return render_template("set_marks.html", title='Выставление оценок', current_page=3,
                           diary_link=f"/teacherdiary/{to_now_week()}",
                           background_color=["#D1B280", "#C292FA", "#7AB996"][current_user.background_color],
                           form=form, students=students, week=week)


@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    form = RegisterStudentForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_student.html', title='Регистрация ученика',
                                   form=form,
                                   background_color=["#D1B280", "#C292FA", "#7AB996"][0],
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Student).filter(Student.email == form.email.data).first() or\
                db_sess.query(Teacher).filter(Teacher.email == form.email.data).first():
            return render_template('register_student.html', title='Регистрация ученика',
                                   form=form,
                                   background_color=["#D1B280", "#C292FA", "#7AB996"][0],
                                   message="Данная почта уже зарегистрирована в системе")
        school_class = db_sess.query(SchoolClass).filter(SchoolClass.number == form.class_number.data,
                                                         SchoolClass.letter == form.class_letter.data
                                                         ).first()
        # Некрасивое решение проблемы с пользовательским id
        max_student_id = db_sess.query(sqlalchemy.func.max(Student.id)).first()[0]
        max_teacher_id = db_sess.query(sqlalchemy.func.max(Teacher.id)).first()[0]
        if max_student_id and max_teacher_id:
            max_id = max(max_student_id, max_teacher_id) + 1
        elif max_student_id:
            max_id = max_student_id + 1
        elif max_teacher_id:
            max_id = max_teacher_id + 1
        else:
            max_id = 1
        student = Student(
            id=max_id,
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            school_class_id=school_class.id,
            background_color=0
        )
        student.set_password(form.password.data)
        db_sess.add(student)
        db_sess.commit()
        return redirect('/login')
    return render_template('register_student.html', title='Регистрация ученика',
                           form=form, background_color=["#D1B280", "#C292FA", "#7AB996"][0])


@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    form = RegisterTeacherForm()
    if form.validate_on_submit():
        # Проверка почта/пароль
        if form.password.data != form.password_again.data:
            return render_template('register_teacher.html', title='Регистрация учителя',
                                   form=form,
                                   background_color=["#D1B280", "#C292FA", "#7AB996"][0],
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Student).filter(Student.email == form.email.data).first() or \
                db_sess.query(Teacher).filter(Teacher.email == form.email.data).first():
            return render_template('register_teacher.html', title='Регистрация учителя',
                                   form=form,
                                   background_color=["#D1B280", "#C292FA", "#7AB996"][0],
                                   message="Данная почта уже зарегистрирована в системе")
        subject = db_sess.query(Subject).filter(Subject.name == form.subject.data
                                                ).first()
        # В зависимости от цифры у некоторых классов присутствуют одни уроки и отсутствуют другие.
        # Проверяем есть ли у данного класса данный урок.
        # Заодно проверяем, нет ли уже у какого-то из выбранных классов учителя по заданному предмету.
        if not form.classes.data:
            return render_template('register_teacher.html', title='Регистрация учителя',
                                   form=form,
                                   background_color=["#D1B280", "#C292FA", "#7AB996"][0],
                                   message=f'Выберите хотя бы один класс')
        for number_letter in form.classes.data:
            letter = number_letter[-1]
            number = int(number_letter[:-1])
            school_class = db_sess.query(SchoolClass).filter(SchoolClass.letter == letter,
                                                             SchoolClass.number == number).first()
            if subject not in school_class.subjects:
                return render_template('register_teacher.html', title='Регистрация учителя',
                                       form=form,
                                       background_color=["#D1B280", "#C292FA", "#7AB996"][0],
                                       message=f'У {number} класса отсутствует предмет'
                                               f' {form.subject.data}')
            for teacher in db_sess.query(Teacher).all():
                if school_class in teacher.school_classes and teacher.subject_id == subject.id:
                    return render_template('register_teacher.html', title='Регистрация учителя',
                                           form=form,
                                           background_color=["#D1B280", "#C292FA", "#7AB996"][0],
                                           message=f'У {number}{letter} класса уже есть учитель'
                                                   f' по предмету {subject.name}')
        # Некрасивое решение проблемы с пользовательским id
        max_student_id = db_sess.query(sqlalchemy.func.max(Student.id)).first()[0]
        max_teacher_id = db_sess.query(sqlalchemy.func.max(Teacher.id)).first()[0]
        if max_student_id and max_teacher_id:
            max_id = max(max_student_id, max_teacher_id) + 1
        elif max_student_id:
            max_id = max_student_id + 1
        elif max_teacher_id:
            max_id = max_teacher_id + 1
        else:
            max_id = 1
        teacher = Teacher(
            id=max_id,
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            subject_id=subject.id,
            background_color=0
        )
        teacher.set_password(form.password.data)
        # Очень страшная проверка пересечения уроков в расписании
        # Делим выбранные классы на 2 смены и попарно сравниваем каждый урок каждого дня,
        # чтоб не получилось ситуаций, в которых учитель ведет уроки у 2 классов одновременно
        list_of_tables1 = list()
        names1 = list()
        list_of_tables2 = list()
        names2 = list()
        for number_letter in form.classes.data:
            letter = number_letter[-1]
            number = int(number_letter[:-1])
            if number % 2 == 1:
                list_of_tables1.append(get_class_schedule(number, letter))
                names1.append(f"{number}{letter}")
            else:
                list_of_tables2.append(get_class_schedule(number, letter))
                names2.append(f"{number}{letter}")
        for i, first_table in enumerate(list_of_tables1):
            for j, second_table in enumerate(list_of_tables1):
                if i == j:
                    continue
                for day in range(min(len(first_table), len(second_table))):
                    for lesson in range(min(len(first_table[day]), len(second_table[day]))):
                        if first_table[day][lesson] == second_table[day][lesson] and\
                                first_table[day][lesson] == subject.name:
                            return render_template('register_teacher.html',
                                                   title='Регистрация учителя',
                                                   form=form,
                                                   background_color=["#D1B280", "#C292FA", "#7AB996"][0],
                                                   message=f'У классов {names1[i]} и {names1[j]}'
                                                           f' совпадают расписания,'
                                                           f' уберите один из классов или'
                                                           f' измените расписание.')
        for i, first_table in enumerate(list_of_tables2):
            for j, second_table in enumerate(list_of_tables2):
                if i == j:
                    continue
                for day in range(min(len(first_table), len(second_table))):
                    for lesson in range(min(len(first_table[day]), len(second_table[day]))):
                        if first_table[day][lesson] == second_table[day][lesson] and\
                                first_table[day][lesson] == subject.name:
                            return render_template('register_teacher.html',
                                                   title='Регистрация учителя',
                                                   form=form,
                                                   background_color=["#D1B280", "#C292FA", "#7AB996"][0],
                                                   message=f'У классов {names2[i]} и {names2[j]}'
                                                           f' совпадают расписания,'
                                                           f' уберите один из классов или'
                                                           f' измените расписание.')
        # Если все проверки пройдены, добавляем учителю каждый выбранный класс
        db_sess.add(teacher)
        for number_letter in form.classes.data:
            letter = number_letter[-1]
            number = int(number_letter[:-1])
            school_class = db_sess.query(SchoolClass).filter(SchoolClass.letter == letter,
                                                             SchoolClass.number == number).first()
            teacher.school_classes.append(school_class)
        db_sess.commit()
        return redirect('/login')
    return render_template('register_teacher.html', title='Регистрация учителя', form=form,
                           background_color=["#D1B280", "#C292FA", "#7AB996"][0])


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # Сначала пройдемся по учителям
        teacher = db_sess.query(Teacher).filter(Teacher.email == form.email.data).first()
        if teacher and teacher.check_password(form.password.data):
            login_user(teacher, remember=form.remember_me.data)
            return redirect(f"/teacherdiary/{to_now_week()}")
        # Если учитель не найден, пройдемся по ученикам
        student = db_sess.query(Student).filter(Student.email == form.email.data).first()
        if student and student.check_password(form.password.data):
            login_user(student, remember=form.remember_me.data)
            return redirect(f"/studentdiary/{to_now_week()}")
        return render_template('login.html',
                               message="Неправильно указана почта или пароль",
                               form=form,
                               background_color=["#D1B280", "#C292FA", "#7AB996"][0])
    return render_template('login.html', title='Вход', form=form,
                           background_color=["#D1B280", "#C292FA", "#7AB996"][0])


@app.route("/settings", methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if current_user.__class__ == Teacher:
            user = db_sess.query(Teacher).filter(Teacher.id == current_user.id).first()
        else:
            user = db_sess.query(Student).filter(Student.id == current_user.id).first()
        if user.check_password(form.old_password.data):
            user.set_password(form.new_password.data)
        user.background_color = ["Светлый", "Фиолетовый", "Зеленый"].index(form.themes.data)
        db_sess.commit()
        return redirect('/')
    if current_user.__class__ == Student:
        diary = 'studentdiary'
    else:
        diary = 'teacherdiary'
    return render_template('settings.html', title='Настройки',
                           diary_link=f"/{diary}/{to_now_week()}",
                           report_link="/studentreport/1",
                           form=form, current_page=4,
                           background_color=["#D1B280", "#C292FA", "#7AB996"][current_user.background_color])


def main():
    db_session.global_init("db/netschool.db")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
