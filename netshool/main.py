from data import db_session
from data.marks import Marks
from data.school_classes import SchoolClass
from data.students import Student
from data.subjects import Subject
from data.teachers import Teacher
from forms.registration import RegisterStudentForm, RegisterTeacherForm, LoginForm
from flask import Flask, render_template, redirect, request, abort, make_response, jsonify, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(Student).get(user_id)


@app.route("/")
def index():
    return render_template("base.html", title='Электронный дневник')


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
        school_class = db_sess.query(SchoolClass).filter(SchoolClass.number == form.class_number,
                                                         SchoolClass.letter == form.class_letter
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
        return redirect('/login')
    return render_template('register_teacher.html', title='Регистрация учителя', form=form)


@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html',title= 'Вход', form=form)


def main():
    db_session.global_init("db/netschool.db")
    app.run()


if __name__ == '__main__':
    main()
