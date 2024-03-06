from libgravatar import Gravatar
from users.models import User
from sqlalchemy.orm import Session
from users import schemas
from datetime import datetime

class AuthController:
    base_model = User

    async def get_user(self, email: str, db: Session) -> base_model | None:
        return db.query(self.base_model).filter(self.base_model.email == email).first()
    
    async def comfirm_email(self, email, db: Session) -> None:
        user = await self.get_user(email, db)
        user.confirmed_at = datetime.now()
        db.commit()
    
    async def create(self, body: schemas.UserCreationModel, db: Session) -> base_model:
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print("Avatar exception:", e)
        user = self.base_model(**body.model_dump(), avatar=avatar)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
class UsersController:
    base_model = User

    async def update_avatar(self, user: base_model, url: str, db: Session):
        user.avatar = url
        db.commit()
        return user