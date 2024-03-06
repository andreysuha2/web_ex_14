from pydantic import Field, BaseModel, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from datetime import date
from typing import Optional

PhoneNumber.phone_format = 'E164'

class ContactModel(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = Field(None, max_length=50)
    phone: Optional[PhoneNumber] = Field(None, max_length=13)
    birthday: Optional[date] = None
    additional_data: Optional[str] = Field(None, max_length=255)

class ContactResponse(ContactModel):
    id: int
      
    class Config:
        from_attributes = True