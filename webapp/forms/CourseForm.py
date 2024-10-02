from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


class CourseForm(FlaskForm):
    course_title = StringField("Название курса", validators=[DataRequired(message='Поле "Название" обязательно для '
                                                                                  'заполнения')])
    description = TextAreaField("Описание курса", validators=[DataRequired(message='Поле "Описание" обязательно для '
                                                                                   'заполнения')])
