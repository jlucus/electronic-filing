import uuid
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.schemas.lobbyist.new_lobbyist_registration import (
    NewLobbyistRegistration,
)
from app.schemas.lobbyist.lobbyist_general import UpdateLobbyingEntity
from app.api.utility.exc import handle_exc, Http400
from app.models.filers import Filer
from app.models.users import User
from app.models.filings import Filing
from app.models.humane_ids import OBJECT_TYPES, ID_START, HumanReadableId, EFilingId


async def insert_human_readable_id(
    db_session: Session,
    *,
    object_id: str,
    object_type: str,
    hr_id_prefix: str = "",
    hr_id: str = None,
):

    if hr_id is None:
        res = (
            db_session.execute(
                select(HumanReadableId).order_by(HumanReadableId.id.desc())
            )
            .unique()
            .scalars()
            .first()
        )
        if res is None:
            hr_id = hr_id_prefix + "-" + str(ID_START)
        else:
            hr_id = hr_id_prefix + "-" + str(res.id + 1)

    new_dict = {
        "hr_id": hr_id,
        "object_id": object_id,
        "object_type": object_type,
    }

    nid = HumanReadableId(**new_dict)

    db_session.add(nid)
    db_session.commit()

    return nid


async def get_e_filer_id_by_orig_amendment(
    db_session: Session,
    amendment_ids: list,
) -> Optional[EFilingId]:

    res = (
        db_session.execute(
            select(
                Filing.amends_orig_id,
                EFilingId.e_filing_id,
            )
            .join(Filing, Filing.filing_id == EFilingId.filing_id)
            .filter(Filing.amends_orig_id.in_(amendment_ids))
        )
        .unique()
        .all()
    )

    return res


async def get_e_filer_id_by_prev_amendment(
    db_session: Session,
    amendment_ids: list,
) -> Optional[EFilingId]:

    res = (
        db_session.execute(
            select(
                Filing.amends_prev_id,
                EFilingId.e_filing_id,
            )
            .join(Filing, Filing.filing_id == EFilingId.filing_id)
            .filter(Filing.amends_prev_id.in_(amendment_ids))
        )
        .unique()
        .all()
    )

    return res