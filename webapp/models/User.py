from flask_login import UserMixin
from werkzeug.security import check_password_hash


class User(UserMixin):
    def __init__(self, user_id: str, login: str, email: str, password, role: str):
        self.user_id = user_id
        self.login = login
        self.email = email
        self.password = password
        self.role = role

    def get_id(self):
        return self.user_id

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __eq__(self, other):
        return isinstance(other, type(self)) and\
            self.user_id == other.user_id and\
            self.login == other.login and\
            self.email == other.email
