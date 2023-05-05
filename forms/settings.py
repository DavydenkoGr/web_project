from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms import SelectField


class SettingsForm(FlaskForm):
    """settings form"""
    old_password = PasswordField("Старый пароль")
    new_password = PasswordField("Новый пароль")
    themes = SelectField("Цвета", choices=["Светлый", "Фиолетовый", "Зеленый"])
    submit = SubmitField("Применить")
