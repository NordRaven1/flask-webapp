from flask_wtf import FlaskForm
from wtforms import TextAreaField
from wtforms.validators import DataRequired


class CommentsForm(FlaskForm):
    comment_text = TextAreaField("Добавить комментарий", validators=[DataRequired(message='Поле "Текст" обязательно '
                                                                                          'для заполнения')])
