from typing import Optional
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.models.users import User
from app.schemas.user.user import UserBasic


# get user


def get_admin_user_by_email(db_session: Session, email: str) -> Optional[User]:

    res = db_session.execute(
        select(User)
        .filter(User.email == email)
        .filter(User.account_type == "admin")
    ).unique().scalar()

    return res

def get_all_active_admin_users(db_session):
    res = db_session.execute(
        select(User)
        .filter(User.account_type == "admin")
        .filter(User.active == True)
    ).unique().scalars().all()

    return res

def get_filer_user_by_email(
    db_session: Session,
    email: str
) -> Optional[User]:

    res = db_session.execute(
        select(User)
        .filter(User.email == email)
        .filter(User.account_type == "filer")
    ).unique().scalar()

    return res

def get_user_by_email(
    db_session: Session,
    email: str
) -> Optional[User]:

    res = db_session.execute(
        select(User)
        .filter(User.email == email)
    ).unique().scalar()

    return res

# insert

async def insert_new_user(
    db_session: Session,
    user_data: UserBasic
) -> Optional[User]:

    new_user = User(**jsonable_encoder(user_data))

    db_session.add(new_user)
    db_session.commit()

    return new_user
