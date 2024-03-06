from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session, joinedload
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import timedelta, datetime
from typing import Optional
from enum import Enum
from app.settings import TOKEN_CONFIG, TokenConfig
from app.db import get_db
from users.models import User, Token as TokenDBModel
from users import schemas
from dataclasses import dataclass
from typing import Callable, List

class TokenScopes(Enum):
    ACCESS='access_token'
    REFRESH='refresh_token'
    EMAIL_CONFIRMATION='email_confirmation_token'

class Password:
    def __init__(self, pwd_context: CryptContext):
        self.pwd_context = pwd_context

    def hash(self, password: str) -> str:
        return self.pwd_context.hash(password)
    
    def verify(self, password: str, hash: str) -> bool:
        return self.pwd_context.verify(password, hash)
    
@dataclass
class TokenCoder:
    encode: Callable[[dict, str, str], str]
    decode: Callable[[str, str, List[str]], dict]
    error: Exception
    
class Token:
    def __init__(self, config: TokenConfig, coder: TokenCoder) -> None:
        self.config = config
        self.coder = coder
         
    async def create(self, data: dict, scope: TokenScopes, expires_delta: Optional[float] = None) -> str:
        to_encode_data = data.copy()
        now = datetime.utcnow()
        expired = now + timedelta(minutes=expires_delta) if expires_delta else now + timedelta(minutes=self.config.default_expired)
        to_encode_data.update({"iat": now, "exp": expired, "scope": scope.value})
        token = self.coder.encode(to_encode_data, self.config.secret_key, algorithm=self.config.algorithm)
        return token
    
    async def decode(self, token: str, scope: TokenScopes) -> str:
        try:
            payload = self.coder.decode(token, self.config.secret_key, algorithms=[self.config.algorithm])
            if payload['scope'] == scope.value:
                return payload["sub"]
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except self.coder.error as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    async def create_access(self, data: dict, expires_delta: Optional[float] = None) -> str:
        return await self.create(data=data, scope=TokenScopes.ACCESS, expires_delta=expires_delta or self.config.access_expired)
    
    async def create_refresh(self, data: dict, expires_delta: Optional[float] = None) -> str:
        return await self.create(data=data, scope=TokenScopes.REFRESH, expires_delta=expires_delta or self.config.refresh_expired)
    
    async def create_email_confirm(self, data: dict, expires_delta: Optional[float] = None) -> str:
        return await self.create(data=data, scope=TokenScopes.EMAIL_CONFIRMATION, expires_delta=expires_delta or self.config.confirmation_email_expired)

    async def decode_access(self, token: str) -> str:
        return await self.decode(token, TokenScopes.ACCESS)

    async def decode_refresh(self, token: str) -> str:
        return await self.decode(token, TokenScopes.REFRESH)
    
    async def decode_email_confirm(self, token: str) -> str:
        return await self.decode(token, TokenScopes.EMAIL_CONFIRMATION)

class Auth:
    oauth2_scheme = OAuth2PasswordBearer(TOKEN_CONFIG.url)
    user_model = User
    tokens_model = TokenDBModel
    invalid_credential_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid username or password')
    invalid_confirmation_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email not confirmed')
    invalid_refresh_token_error = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid refresh token')
    credentionals_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    def __init__(self, password: Password, token: Token) -> None:
        self.password = password
        self.token = token

    def validate(self, user: user_model | None, credentials: OAuth2PasswordRequestForm) -> bool:
        if user is None:
            return False
        if not self.password.verify(credentials.password, user.password):
            return False
        return True
    
    async def refresh(self, refres_token_str: str, db: Session) -> schemas.TokenModel:
        email = await self.token.decode_refresh(refres_token_str)
        refres_token = db.query(self.tokens_model).filter(
            self.tokens_model.token==refres_token_str
            ).options(joinedload(self.tokens_model.user)).first()
        user = await self.__get_user(email, db)
        if refres_token:
            db.delete(refres_token)
            db.commit()
        print(user, refres_token)
        if user is None or refres_token is None or refres_token.user != user:
            raise self.credentionals_exception
        return await self.__generate_tokens(user, db)
        
    async def authenticate(self, credentials: OAuth2PasswordRequestForm, db: Session) -> schemas.TokenModel:
        user = await self.__get_user(credentials.username, db)
        if not self.validate(user, credentials):
            raise self.invalid_credential_error
        if user.confirmed_at is None:
            raise self.invalid_confirmation_error
        return await self.__generate_tokens(user, db)
    
    async def __generate_tokens(self, user: user_model, db: Session) -> schemas.TokenModel:
        access_token_str = await self.token.create_access({"sub": user.email})
        refresh_token_str = await self.token.create_refresh({"sub": user.email})
        refresh_token = self.tokens_model(token=refresh_token_str)
        user.tokens.append(refresh_token)
        db.commit()
        return { "access_token": access_token_str, "refresh_token": refresh_token.token, type: "bearer" }
        
    async def __get_user(self, email: str, db: Session) -> user_model | None:
        return db.query(self.user_model).filter(self.user_model.email == email).first()

    async def __call__(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> user_model:
        email = await self.token.decode_access(token)
        if email is None:
            raise self.credentionals_exception
        user = await self.__get_user(email, db)
        if user is None:
            raise self.credentionals_exception
        return user
        

auth = Auth(
    password=Password(CryptContext(schemes=['bcrypt'], deprecated='auto')),
    token=Token(config=TOKEN_CONFIG, coder=TokenCoder(encode=jwt.encode, decode=jwt.decode, error=JWTError))
)