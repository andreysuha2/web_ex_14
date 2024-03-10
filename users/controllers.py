from libgravatar import Gravatar
from users.models import User
from sqlalchemy.orm import Session
from users import schemas
from datetime import datetime

class AuthController:
    base_model = User

    async def get_user(self, email: str, db: Session) -> base_model | None:
        """
        Retrieves a single user with the specified email.

        :param email: The email of the user to retrieve.
        :type email: str
        :param db: The database session.
        :type db: Session
        :return: The user with the specified email, or None if it does not exist.
        :rtype: User | None
        """
        return db.query(self.base_model).filter(self.base_model.email == email).first()
    
    async def comfirm_email(self, email, db: Session) -> None:
        """
        Add flag as confirmed user

        :param email: The email of the user who should be confirmed.
        :type email: str
        :param db: The database session.
        :type db: Session
        :return: None.
        :rtype: None
        """
        user = await self.get_user(email, db)
        user.confirmed_at = datetime.now()
        db.commit()
    
    async def create(self, body: schemas.UserCreationModel, db: Session) -> base_model:
        """
        Creates a new user.

        :param body: The data for the user to create.
        :type body: UserCreationModel
        :param db: The database session.
        :type db: Session
        :return: The newly created user.
        :rtype: User
        """
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