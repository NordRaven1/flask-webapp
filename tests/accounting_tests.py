from tests import BaseTestCase
from webapp.db.accounting_functions import register_user, find_user_by_email


class AccountingTests(BaseTestCase):

    def test_registration(self):
        login, email, password = "ivan", "ivan@mail.com", "qwerty123"
        with self.app.app_context():
            self.create_data()
            self.assertIsNone(find_user_by_email(email))
            register_user(login, email, password)
            user = find_user_by_email(email)
            self.assertEqual(login, user.login)
            self.assertEqual(email, user.email)
            self.assertTrue(user.check_password(password))