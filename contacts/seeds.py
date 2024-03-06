from sqlalchemy.orm import Session
from app.db import get_db
from contacts.models import Contact
from users.models import User
from datetime import timedelta, datetime
from typing import List
import random
import faker

fake_data: faker.Faker = faker.Faker()

COUNT_CONTACTS = 100
PHONES_CODES = ['073', '063', '050', '067', '066', '096', '093', '099']

def create_contacts(count: int) -> List[dict]:
    contacts = []       
    for _ in range(count):
        additional_data = None
        if bool(random.getrandbits(1)):
            additional_data = fake_data.paragraph(nb_sentences=1)
        contacts.append({
            "first_name": fake_data.first_name(),
            "last_name": fake_data.last_name(),
            "email": fake_data.email(),
            "birthday": fake_data.date(end_datetime=datetime.now() - timedelta(days=5*365)),
            "phone": f"+38{random.choice(PHONES_CODES)}{fake_data.msisdn()[6:]}",
            "additional_data": additional_data
        })
    return contacts

def upload_contacts(db: Session, contacts: List[dict]) -> None:
    users = db.query(User).all()
    for contact_data in contacts:
        contact = Contact(**contact_data, user = random.choice(users))
        db.add(contact)
    db.commit()
    
def main():
    contacts = create_contacts(COUNT_CONTACTS)
    upload_contacts(db=next(get_db()), contacts=contacts)

if __name__ == "__main__":
    main()