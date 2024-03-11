import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from users.controllers import AuthController, UsersController
from users.models import User
from users.schemas import UserCreationModel
from contacts.models import Contact

class TestAuthControllers(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.controller = AuthController()
        self.session = MagicMock(spec=Session)

    async def test_get_user_found(self):
        user = User()
        self.session.query().filter().first.return_value = user
        result = await self.controller.get_user(email="test@mail.com", db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await self.controller.get_user(email="test@mail.com", db=self.session)
        self.assertIsNone(result)

    async def test_confirm_email(self):
        user = User()
        with patch.object(self.controller, "get_user") as get_user_mock:
            get_user_mock.return_value = user
            result = await self.controller.comfirm_email(email="test@mail.com", db=self.session)
            self.assertIsInstance(user.confirmed_at, datetime)
            self.assertIsNone(result)

    async def test_create(self):
        body = UserCreationModel(username="username", email="test@mail.com", password="123123123")
        result = await self.controller.create(body=body, db=self.session)
        self.assertEqual(body.username, result.username)
        self.assertEqual(body.email, result.email)
        self.assertEqual(body.password, result.password)

class TestUserController(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.controller = UsersController()
        self.session = MagicMock(spec=Session)
    
    async def test_update_avatar(self):
        user = User()
        url = "https://test.url"
        result = await self.controller.update_avatar(user=user, url=url, db=self.session)
        self.assertEqual(result.avatar, url)

if __name__ == "__main__":
    unittest.main()