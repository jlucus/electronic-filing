from sqlalchemy import (
    select,
    Column,
    Integer,
    String,
    Boolean,
    JSON,
    DateTime,
    ForeignKey,
    Table,
    Sequence
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.bases import CustomBase

OBJECT_TYPES = [
    "filer",
    "lobbying_entity",
    "campaign_entity"
]

ID_START=30000

ID_SEQ = Sequence('human_readable_id_seq', minvalue=ID_START, start=ID_START)
class HumanReadableId(CustomBase):
    id = Column(Integer, ID_SEQ, primary_key=True,
                server_default=ID_SEQ.next_value())
    hr_id = Column(String, nullable=False, unique=True)
    object_id = Column(UUID, nullable=False, unique=True)
    object_type = Column(String, nullable=False)
    

ID_START2=200000000
ID_SEQ2 = Sequence('human_readable_filing_id_seq',
                   minvalue=ID_START2, start=ID_START2)
class EFilingId(CustomBase):
    id = Column(Integer, ID_SEQ2, primary_key=True,
                server_default=ID_SEQ2.next_value())
    e_filing_id = Column(String, nullable=False, unique=True)
    filing_id = Column(UUID, nullable=False, unique=True)

