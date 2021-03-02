import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__))+'/../backend/')
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.session import db_session
from app.models.filings import (
    Filing,
    FilingRaw,
    FilingSubtype
)
from app.models.filers import (
    Filer,
    FilerFilerType,
    FilerContactInfo
)


def remove_filing(db_session, filing_id):

    res = db_session.execute(
        select(FilingSubType)
        .filter(FilingSubtype.filing_id == filing_id)
    ).unique().scalars().all()

    for subtype in res:
        db_session.delete(res)

    res = db_session.execute(
        select(FilingRaw)\
        .filter(FilingRaw.filing_id == filing_id)
    ).unique().scalars().all()

    for raw in res:
        db_session.delete(res)

    res = db_session.execute(
        select(Filing)\
        .filter(Filing.filing_id == filing_id)
    ).unique().scalars().all()
    
    for filing in res:
        db_session.delete(res)

    db_session.commit()
