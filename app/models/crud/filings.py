from typing import Optional
from sqlalchemy import select
from sqlalchemy.sql import func, and_, or_
from sqlalchemy.orm import Session
from app.utils.date_utils import today
from app.models.filings import Filing, FilingRaw, FilingSubtype
from app.models.filers import Filer, FilerContactInfo
from app.models.entities import LobbyingEntityContactInfo

FILED_STATUS = ["filed fee pending", "filed"]

# pull data
async def get_filing_by_id_and_type(
    db_session: Session, filing_id: str, filing_type: str
) -> Optional[Filing]:
    res = (
        db_session.execute(
            select(Filing)
            .filter(Filing.filing_id == filing_id)
            .filter(Filing.filing_type == filing_type)
        )
        .unique()
        .scalar()
    )

    return res


async def get_filing_by_id(
    db_session: Session,
    filing_id: str,
) -> Optional[Filing]:
    res = (
        db_session.execute(select(Filing).filter(Filing.filing_id == filing_id))
        .unique()
        .scalar()
    )

    return res


async def get_latest_filing_by_entity_id_and_filing_type_and_year(
    db_session: Session, entity_id: str, filing_type: str, year: str
):
    period_start = year + "-01-01"
    period_end = year + "-12-31"
    res = (
        db_session.execute(
            select(Filing)
            .filter(Filing.entity_id == entity_id)
            .filter(Filing.filing_type == filing_type)
            .filter(Filing.period_start >= period_start)
            .filter(Filing.period_end <= period_end)
            .order_by(
                Filing.filing_date.desc(),
                Filing.updated.desc(),
                Filing.e_filing_id.desc(),
            )
        )
        .unique()
        .scalars()
        .first()
    )

    return res


async def get_all_filings_by_filer_id(
    db_session: Session, filer_id: str, start_date: str, end_date: str
) -> Optional[Filing]:

    res = (
        db_session.execute(
            select(
                Filing.filing_date,
                FilerContactInfo.first_name,
                FilerContactInfo.last_name,
                Filing.filing_type,
                Filing.doc_public,
            )
            .join(Filer, Filer.filer_id == Filing.filer_id)
            .join(FilerContactInfo, Filer.filer_id == FilerContactInfo.filer_id)
            .filter(Filing.filer_id == filer_id)
            .filter(
                and_(Filing.period_start >= start_date, Filing.period_end < end_date)
            )
        )
        .unique()
        .all()
    )

    return res


async def get_all_filings_by_all_filer_ids(
    db_session: Session, filer_ids: list, start_date: str = None, end_date: str = None
) -> Optional[Filing]:

    if start_date is None:
        start_date = "1970-01-01"
    if end_date is None:
        end_date = today().isoformat()

    res = (
        db_session.execute(
            select(
                Filing.filing_date,
                Filing.filing_type,
                Filing.doc_public,
                Filing.amendment,
                Filing.amends_orig_id,
                Filing.amends_prev_id,
                Filing.amendment_number,
                FilingSubtype.filing_subtype,
                FilerContactInfo.first_name,
                FilerContactInfo.last_name,
            )
            .join(FilingSubtype, FilingSubtype.filing_id == Filing.filing_id)
            .join(Filer, Filer.filer_id == Filing.filer_id)
            .join(FilerContactInfo, FilerContactInfo.filer_id == Filer.filer_id)
            .filter(Filing.filer_id.in_(filer_ids))
            .filter(
                or_(
                    and_(
                        Filing.filing_date >= start_date, Filing.filing_date <= end_date
                    ),
                    and_(
                        Filing.period_start >= start_date,
                        Filing.period_start <= end_date,
                    ),
                )
            )
            .order_by(
                Filing.filing_date.desc(),
            )
        )
        .unique()
        .all()
    )

    return res


