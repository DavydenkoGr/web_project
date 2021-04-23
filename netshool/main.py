from data import db_session
from data.marks import Marks
from data.school_classes import SchoolClass
from data.students import Student
from data.subjects import Subject
from data.teachers import Teacher
from forms.registration import RegisterStudentForm, RegisterTeacherForm, LoginForm
from forms.set_marks import MarksSettingForm
from flask import Flask, render_template, redirect, request, abort, make_response, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from wtforms import SelectField, FieldList
from xlsx_reader import get_class_schedule


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
    logout_user()
    return redirect("/")


@app.route("/")
def index():
    return render_template("base.html", title='Электронный дневник')


@app.route("/studentdiary")
@login_required
def studentdiary():
    if type_of_user != 'student':
        return redirect('/')
    db_sess = db_session.create_session()
    school_class = db_sess.query(SchoolClass).filter(current_user.school_class_id == SchoolClass.id
                                                     ).first()
    table = get_class_schedule(school_class.number, school_class.letter)
    return render_template("studentdiary.html", title='Электронный дневник',
                           table=table, size=len(table), dont_add_container=True)


@app.route("/teacherdiary")
@login_required
def teacherdiary():
    if type_of_user != 'teacher':
        return redirect('/')
    return render_template("teacherdiary.html", title='Электронный журнал', dont_add_container=True)


@app.route("/teacherdiary/set_marks/<int:class_id>", methods=['GET', 'POST'])
@login_required
def set_marks(class_id):
    if type_of_user != 'teacher':
        return redirect('/')
    db_sess = db_session.create_session()
    students = db_sess.query(Student).filter(Student.school_class_id == class_id).all()
    MarksSettingForm.marks = FieldList(SelectField("Оценка", choices=['', 5, 4, 3, 2]),
                                       min_entries=len(students))
    form = MarksSettingForm()
    if request.method == 'POST':
        # Сохранение оценок
        print(form.homework.data)
        print(form.marks.data)
        return redirect('/teacherdiary')
    return render_template("set_marks.html", title='Выставление оценок',
                           form=form, students=students)


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
        for number_letter in form.classes.data:
            letter = number_letter[-1]
            number = int(number_letter[:-1])
            school_class = db_sess.query(SchoolClass).filter(SchoolClass.letter == letter,
                                                             SchoolClass.number == number).first()
            if subject not in school_class.subjects:
                return render_template('register_teacher.html', title='Регистрация учителя',
                                       form=form,
                                       message=f'У {number} класса отсутствует предмет {form.subject.data}')
        teacher = Teacher(
            surname=form.surname.data,
            name=form.name.data,
            email=form.email.data,
            subject_id=subject.id
        )
        teacher.set_password(form.password.data)
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
            return redirect("/teacherdiary")
        # Если учитель не найден, пройдемся по ученикам
        student = db_sess.query(Student).filter(Student.email == form.email.data).first()
        if student and student.check_password(form.password.data):
            type_of_user = 'student'
            login_user(student, remember=form.remember_me.data)
            return redirect("/studentdiary")
        return render_template('login.html',
                               message="Неправильно указана почта или пароль",
                               form=form)
    return render_template('login.html', title='Вход', form=form)


def main():
    db_session.global_init("db/netschool.db")
    app.run()


if __name__ == '__main__':
    main()
