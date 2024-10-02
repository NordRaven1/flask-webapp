from typing import Union

from webapp.models.User import User
from webapp.images.CoverImage import CoverImage


class Article:
    def __init__(self, article_id: str, article_title: str, article_text: str, author: User,
                 image: Union[CoverImage, None]):
        self.article_id = article_id
        self.article_title = article_title
        self.article_text = article_text
        self.author = author
        self.image = image
