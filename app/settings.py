from dotenv import load_dotenv
from dataclasses import dataclass
import os

load_dotenv()

# APP
APP_HOST = os.getenv('APP_HOST')
APP_PORT = int(os.getenv('APP_PORT'))

#SMTP
SMTP_SERVER=os.getenv("SMTP_SERVER")
SMTP_EMAIL=os.getenv("SMTP_EMAIL")
SMTP_PASSWORD=os.getenv("SMTP_PASSWORD")
SMTP_PORT=int(os.getenv("SMTP_PORT"))

# DATABASE SETTINGS
DB_ENGINE = os.getenv('DB_ENGINE')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT', ''))

DB_CONNECTION_STRING = f"{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# URL
BASE_URL_PREFIX = '/api'

#REDIS
REDIS_PORT = int(os.getenv('REDIS_PORT'))
REDIS_HOST = 'localhost'

#CLODUDINARY
CLOUDINARY_NAME = os.getenv("CLOUDINARY_NAME")
CLOUDINARY_KEY = os.getenv("CLOUDINARY_KEY")
CLOUDINARY_SECRET = os.getenv("CLOUDINARY_SECRET")

# TOKEN CONFIG
@dataclass(frozen=True)
class TokenConfig:
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = "HS256"
    default_expired: int = 120 # in minutes
    access_expired: int = 15 # in minutes
    refresh_expired: int = 7 * 1440 # in days
    confirmation_email_expired: int = 7 * 1440 # in days
    url: str = '/api/auth/login'

TOKEN_CONFIG = TokenConfig()
