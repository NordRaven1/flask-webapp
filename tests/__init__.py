import unittest

from webapp.app import create_app
from webapp.db.db_functions import init_db


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config={
            "DATABASE": ":memory:",
            "TEST": "true"
        })

    def create_data(self):
        init_db()
