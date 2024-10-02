from webapp.models.User import User


class Comment:
    def __init__(self, comment_id: str, comment_text: str, author: User):
        self.comment_id = comment_id
        self.comment_text = comment_text
        self.author = author
