from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.init_helpers import (
    init_uuid4,
)
from app.models.bases import CustomBase
from app.schemas.forms import FORM_TYPE_IDS # for form_type field validation

FORM_TYPE_IDS = FORM_TYPES.keys()


class Form(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    created = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    form_type = Column(String, ForeignKey(""), nullable=False)
    submitted = Column(Boolean, nullable=False, default=False)
    # relationship
    form_parts = relationship("FormPart")


class FormPart(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    created = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now())
    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    form_type = Column(String, ForeignKey(""), nullable=False)
    form_id = Column(UUID, ForeignKey("form"), nullable=False)
    form_part_id = Column(Integer, nullable=False)
    form_data = Column(JSON, nullable=True)
    valid = Column(Boolean, nullable=False, default=False)


class FormType(CustomBae):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    form_type = Column(Integer, nullable=False)
