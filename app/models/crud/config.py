from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.config import (
    FilingConfig
)

async def get_filing_config_key(
    db_session: Session,
    key: str,
    filing_group: str,
    filing_type: str,
    year: str,
) -> Optional[FilingConfig]:
    res = db_session.execute(
        select(FilingConfig)
        .filter(FilingConfig.filing_group == filing_group)
        .filter(FilingConfig.filing_type == filing_type)
        .filter(FilingConfig.filing_year == year)
        .filter(FilingConfig.key == key)
    ).unique().scalar()

    return res
    
