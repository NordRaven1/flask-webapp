from webapp.models.User import User


class Course:
    def __init__(self, course_id: str, course_title: str, author: User, description: str):
        self.course_id = course_id
        self.course_title = course_title
        self.author = author
        self.description = description
