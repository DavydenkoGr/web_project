from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, IntegerField, BooleanField
from wtforms import SelectField, RadioField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired


class RegisterStudentForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    class_number = SelectField('Class number', validators=[DataRequired()], choices=[i + 1 for i in range(11)])
    class_letter = SelectField('Class letter', validators=[DataRequired()], choices=['А', 'Б', 'В', 'Г'])
    submit = SubmitField('Зарегистрироваться')


class RegisterTeacherForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    classes = RadioField('Классы', validators=[DataRequired()],
                         choices=[str(i + 1) + j for i in range(11) for j in ['А', 'Б', 'В', 'Г']])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
