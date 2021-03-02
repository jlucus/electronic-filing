from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    JSON,
    DateTime,
    ForeignKey,
    Table,
    Date
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

RESOURCE_TYPES = [
    "note"
]

PERMISSIONS = {
    0: "read only",
    1: "update",
    2: "delete"
}


class Permission(CustomBase):

    resource_id = Column(UUID, primary_key=True, default=init_uuid4)
    filer_or_entity_id = Column(UUID, nullable=False)
    resource_type = Column(String, nullable=False)
    permission = Column(Integer, nullable=False)
