from typing import Optional
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.models.filers import Filer, FilerContactInfo, FilerFilerType
from app.schemas.filer.filer import FilerBasic, FilerContactInfoSchema


async def get_filer_by_netfile_user_id(
    db_session: Session,
    netfile_user_id: str,
):
    res = (
        db_session.execute(
            select(Filer).filter(Filer.netfile_user_id == netfile_user_id)
        )
        .unique()
        .scalar()
    )
    return res


async def get_filer_by_email(
    db_session: Session,
    email: str,
):
    res = (
        db_session.execute(select(Filer).filter(Filer.email == email)).unique().scalar()
    )
    return res


async def get_filer_by_user_id(db_session: Session, user_id: int) -> Optional[Filer]:

    res = (
        db_session.execute(select(Filer).filter(Filer.user_id == user_id))
        .unique()
        .scalar()
    )

    return res


async def get_filer_filer_type_by_filer_id(
    db_session: Session,
    filer_id: str,
):
    res = (
        db_session.execute(
            select(FilerFilerType).filter(FilerFilerType.filer_id == filer_id)
        )
        .unique()
        .scalars()
    )

    return res


async def get_all_filer_ids_by_last_name(
    db_session: Session,
    last_name: str,
):

    res = (
        db_session.execute(
            select(FilerContactInfo.filer_id).filter(
                func.lower(FilerContactInfo.last_name) == (last_name).lower()
            )
        )
        .unique()
        .scalars()
        .all()
    )

    return res

async def get_all_filer_ids_by_start_of_last_name(
    db_session: Session,
    last_name: str,
):

    search = f"{last_name.lower()}%"

    res = (
        db_session.execute(
            select(FilerContactInfo.filer_id,
                   FilerContactInfo.first_name,
                   FilerContactInfo.last_name).filter(
                func.lower(FilerContactInfo.last_name).like(search)
            )
        )
        .unique()
        .all()
    )

    return res



async def insert_new_filer_basic(
    db_session: Session, filer: FilerBasic
) -> Optional[Filer]:

    new_filer = Filer(user_id=filer.user_id)

    db_session.add(new_filer)
    db_session.flush()

    new_contact = FilerContactInfo()
    new_contact.filer_id = new_filer.filer_id
    new_contact.first_name = filer.first_name
    new_contact.middle_name = filer.middle_name
    new_contact.last_name = filer.last_name
    db_session.add(new_contact)

    db_session.commit()

    return new_filer


async def update_filer_contact_info(
    db_session: Session, filer: Filer, payload: FilerContactInfo
) -> bool:

    new_ci = FilerContactInfo()
    new_ci.filer_id = filer.filer_id
    new_ci.first_name = payload.first_name
    new_ci.middle_name = payload.middle_name
    new_ci.last_name = payload.last_name
    new_ci.address1 = payload.address1
    new_ci.address2 = payload.address2
    new_ci.city = payload.city
    new_ci.zipcode = payload.zipcode
    new_ci.state = payload.state
    new_ci.phone = payload.phone
    new_ci.country = payload.country
    new_ci.hide_details = payload.hide_details
    new_ci.effective_date = payload.effective_date

    db_session.add(new_ci)
    db_session.commit()

    return True
