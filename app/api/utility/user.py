import logging
import traceback
import secrets
import datetime
import pytz
from typing import Optional
import jwt
from fastapi import (
    Depends,
    HTTPException,
    Request,
    Response,
)
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from app.api.utility.exc import (
    CREDENTIALS_EXCEPTION,
    AccountException
)
from app.core.config import (
    AuthJWTSettings,
    SECRET_KEY,
    ALGORITHM,
    PASSWORD_RESET_EXPIRE_MINS,
    EMAIL_TEMPLATES,
    FRONTEND_ROUTES,
    APP_HOST,
    EFILE_EMAIL
)
from app.schemas.user.user import (
    UserResetPassword,
    ResetPasswordRequest
)
from app.schemas.token import TokenData
from app.core.security import (
    verify_password,
    get_password_hash
)
from app.db.utils import get_db
from app.utils.auth import (
    create_access_token,
    check_access_token
)
from app.models.users import User
from app.models.crud.user import (
    get_admin_user_by_email,
    get_filer_user_by_email,
    get_user_by_email
)
from app.api.utility.exc import (
    Http400,
    Http500,
    handle_exc,
    CREDENTIALS_EXCEPTION,
    AccountException
)
from app.api.utility.emails import (
    send_templated_email_disk,
)

logger = logging.getLogger("fastapi")

@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()

# user accessors

async def get_current_user(
    request: Request,
    response: Response,
    db_session: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):

    try:
        Authorize.jwt_required()
    except Exception as e:
        traceback.print_exc()
        raise

    token = Authorize.get_raw_jwt()

    # admin user
    admin = token.get('admin', False)
    if admin:
        user = get_admin_user_by_email(db_session, token.get('sub'))
        if user is None:
            raise CREDENTIALS_EXCEPTION
        return user

    filer = token.get('filer', False)
    if filer:
        user = get_filer_user_by_email(db_session, token.get('sub'))
        if user is None:
            raise CREDENTIALS_EXCEPTION
        return user


    raise CREDENTIALS_EXCEPTION


async def get_active_user(user: User = Depends(get_current_user) ):
    if not user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

async def get_active_admin_user(user: User = Depends(get_current_user) ):
    if not user.active:
        raise HTTPException(status_code=400, detail="Inactive user.")
    if not user.account_type == "admin":
        raise HTTPException(status_code=400, detail="Not an admin user.")
    return user


async def get_active_user_from_cookie(
    request: Request,
    db_session: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):

    Authorize.jwt_refresh_token_required()
    token = Authorize.get_raw_jwt()

    # admin user
    admin = token.get('admin', False)
    if admin:
        user = get_admin_user_by_email(db_session, token.get('sub'))
        if user is None or not user.active:
            raise CREDENTIALS_EXCEPTION
        return user

    filer = token.get('filer', False)
    if filer:
        user = get_filer_user_by_email(db_session, token.get('sub'))
        if user is None or not user.active:
            raise CREDENTIALS_EXCEPTION
        return user

    raise CREDENTIALS_EXCEPTION



# authentication

def authenticate_admin_user(
    db_session: Session, email: str, password: str):
    user = get_admin_user_by_email(db_session, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

def authenticate_filer_user(
    db_session: Session, email: str, password: str):
    user = get_filer_user_by_email(db_session, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def saml_verify_admin_user(
    db_session: Session,
    email: str
):
    user = get_admin_user_by_email(db_session, email)
    if not user or not user.city:
        return False
    return user


def create_access_token(*, data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.datetime.now(tz=pytz.utc) + expires_delta
    else:
        expire = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_access_token(db_session: Session, form):
    user = authenticate_user(db_session, form.username, form.password)

    if not user:
        logging.info("Unregistered user attempted login: '%s'", form.username)
        raise CREDENTIALS_EXCEPTION

    access_token_expires = datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    if access_token:
        try:
            user.last_login = datetime.datetime.now(tz=pytz.utc)
            db_session.add(user)
            db_session.commit()
        except Exception as inst:
            logging.error("Exception: e = %s", inst)
            db_session.rollback()

    logging.info("Access token granted to user '%s'", form.username)
    return access_token


async def set_user_password(
    db_session: Session,
    payload: UserResetPassword
):

    res = check_access_token(payload)
    logger.info(f"Reset password: {res}")

    
    if 'sub' not in res.keys() or 'email_code' not in res.keys():
        raise Http400(detail="Missing user information in token.")
        
    user_email = res['sub']
    email_code = res['email_code']

    user = get_user_by_email(db_session, user_email)

    if user is None:
        logger.info(f"User {email} does not exist. Password reset fail.")
        return True

    if not user.active:
        # user isn't active
        logger.info(f"User {email} is inactive. Password reset fail.")
        raise AccountException(detail="User is not active. "\
                               "Please contact City Clerk's Office.") 

    if user.city:
        logger.info(f"User {email} is City user. Password reset fail.")
        raise AccountException(detail="sandiego.gov passwords cannot be reset here.")

    if user.password_set_reset_secret != email_code:
        logger.info(f"User {email} wrong reset code. Password reset fail.")
        raise Http401(detail="Invalid credentials.")

    hashed_password = get_password_hash(payload.password)
    user.password_hash = hashed_password

    db_session.commit()

    return True

async def user_password_reset_request(
    db_session: Session,
    payload: ResetPasswordRequest
):
    user_email = payload.email
    user = get_user_by_email(db_session, user_email)

    # we don't tell the submitter if the account doesn't exist
    if user is None:
        logger.info(f"User {email} does not exist. Password reset fail.")
        return True
        # raise AccountException(detail="User does not exist.")

    if not user.active:
        # user isn't active
        logger.info(f"User {email} is inactive. Password reset fail.")
        return True

    if user.city:
        logger.info(f"User {email} is City user. Password reset fail.")
        raise AccountException(detail="sandiego.gov passwords cannot be reset here.")

    # okay, let's build the token and send the email
    user.password_set_reset_secret = secrets.token_hex(16)
    now = datetime.datetime.now(tz=pytz.utc)
    access_token_expires = datetime.timedelta(
        minutes=PASSWORD_RESET_EXPIRE_MINS
    )
    user.password_set_reset_expire = now + access_token_expires
    data = {
        "sub": user.email,
        "email_code": user.password_set_reset_secret,
        "endpoint": FRONTEND_ROUTES["user_set_password"]
    }
    
    access_token = create_access_token(
        data=data,
        expires_delta=access_token_expires
    ).decode('UTF-8')

    print(access_token)
    
    url = (
        APP_HOST + FRONTEND_ROUTES["user_set_password"] +
        f"?token={access_token}"
    )

    # get message template
    template = EMAIL_TEMPLATES["password_set_reset_email"]

    recipients = [user.email]

    data = {"url": url}
    
    await send_templated_email_disk(
        db_session=db_session,
        data=data,
        template_name=template,
        message_type="password_set_reset_email",
        subject="[eFile San Diego] Password Reset",
        sender=EFILE_EMAIL,
        recipients=recipients,
        to_id=user.id,
    )
    

    return True
    
