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

DOC_TYPES = [
    "electronic filing",
    "uploaded filing",
    "filer upload",
    "portal attachment",
]

class Document(CustomBase):

    id = Column(Integer,primary_key=True)
    doc_id = Column(String, nullable=False, unique=True)
    doc_type = Column(String)
    mime_type = Column(String)
    size_bytes = Column(Integer)
    filename = Column(String)
    s3bucket = Column(String)
    s3key = Column(String)
    public = Column(Boolean, nullable=False, server_default='f')
    uploader_user_id = Column(Integer, ForeignKey("user.id"))

    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True),
                     nullable=False, default=func.now(),
                     onupdate=func.now())

    __table_args__ = (
        Index('idx_doc_id', 'doc_id'),
    )
    
# class DocumentPermission
# TBD
