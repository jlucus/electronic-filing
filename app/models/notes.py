from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    JSON,
    DateTime,
    ForeignKey,
    Table,
    Date,
    Index
)
from sqlalchemy.dialects.postgresql import (
    JSON,
    UUID,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.bases import CustomBase
from app.models.init_helpers import (
    init_uuid4,
)

# portal -- admin facing
# profile -- filer facing

# note data model
# Some scenarios:
# Admin writes internal note on filer portal
# Admin writes internal note on entity portal
# Filer writes note and shares doc for admin
# Admin writes note for filer/entity, with document

# NOTE: for now, we only implement the following:
# Admins can write notes and add attachments to portals, not shared with filer
# Filer can write notes and add attachments to portals, always visible to admin

class Note(CustomBase):
    note_id = Column(UUID, primary_key=True, default=init_uuid4)
    content = Column(String)
    
    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True),
                     nullable=False, default=func.now(),
                     onupdate=func.now())

    attachments = relationship("NoteDocument")
    
# note will be attached to filer or entity, not both, can't have a
# foreign key here, though
class NoteFilerOrEntity(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filer_or_entity_id = Column(UUID, nullable=False)
    note_id = Column(UUID, ForeignKey("note.note_id"), nullable=False)
    __table_args__ = (
        Index('idx_nfe_note_id', 'note_id'),
    )
    
class NoteDocument(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    note_id = Column(UUID, ForeignKey("note.note_id"), nullable=False)
    doc_id = Column(String, ForeignKey("document.doc_id"), nullable=False)
    archived = Column(Boolean)
    __table_args__ = (
        Index('idx_nd_note_id', 'note_id'),
    )
