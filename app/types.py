from sqlalchemy.orm import Session
from fastapi import Depends
from app.db import get_db
from users.auth import auth
from typing import Annotated

AuthDep = Annotated[auth, Depends(auth)]
DBConnectionDep = Annotated[Session, Depends(get_db)]