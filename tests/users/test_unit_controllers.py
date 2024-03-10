import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from users.controllers import AuthController, UsersController
from users.models import User

class TestAuthControllers(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.auth_controller = AuthController()
        self.session = MagicMock(spec=Session)

    def test_get_user(self):
        user = User()