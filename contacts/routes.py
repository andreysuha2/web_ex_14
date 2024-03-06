from fastapi import APIRouter, HTTPException, Depends, status
from app.types import DBConnectionDep, AuthDep
from typing import Annotated, List
from contacts.controllers import ContactController 
from contacts import schemas
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix='/contacts', tags=['contacts'])
ContactControllerDep = Annotated[ContactController, Depends(ContactController)]

@router.get('/', response_model=List[schemas.ContactResponse])
async def contacts_list(
        user: AuthDep,
        controller: ContactControllerDep,
        db: DBConnectionDep, 
        q: str = '', 
        skip: int = 0, 
        limit: int = 100
    ):
    return await controller.list(user=user, skip=skip, limit=limit, db=db, q=q)

@router.post('/', response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def create_contact(user: AuthDep, controller: ContactControllerDep, db: DBConnectionDep, body: schemas.ContactModel):
    return await controller.create(user=user, body=body, db=db)

@router.get('/upcoming_birthdays', response_model=List[schemas.ContactResponse])
async def get_upcoming_birthdays(user: AuthDep, controller: ContactControllerDep, db: DBConnectionDep, days: int = 7):
    return await controller.upcoming_birthdays(user=user, db=db, days=days)

@router.get('/{contact_id}', response_model=schemas.ContactResponse)
async def read_contact(user: AuthDep, controller: ContactControllerDep, db: DBConnectionDep, contact_id: int):
    contact = await controller.read(user=user, id=contact_id, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return contact

@router.put('/{contact_id}', response_model=schemas.ContactResponse, dependencies=[Depends(RateLimiter(times=1, seconds=10))])
async def update_contact(user: AuthDep, controller: ContactControllerDep, db: DBConnectionDep, body: schemas.ContactModel, contact_id: int):
    contact = await controller.update(user=user, id=contact_id, body=body, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return contact

@router.delete('/{contact_id}', response_model=schemas.ContactResponse)
async def delete_contact(user: AuthDep, controller: ContactControllerDep, db: DBConnectionDep, contact_id: int):
    contact = await controller.delete(user=user, id=contact_id, db=db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return contact