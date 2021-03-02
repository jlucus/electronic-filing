from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    JSON,
    DateTime,
    Date,
    ForeignKey,
    Table,
    Sequence,
    Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.init_helpers import (
    init_uuid4,
)
from app.models.bases import CustomBase


class FilingConfig(CustomBase):

    id = Column(Integer, primary_key=True)
    # lobbyist, sei
    filing_group = Column(String, nullable=False)
    filing_type = Column(String)
    filing_year = Column(String)
    key = Column(String)
    value = Column(String)
    pytype = Column(String)
    
    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True),
                     nullable=False, default=func.now(),
                     onupdate=func.now())
