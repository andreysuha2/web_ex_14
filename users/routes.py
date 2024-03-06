from fastapi import APIRouter, status, Depends, HTTPException, Security, BackgroundTasks, Request, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from fastapi_limiter.depends import RateLimiter
from users import schemas
from users.models import User
from typing import Annotated
from app import settings
from app.types import DBConnectionDep, AuthDep
from app.mail.confirmation_email import ConfirmationEmail
from users.controllers import AuthController, UsersController
from users.auth import auth
import cloudinary
import cloudinary.uploader

security = HTTPBearer()

auth_router = APIRouter(prefix="/auth", tags=['auth'])
user_router = APIRouter(prefix="/users", tags=['users'])

AuthControllerDep = Annotated[AuthController, Depends(AuthController)]
UsersControllerDep = Annotated[UsersController, Depends(UsersController)]

@auth_router.post("/singup", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(RateLimiter(times=1, seconds=60))])
async def singup(controller: AuthControllerDep, db: DBConnectionDep, bg_tasks: BackgroundTasks, request: Request, body: schemas.UserCreationModel):
    exist_user = await controller.get_user(email=body.email, db=db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exist')
    body.password = auth.password.hash(body.password)
    user = await controller.create(body, db)
    bg_tasks.add_task(ConfirmationEmail(email=user.email), username=user.username, host=request.base_url)
    return user

@auth_router.post('/login', response_model=schemas.TokenModel, dependencies=[Depends(RateLimiter(times=1, seconds=30))])
async def login(db: DBConnectionDep, body: OAuth2PasswordRequestForm = Depends()):
    return await auth.authenticate(body, db)

@auth_router.get('/confirmed_email/{token}')
async def confirm_email(token: str, db: DBConnectionDep, controller: AuthControllerDep):
    email = await auth.token.decode_email_confirm(token)
    user = await controller.get_user(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verefication error")
    if user.confirmed_at:
        return {"message": "Your email is already confirmed"}
    await controller.comfirm_email(email, db)
    return { "message": "Email confirmed!" }

@auth_router.post('/request_email', dependencies=[Depends(RateLimiter(times=1, seconds=30))])
async def request_email(body: schemas.RequestEmail, bg_tasks: BackgroundTasks, request: Request, db: DBConnectionDep, controller: AuthControllerDep):
    user = await controller.get_user(body.email, db)
    if user.confirmed_at:
        return {"message": "Your email is already confirmed"}
    if user:
        bg_tasks.add_task(ConfirmationEmail(body.email), username=user.username, host=request.base_url)
    return {"message": "Check your email for confirmation"}

@auth_router.get('/refresh_token', response_model=schemas.TokenModel)
async def refresh_token(db: DBConnectionDep, credentials: HTTPAuthorizationCredentials = Security(security)):
    return await auth.refresh(credentials.credentials, db)

@user_router.get("/", response_model=schemas.UserResponse)
async def read_user(user: AuthDep):
    return user

@user_router.patch("/avatar", response_model=schemas.UserResponse)
async def update_user_avatar(db: DBConnectionDep, controller: UsersControllerDep, current_user: AuthDep, file: UploadFile = File()):
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_KEY,
        api_secret=settings.CLOUDINARY_SECRET,
        security=True
    )
    public_id = f"ContactsApp/{current_user.username}"
    r = cloudinary.uploader.upload(file.file, public_id=public_id)
    src_url = cloudinary.CloudinaryImage(public_id).build_url(width=250, height=250, crop='fill', version=r.get('version'))
    user = await controller.update_avatar(current_user, src_url, db)
    return user