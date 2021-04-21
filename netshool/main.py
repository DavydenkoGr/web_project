from flask import Flask, render_template, redirect, request, abort, make_response, jsonify, url_for
from data import db_session
from data.marks import Marks
from data.school_classes import SchoolClass
from data.students import Student
from data.subjects import Subject
from data.teachers import Teacher
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api


app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    return 'Тестовая страница'


def main():
    db_session.global_init("db/netschool.db")


if __name__ == '__main__':
    main()
