import sqlite3
from typing import Union

from flask_login import current_user

from webapp.db.accounting_functions import find_user_by_id
from webapp.db.db_functions import get_connection
import uuid

from webapp.models.Article import Article
from webapp.models.Comment import Comment
from webapp.models.Course import Course
from webapp.models.User import User
from webapp.exceptions.exceptions import CourseAlreadyExists, ArticleAlreadyExists
from webapp.images.CoverImage import CoverImage
from webapp.images.image_functions import image_from_bytes, image_to_bytes
from PIL import Image as PILImage


def add_course(course_title: str, author: User, description: str):
    connection = get_connection()
    try:
        connection.cursor().execute("""
            INSERT INTO courses (course_id, course_title, author_id, description)
            VALUES (?, ?, ?, ?);
        """, (str(uuid.uuid4()), course_title, author.user_id, description))
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        raise CourseAlreadyExists()


def edit_course(course_title: str, description: str, course_id: str):
    connection = get_connection()
    try:
        connection.cursor().execute("""
            UPDATE courses
            SET course_title = ?, description = ?
            WHERE course_id = ?
        """, (course_title, description, course_id))
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        raise CourseAlreadyExists()


def get_all_curses() -> list[Course]:
    all_courses = get_connection().cursor().execute("""
        SELECT course_id, course_title, author_id, description FROM courses
    """).fetchall()
    return [Course(course["course_id"], course["course_title"], find_user_by_id(course["author_id"]),
                   course["description"]) for course in all_courses]


def find_course_by_id(course_id: str) -> Union[Course, None]:
    record = get_connection().cursor().execute("""
            SELECT course_id, course_title, author_id, description
            FROM courses
            WHERE course_id = ?;
        """, (course_id,)).fetchone()
    if record is None:
        return None
    return Course(record["course_id"], record["course_title"], find_user_by_id(record["author_id"]),
                  record["description"])


def get_courses_per_page(user_id: Union[str, None], per_page: int, offset: int, title: str, description: str) -> \
        list[Course]:
    courses_per_page = get_connection().cursor().execute("""
    SELECT c.course_id, c.course_title, c.author_id, c.description,
       CASE WHEN fc.course_id IS NOT NULL THEN 1 ELSE 2 END AS source
    FROM courses c
    LEFT JOIN fav_courses fc ON c.course_id = fc.course_id AND fc.user_id = ?
    WHERE (c.course_title LIKE '%' || ? || '%' OR ? = '')
    AND (c.description LIKE '%' || ? || '%' OR ? = '')
    ORDER BY source
    LIMIT ? OFFSET ?
    """, (user_id, title, title, description, description, per_page, offset)).fetchall()
    return [Course(course["course_id"], course["course_title"], find_user_by_id(course["author_id"]),
                   course["description"]) for course in courses_per_page]


def get_fav_courses_per_page(user_id: str, per_page: int, offset: int) -> list[Course]:
    courses_per_page = get_connection().cursor().execute("""
    SELECT c.course_id, c.course_title, c.author_id, c.description
    FROM courses c
    JOIN fav_courses fc ON c.course_id = fc.course_id AND fc.user_id = ?
    LIMIT ? OFFSET ?
    """, (user_id, per_page, offset)).fetchall()
    return [Course(course["course_id"], course["course_title"], find_user_by_id(course["author_id"]),
                   course["description"]) for course in courses_per_page]


def get_count_of_courses(title: str, description: str) -> int:
    count_of_curses = get_connection().cursor().execute("""
    SELECT COUNT(course_id) FROM courses
    WHERE (course_title LIKE '%' || ? || '%' OR ? = '')
    AND (description LIKE '%' || ? || '%' OR ? = '')
    """, (title, title, description, description)).fetchone()[0]
    return count_of_curses


def get_count_of_fav_courses() -> int:
    count_of_fav_curses = get_connection().cursor().execute("""
    SELECT COUNT(course_id) FROM fav_courses
    WHERE user_id = ?;
    """, (current_user.user_id,)).fetchone()[0]
    return count_of_fav_curses


def add_course_to_favourites(user: User, course_id: str):
    connection = get_connection()
    connection.cursor().execute("""
            INSERT INTO fav_courses (user_id, course_id)
            VALUES (?, ?);
        """, (user.user_id, course_id))
    connection.commit()


def get_courses_favoured_by_user(user: User) -> list[Course]:
    courses = get_connection().cursor().execute("""
                SELECT c.course_id, c.course_title, c.author_id, c.description FROM courses c
                JOIN fav_courses fc ON c.course_id = fc.course_id AND fc.user_id = ?
            """, (user.user_id,)).fetchall()
    return [Course(course["course_id"], course["course_title"], find_user_by_id(course["author_id"]),
                   course["description"]) for course in courses]


def remove_course_from_favoured(user: User, course_id: str):
    connection = get_connection()
    connection.cursor().execute("""
                DELETE FROM fav_courses
                WHERE course_id = ? AND user_id = ?
            """, (course_id, user.user_id))
    connection.commit()


def delete_course(course_id: str):
    connection = get_connection()
    connection.cursor().execute("""
                DELETE FROM courses
                WHERE course_id = ?
            """, (course_id,))
    connection.commit()


def get_all_articles_at_course(course_id: str, per_page: int, offset: int) -> list[Article]:
    all_articles = get_connection().cursor().execute("""
            SELECT article_id, article_title, article_text, author_id, image FROM articles
            WHERE parent_course_id = ?
            LIMIT ? OFFSET ?
        """, (course_id, per_page, offset)).fetchall()
    return [Article(article["article_id"], article["article_title"], article["article_text"],
                    find_user_by_id(article["author_id"]), CoverImage.create(image_from_bytes(article["image"])))
            for article in all_articles]