async def get_all_lobbyist_filings_by_all_filer_ids(
    db_session: Session, filer_ids: list, start_date: str = None, end_date: str = None
) -> Optional[Filing]:

    if start_date is None:
        start_date = "1970-01-01"
    if end_date is None:
        end_date = today().isoformat()

    res = (
        db_session.execute(
            select(
                Filing.filing_date,
                Filing.filing_type,
                Filing.doc_public,
                Filing.amendment,
                Filing.amends_orig_id,
                Filing.amends_prev_id,
                Filing.amendment_number,
                LobbyingEntityContactInfo.name.label("filer"),
            )
            .join(
                LobbyingEntityContactInfo,
                LobbyingEntityContactInfo.entity_id == Filing.entity_id,
            )
            .filter(Filing.filer_id.in_(filer_ids))
            .filter(
                or_(
                    and_(
                        Filing.filing_date >= start_date, Filing.filing_date <= end_date
                    ),
                    and_(
                        Filing.period_start >= start_date,
                        Filing.period_start <= end_date,
                    ),
                )
            )
            .order_by(
                Filing.filing_date.desc(),
            )
        )
        .unique()
        .all()
    )

    return res


async def get_filing_by_public_doc(
    db_session: Session, doc_public: str
) -> Optional[Filing]:
    res = (
        db_session.execute(select(Filing).filter(Filing.doc_public == doc_public))
        .unique()
        .scalar()
    )

    return res


async def get_filing_metadata_by_public_doc(
    db_session: Session, doc_public: str
) -> Optional[Filing]:
    res = (
        db_session.execute(
            select(
                Filing.filing_date,
                Filing.filing_type,
                Filing.amendment,
                Filing.filing_id,
                Filing.e_filing_id,
                FilingSubtype.filing_subtype,
                FilerContactInfo.first_name,
                FilerContactInfo.last_name,
            )
            .join(Filer, Filer.filer_id == Filing.filer_id)
            .join(FilingSubtype, FilingSubtype.filing_id == Filing.filing_id)
            .join(FilerContactInfo, FilerContactInfo.filer_id == Filer.filer_id)
            .filter(Filing.doc_public == doc_public)
        )
        .unique()
        .first()
    )

    return res


async def get_lobbyist_filing_metadata_by_public_doc(
    db_session: Session, doc_public: str
) -> Optional[Filing]:

    res = (
        db_session.execute(
            select(
                Filing.filing_date,
                Filing.filing_type,
                Filing.amendment,
                Filing.e_filing_id,
                Filing.filing_id,
                LobbyingEntityContactInfo.name,
            )
            .join(
                LobbyingEntityContactInfo,
                LobbyingEntityContactInfo.entity_id == Filing.entity_id,
            )
            .filter(Filing.doc_public == doc_public)
        )
        .unique()
        .first()
    )

    return res


async def get_lobbyist_filing_by_public_doc(
    db_session: Session, doc_public: str
) -> Optional[Filing]:
    res = (
        db_session.execute(
            select(
                Filing.filing_type,
                Filing.filing_date,
            )
            .join(Filer, Filer.filer_id == Filing.filer_id)
            .filter(Filing.doc_public == doc_public)
        )
        .unique()
        .scalar()
    )

    return res


async def get_raw_filing_by_id(
    db_session: Session, filing_id: str
) -> Optional[FilingRaw]:

    res = (
        db_session.execute(select(FilingRaw).filter(FilingRaw.filing_id == filing_id))
        .unique()
        .scalar()
    )

    return res


# insert
async def create_new_filing(db_session: Session, filing_dict: dict) -> Optional[Filing]:

    new_filing = Filing(**filing_dict)
    db_session.add(new_filing)
    db_session.commit()

    return new_filing


async def upsert_raw_filing(
    db_session: Session, filing_dict: dict
) -> Optional[FilingRaw]:

    # because our change is in json, we need
    # to actually manually get the object and change it
    filing_raw = (
        db_session.execute(
            select(FilingRaw).filter(FilingRaw.filing_id == filing_dict["filing_id"])
        )
        .unique()
        .scalar()
    )

    if filing_raw is None:
        filing_raw = FilingRaw()
        filing_raw.filing_id = filing_dict["filing_id"]

    filing_raw.raw_json = filing_dict
    db_session.add(filing_raw)
    db_session.commit()

    return filing_raw
