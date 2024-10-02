from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, FileField
from wtforms.validators import DataRequired


class ArticleForm(FlaskForm):
    article_title = StringField("Название статьи", validators=[DataRequired(message='Поле "Название" обязательно для '
                                                                                    'заполнения')])
    article_text = TextAreaField("Текст статьи", validators=[DataRequired(message='Поле "Текст" обязательно для '
                                                                                  'заполнения')])
    cover_image = FileField("Прикрепите изображение", validators=[FileAllowed(
        ['jpg', 'jpeg', 'png'], 'Загружать можно только изображения формата "jpg", "jpeg", "png" !')])
