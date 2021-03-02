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
from sqlalchemy.dialects.postgresql import (
    JSON,
    UUID,
)
from sqlalchemy.orm import relationship
from app.models.bases import CustomBase
from app.models.init_helpers import (
    init_uuid4,
    datetime_now_utc,
)

TASK_TYPES = [
    "review_new_lobbyist"
]


class Task(CustomBase):
    id = Column(Integer, primary_key=True)
    task_ref = Column(UUID)
    task_type = Column(String, nullable=False)
    admin_task = Column(Boolean, nullable=False, server_default='f')
    assigned_to = Column(Integer, ForeignKey("user.id"), nullable=True)
    task_short = Column(String)
    task_detail = Column(String)
    task_link = Column(String)

    meta = Column(JSON)

    complete = Column(Boolean, nullable=False, server_default='f')
    completed_by_user_id = Column(Integer, ForeignKey("user.id"))

    created = Column(DateTime(timezone=True), nullable=False,
                     default=datetime_now_utc)
    updated = Column(DateTime(timezone=True), nullable=False,
                     default=datetime_now_utc)
