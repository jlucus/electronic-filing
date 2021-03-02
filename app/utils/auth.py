import traceback
import logging
import datetime
import pytz
from passlib.context import CryptContext
import jwt
from app.core.config import (
    SECRET_KEY,
    ALGORITHM
)
from app.api.utility.exc import (
    CREDENTIALS_EXCEPTION,
    EXPIRED_CREDENTIALS_EXCEPTION
)

logger = logging.getLogger("fastapi")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: datetime.timedelta = None) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.datetime.now(tz=pytz.utc) + expires_delta
    else:
        expire = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def check_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token.token.encode(), SECRET_KEY, algorithms=[ALGORITHM])

        return payload
        
    except jwt.ExpiredSignatureError:
        logger.exception(traceback.format_exc())
        raise EXPIRED_CREDENTIALS_EXCEPTION
    except jwt.PyJWTError:
        logger.exception(traceback.format_exc())
        raise CREDENTIALS_EXCEPTION
    


