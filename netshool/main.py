from data import db_session
from data.marks import Marks
from data.school_classes import SchoolClass
from data.students import Student
from data.subjects import Subject
from data.teachers import Teacher
from data.homework import Homework
from forms.registration import RegisterStudentForm, RegisterTeacherForm, LoginForm
from forms.set_marks import MarksSettingForm
from flask import Flask, render_template, redirect, request, abort, make_response, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from wtforms import SelectField, FieldList
from xlsx_reader import get_class_schedule
from date_and_time import *


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
# Переменная, отвечающая за тип пользователя
type_of_user = None


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    if type_of_user == 'teacher':
        return db_sess.query(Teacher).get(user_id)
    elif type_of_user == 'student':
        return db_sess.query(Student).get(user_id)


@app.route('/logout')
@login_required
def logout():
    global type_of_user
    type_of_user = None
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    return render_template("base.html", title='Электронный дневник')


@app.route("/studentdiary/<int:week>")
@login_required
def studentdiary(week):
    if type_of_user != 'student':
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

    return render_template("studentdiary.html", title='Электронный дневник',
                           table=table, dont_add_container=True,
                           sizes=[len(table), [len(table[i]) for i in range(len(table))]],
                           week=week, week_list=week_list, holidays=holidays, mark_table=mark_table,
                           homework_table=homework_table)


@app.route("/teacherdiary/<int:week>")
@login_required
def teacherdiary(week):
    if type_of_user != 'teacher':
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
                           table=teacher_schedule, id_table=id_table,
                           week=week, week_list=week_list, holidays=holidays,
                           homework_table=homework_table)


@app.route("/teacherdiary/<int:week>/<int:weekday>/<int:lesson_number>", methods=['GET', 'POST'])
@login_required
def set_marks(week, weekday, lesson_number):
    if type_of_user != 'teacher':
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
                print(1)
                homework = Homework(
                    subject_id=subject.id,
                    class_id=class_id,
                    task=form.homework.data,
                    date_info=f"{week}/{weekday}/{lesson_number}"
                )
                db_sess.add(homework)
            else:
                homework.task=form.homework.data
        db_sess.commit()
        return redirect(f"/teacherdiary/{week}")
    return render_template("set_marks.html", title='Выставление оценок',
                           form=form, students=students, week=week)


@app.route('/register_student', methods=['GET', 'POST'])
def register_student():
    form = RegisterStudentForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register_student.html', title='Регистрация ученика',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Student).filter(Student.email == form.email.data).first() or\
                db_sess.query(Teacher).filter(Teacher.email == form.email.data).first():
            return render_template('register_student.html', title='Регистрация ученика',
                                   form=form,
                                   message="Данная почта уже зарегистрирована в системе")
        school_class = db_sess.query(SchoolClass).filter(SchoolClass.number == form.class_number.data,
                                                         SchoolClass.letter == form.class_letter.data
                                                         ).first()
        student = Student(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            school_class_id=school_class.id
        )
        student.set_password(form.password.data)
        db_sess.add(student)
        db_sess.commit()
        return redirect('/login')
    return render_template('register_student.html', title='Регистрация ученика', form=form)


@app.route('/register_teacher', methods=['GET', 'POST'])
def register_teacher():
    form = RegisterTeacherForm()
    if form.validate_on_submit():
        # Проверка почта/пароль
        if form.password.data != form.password_again.data:
            return render_template('register_teacher.html', title='Регистрация учителя',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(Student).filter(Student.email == form.email.data).first() or \
                db_sess.query(Teacher).filter(Teacher.email == form.email.data).first():
            return render_template('register_teacher.html', title='Регистрация учителя',
                                   form=form,
                                   message="Данная почта уже зарегистрирована в системе")
        subject = db_sess.query(Subject).filter(Subject.name == form.subject.data
                                                ).first()
        # В зависимости от цифры у некоторых классов присутсвуют одни уроки и отсутствуют другие.
        # Проверяем есть ли у данноко класса данный урок.
        # Заодно проверяем, нет ли уже у какого-то из выбранных классов учителя по заданному предмету.
        for number_letter in form.classes.data:
            letter = number_letter[-1]
            number = int(number_letter[:-1])
            school_class = db_sess.query(SchoolClass).filter(SchoolClass.letter == letter,
                                                             SchoolClass.number == number).first()
            if subject not in school_class.subjects:
                return render_template('register_teacher.html', title='Регистрация учителя',
                                       form=form,
                                       message=f'У {number} класса отсутствует предмет'
                                               f' {form.subject.data}')
            for teacher in db_sess.query(Teacher).all():
                if school_class in teacher.school_classes and teacher.subject_id == subject.id:
                    return render_template('register_teacher.html', title='Регистрация учителя',
                                           form=form,
                                           message=f'У {number}{letter} класса уже есть учитель'
                                                   f' по предмету {subject.name}')
        teacher = Teacher(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            subject_id=subject.id
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
    return render_template('register_teacher.html', title='Регистрация учителя', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    global type_of_user
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        # Сначала пройдемся по учителям
        teacher = db_sess.query(Teacher).filter(Teacher.email == form.email.data).first()
        if teacher and teacher.check_password(form.password.data):
            type_of_user = 'teacher'
            login_user(teacher, remember=form.remember_me.data)
            return redirect(f"/teacherdiary/{to_now_week()}")
        # Если учитель не найден, пройдемся по ученикам
        student = db_sess.query(Student).filter(Student.email == form.email.data).first()
        if student and student.check_password(form.password.data):
            type_of_user = 'student'
            login_user(student, remember=form.remember_me.data)
            return redirect(f"/studentdiary/{to_now_week()}")
        return render_template('login.html',
                               message="Неправильно указана почта или пароль",
                               form=form)
    return render_template('login.html', title='Вход', form=form)


def main():
    db_session.global_init("db/netschool.db")
    print(holidays)
    app.run()


if __name__ == '__main__':
    main()
