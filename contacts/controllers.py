from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.db import has_date_next_days
from users.models import User
from contacts.models import Contact
from contacts import schemas
from typing import List

class ContactController:
    base_model = Contact
    user_model = User

    async def list(self, q: str,  skip: int, limit: int, user: user_model, db: Session) -> List[base_model]:
        """
        Retrieves a list of contacts for a specific user with specified pagination parameters.

        :param q: query string
        :type q: str
        :param skip: The number of notes to skip.
        :type skip: int
        :param limit: The maximum number of notes to return.
        :type limit: int
        :param user: The user to retrieve notes for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: A list of contacts.
        :rtype: List[Contact]
        """
        query = db.query(self.base_model).filter(self.base_model.user == user)
        if q:
            query = query.filter(or_(
                self.base_model.first_name.like(f'{q}%'),
                self.base_model.last_name.like(f'{q}%'),
                self.base_model.email.like(f'{q}%'))
            )
        return query.offset(skip).limit(limit).all()

    async def create(self, user: user_model, body: schemas.ContactModel, db: Session) -> base_model:
        """
        Creates a new contact for a specific user.

        :param body: The data for the contact to create.
        :type body: ContactModel
        :param user: The user to create the note for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The newly created contact.
        :rtype: Contact
        """
        contact = self.base_model(**body.model_dump(), user=user)
        db.add(contact)
        db.commit()
        db.refresh(contact)
        return contact
        
    async def read(self, user: user_model, id: int, db: Session) -> base_model |  None:
        """
        Retrieves a single contact with the specified ID for a specific user.

        :param id: The ID of the contact to retrieve.
        :type id: int
        :param user: The user to retrieve the note for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The contact with the specified ID, or None if it does not exist.
        :rtype: Contact | None
        """
        return db.query(self.base_model).filter(self.base_model.id == id, self.base_model.user == user).first()
    
    async def update(self, user: user_model, id: int, body: schemas.ContactModel, db: Session) -> base_model | None:
        """
        Updates a single contact with the specified ID for a specific user.

        :param id: The ID of the contact to update.
        :type id: int
        :param body: The updated data for the note.
        :type body: NoteUpdate
        :param user: The user to update the note for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The updated contact, or None if it does not exist.
        :rtype: Contact | None
        """
        contact = db.query(self.base_model).filter(self.base_model.id == id, self.base_model.user == user).first()
        if contact:
            for key, value in body.model_dump().items():
                setattr(contact, key, value)
            db.commit()
        return contact
    
    async def delete(self, user: user_model, id: int, db: Session) -> base_model | None:
        """
        Removes a single contact with the specified ID for a specific user.

        :param id: The ID of the contact to remove.
        :type id: int
        :param user: The user to remove the note for.
        :type user: User
        :param db: The database session.
        :type db: Session
        :return: The removed contact, or None if it does not exist.
        :rtype: Contact | None
        """
        contact = db.query(self.base_model).filter(self.base_model.id == id, self.base_model.user == user).first()
        if contact:
            db.delete(contact)
            db.commit()
        return contact
    
    async def upcoming_birthdays(self, user: user_model, db: Session, days: int = 7) -> List[base_model]:
        return db.query(self.base_model).filter(has_date_next_days(self.base_model.birthday, days), self.base_model.user == user).all()