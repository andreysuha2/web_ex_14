import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from contacts.models import Contact
from contacts.schemas import ContactModel
from users.models import User
from contacts.controllers import ContactController


class TestContactController(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.controller = ContactController()
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)
    
    async def test_list(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await self.controller.list(q="", skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_read_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await self.controller.read(id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_read_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await self.controller.read(id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create(self):
        body = ContactModel(first_name="Ivan", phone="+380331231234")
        result = await self.controller.create(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.phone, body.phone)
        self.assertTrue(hasattr(result, "id"))

    async def test_remove_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await self.controller.delete(id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await self.controller.delete(id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_found(self):
        body = ContactModel(first_name="Ivan", phone="+380331231234")
        contact = Contact(first_name="Petro", last_name="Petrenko")
        self.session.query().filter().first.return_value = contact
        result = await self.controller.update(id=1, body=body, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_not_found(self):
        body = ContactModel(first_name="Ivan", phone="+380331231234")
        self.session.query().filter().first.return_value = None
        result = await self.controller.update(id=1, body=body, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_upcoming_birthdays(self):
        # тут мав би бути тест який фільтрує тестові данні
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().all.return_value = contacts
        result = await self.controller.upcoming_birthdays(user=self.user, db=self.session)
        self.assertEqual(result, contacts)

if __name__ == "__main__":
    unittest.main()