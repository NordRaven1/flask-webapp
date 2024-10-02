from flask_wtf import FlaskForm
from wtforms import PasswordField, EmailField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[DataRequired(message='Поле "Email" обязательно для заполнения')])
    password = PasswordField("Пароль", validators=[DataRequired(message='Поле "Пароль" обязательно для заполнения')])
