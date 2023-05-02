from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField
from wtforms import SelectField, widgets, SelectMultipleField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired
from constants import CLASSES_LETTERS, CLASSES_NUMBERS, SUBJECTS, CLASSES_WITH_NUMBERS


class MultiCheckboxField(SelectMultipleField):
    """additional class, which helps to create multi checkbox field in the registration form"""
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class RegisterStudentForm(FlaskForm):
    """register student form"""
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    class_number = SelectField('Номер класса', validators=[DataRequired()], choices=CLASSES_NUMBERS)
    class_letter = SelectField('Буква класса', validators=[DataRequired()], choices=CLASSES_LETTERS)
    submit = SubmitField('Зарегистрироваться')


class RegisterTeacherForm(FlaskForm):
    """register teacher form"""
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    subject = SelectField('Предмет', validators=[DataRequired()], choices=SUBJECTS)
    classes = MultiCheckboxField('Классы', choices=CLASSES_WITH_NUMBERS)
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    """login form"""
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')
