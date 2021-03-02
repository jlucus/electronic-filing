from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    JSON,
    DateTime,
    ForeignKey,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.init_helpers import (
    init_uuid4,
)
from app.models.bases import CustomBase


class Organization(CustomBase):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created = Column(DateTime(timezone=True), nullable=False, default=func.now())


class Department(CustomBase):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    created = Column(DateTime(timezone=True), nullable=False, default=func.now())
                             

class Position(CustomBase):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    organization_id = Column(Integer, ForeignKey('organization.id'))
    department_id = Column(Integer, ForeignKey('department.id'))
    is_87200 = Column(Boolean, nullable=False, server_default='f')
    created = Column(DateTime(timezone=True), nullable=False, default=func.now())

