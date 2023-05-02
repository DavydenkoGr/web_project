from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField


class MarksSettingForm(FlaskForm):
    """teacher setting marks form"""
    homework = TextAreaField("Домашняя работа")
    submit = SubmitField('Сохранить')
