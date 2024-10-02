from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import DataRequired, ValidationError


class RegistrationForm(FlaskForm):
    login = StringField("Имя пользователя", validators=[DataRequired(message='Поле "Имя" обязательно для заполнения')])
    email = EmailField("Email", validators=[DataRequired(message='Поле "Email" обязательно для заполнения')])
    password = PasswordField("Пароль", validators=[DataRequired(message='Поле "Пароль" обязательно для заполнения')])
    password_repeat = PasswordField("Повторите пароль", validators=[DataRequired(message='Поле "Повторите пароль" '
                                                                                         'обязательно для заполнения')])

    def validate_password_repeat(self, field):
        if field.data != self.password.data:
            raise ValidationError("Пароли должны совпадать!")