def add_article(article_title: str, course_id: str, article_text: str, author: User,
                image: Union[PILImage.Image, None]):
    connection = get_connection()
    image_bytes = image_to_bytes(image)
    try:
        connection.cursor().execute("""
            INSERT INTO articles (article_id, article_title, parent_course_id, article_text, author_id, image)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (str(uuid.uuid4()), article_title, course_id, article_text, author.user_id, image_bytes))
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        raise ArticleAlreadyExists()


def find_article_by_id(article_id: str) -> Union[Article, None]:
    record = get_connection().cursor().execute("""
            SELECT article_id, article_title, article_text, author_id, image
            FROM articles
            WHERE article_id = ?;
        """, (article_id,)).fetchone()
    if record is None:
        return None
    return Article(record["article_id"], record["article_title"], record["article_text"],
                   find_user_by_id(record["author_id"]), CoverImage.create(image_from_bytes(record["image"])))


def get_count_of_articles_in_course(course_id: str) -> int:
    count_of_articles = get_connection().cursor().execute("""
    SELECT COUNT(article_id) FROM articles
    WHERE parent_course_id = ?;
    """, (course_id,)).fetchone()[0]
    return count_of_articles


def delete_article(article_id: str):
    connection = get_connection()
    connection.cursor().execute("""
                DELETE FROM articles
                WHERE article_id = ?
            """, (article_id,))
    connection.commit()


def edit_article(article_title: str, article_text: str, article_id: str, cover_image: Union[PILImage.Image, None]):
    connection = get_connection()
    image_bytes = image_to_bytes(cover_image)
    try:
        connection.cursor().execute("""
            UPDATE articles
            SET article_title = ?, article_text = ?, image = ?
            WHERE article_id = ?
        """, (article_title, article_text, image_bytes, article_id))
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        raise ArticleAlreadyExists()


def add_comment(author: User, comment_text: str, article_id: str):
    connection = get_connection()
    connection.cursor().execute("""
            INSERT INTO comments (comment_id, comment_text, author_id, parent_article_id)
            VALUES (?, ?, ?, ?);
        """, (str(uuid.uuid4()), comment_text, author.user_id, article_id))
    connection.commit()


def get_comments_for_article(article_id: str) -> list[Comment]:
    comments = get_connection().cursor().execute("""
            SELECT comment_id, comment_text, author_id FROM comments
            WHERE parent_article_id = ? AND parent_comment_id IS NULL
        """, (article_id,)).fetchall()
    return [Comment(comment["comment_id"], comment["comment_text"], find_user_by_id(comment["author_id"]))
            for comment in comments]


def find_comment_by_id(comment_id: str) -> Union[Comment, None]:
    record = get_connection().cursor().execute("""
            SELECT comment_id, comment_text, author_id FROM comments
            WHERE comment_id = ?
        """, (comment_id,)).fetchone()
    if record is None:
        return None
    return Comment(record["comment_id"], record["comment_text"], find_user_by_id(record["author_id"]))


def reply_to_comment(author: User, comment_text: str, article_id: str, parent_comment_id: str):
    connection = get_connection()
    connection.cursor().execute("""
            INSERT INTO comments (comment_id, comment_text, author_id, parent_article_id, parent_comment_id)
            VALUES (?, ?, ?, ?, ?);
        """, (str(uuid.uuid4()), comment_text, author.user_id, article_id, parent_comment_id))
    connection.commit()


def get_replies_for_comment(parent_comment_id: str) -> list[Comment]:
    replies = get_connection().cursor().execute("""
               SELECT comment_id, comment_text, author_id FROM comments
               WHERE parent_comment_id = ?
           """, (parent_comment_id,)).fetchall()
    return [Comment(reply["comment_id"], reply["comment_text"], find_user_by_id(reply["author_id"]))
            for reply in replies]


def find_article_by_comment(comment: Comment) -> Union[Article, None]:
    record = get_connection().cursor().execute("""
            SELECT a.article_id, a.article_title, a.article_text, a.author_id, a.image
            FROM articles a
            JOIN comments c on c.parent_article_id = a.article_id AND c.comment_id = ?
        """, (comment.comment_id,)).fetchone()
    if record is None:
        return None
    return Article(record["article_id"], record["article_title"], record["article_text"],
                   find_user_by_id(record["author_id"]), CoverImage.create(image_from_bytes(record["image"])))


def find_course_by_article(article: Article) -> Union[Course, None]:
    record = get_connection().cursor().execute("""
            SELECT c.course_id, c.course_title, c.author_id, c.description
            FROM courses c
            JOIN articles a ON c.course_id = a.parent_course_id AND a.article_id = ?
        """, (article.article_id,)).fetchone()
    if record is None:
        return None
    return Course(record["course_id"], record["course_title"], find_user_by_id(record["author_id"]),
                  record["description"])


def get_comments_left_by_user(user: User) -> list[Comment]:
    comments = get_connection().cursor().execute("""
                   SELECT comment_id, comment_text, author_id FROM comments
                   WHERE author_id = ?
               """, (user.user_id,)).fetchall()
    return [Comment(comment["comment_id"], comment["comment_text"], find_user_by_id(comment["author_id"]))
            for comment in comments]


def delete_comment(comment_id: str):
    connection = get_connection()
    connection.cursor().execute("""
                DELETE FROM comments
                WHERE comment_id = ?
            """, (comment_id,))
    connection.commit()
