from pydantic import Field, BaseModel, EmailStr
from datetime import datetime
from contacts.schemas import ContactResponse
from typing import List

class UserCreationModel(BaseModel):
    username: str = Field(min_length=5, max_length=16, pattern="^\\w+$")
    email: EmailStr
    password: str = Field(min_length=6)

class UserModer(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str
    created_at: datetime

class UserResponse(UserModer):
    contacts: List[ContactResponse]

    class Config:
        from_attributes = True

class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = 'bearer'

class RequestEmail(BaseModel):
    email: EmailStr
