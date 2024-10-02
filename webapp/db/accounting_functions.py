import sqlite3
import uuid
from typing import Union

from werkzeug.security import generate_password_hash

from webapp.db.db_functions import get_connection
from webapp.models.User import User
from webapp.exceptions.exceptions import AlreadyRegisteredException


def register_user(login: str, email: str, password: str):
    connection = get_connection()
    # более правильный способ, но требует блокировки БД
    # if find_user_with_email(email) or find_user_with_login(login):
    #     raise AlreadyRegisteredException()
    try:
        connection.cursor().execute("""
                INSERT INTO users (user_id, login, email, password, role)
                VALUES (?, ?, ?, ?, ?);
            """, (str(uuid.uuid4()), login, email, generate_password_hash(password), "reader"))
        connection.commit()
    except sqlite3.IntegrityError as e:
        if "users.email" in str(e) or "users.login" in str(e):
            connection.rollback()
            raise AlreadyRegisteredException()


def get_all_users() -> list[User]:
    all_users = get_connection().cursor().execute("""
        SELECT user_id, login, email, password, role FROM users
        WHERE role != 'admin'
    """).fetchall()
    return [User(user["user_id"], user["login"], user["email"], user["password"], user["role"]) for user in all_users]


def find_user_by_id(user_id: str) -> Union[User, None]:
    record = get_connection().cursor().execute("""
                SELECT user_id, login, email, password, role
                FROM users
                WHERE user_id = ?;
            """, (user_id,)).fetchone()
    if record is None:
        return None
    return User(record["user_id"], record["login"], record["email"], record["password"], record["role"])


def find_user_by_login(user_login: str) -> Union[User, None]:
    record = get_connection().cursor().execute("""
                    SELECT user_id, login, email, password, role
                    FROM users
                    WHERE login = ?;
                """, (user_login,)).fetchone()
    if record is None:
        return None
    return User(record["user_id"], record["login"], record["email"], record["password"], record["role"])


def find_user_by_email(user_email: str) -> Union[User, None]:
    record = get_connection().cursor().execute("""
                    SELECT user_id, login, email, password, role
                    FROM users
                    WHERE email = ?;
                """, (user_email,)).fetchone()
    if record is None:
        return None
    return User(record["user_id"], record["login"], record["email"], record["password"], record["role"])


def user_to_author(user_id: str):
    connection = get_connection()
    connection.cursor().execute("""
            UPDATE users
            SET role = 'author'
            WHERE user_id = ?
        """, (user_id,))
    connection.commit()


def user_to_reader(user_id: str):
    connection = get_connection()
    connection.cursor().execute("""
            UPDATE users
            SET role = 'reader'
            WHERE user_id = ?
        """, (user_id,))
    connection.commit()
