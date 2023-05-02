from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, BooleanField
from wtforms import SelectField, widgets, SelectMultipleField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class RegisterStudentForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    class_number = SelectField('Номер класса', validators=[DataRequired()], choices=[i + 1 for i in range(11)])
    class_letter = SelectField('Буква класса', validators=[DataRequired()], choices=['А', 'Б', 'В', 'Г'])
    submit = SubmitField('Зарегистрироваться')


class RegisterTeacherForm(FlaskForm):
    s = ('Математика', 'Физика', 'Химия', 'Информатика', 'Русский язык', 'Английский язык',
         'История', 'Обществознание', 'Биология', 'География', 'Литература',
         'Физкультура', 'ОБЖ', 'Технология', 'ИЗО', 'Музыка', 'Окружающий мир')
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия', validators=[DataRequired()])
    name = StringField('Имя', validators=[DataRequired()])
    subject = SelectField('Предмет', validators=[DataRequired()], choices=s)
    classes = MultiCheckboxField('Классы', choices=[(str(i + 1) + j, str(i + 1) + j)
                                                    for i in range(11) for j in ['А', 'Б', 'В', 'Г']])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SettingsForm(FlaskForm):
    old_password = PasswordField('Старый пароль')
    new_password = PasswordField('Новый пароль')
    themes = SelectField('Цвета', choices=["Светлый", "Фиолетовый", "Зеленый"])
    submit = SubmitField('Применить')
