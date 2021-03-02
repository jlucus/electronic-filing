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
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.bases import CustomBase
from app.models.init_helpers import (
    init_uuid4,
)

MESSAGE_TYPES = [
    "lobbyist_new_admin_notify",
    "lobbyist_email_confirmation",
    "lobbyist_new_welcome",
    "one-off"
]


class Message(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    sender = Column(String)
    from_id = Column(Integer, ForeignKey("user.id"))
    to_id = Column(Integer, ForeignKey("user.id"))
    recipients = Column(String)
    recipients_group = Column(String)
    subject = Column(String)
    message = Column(String)
    message_type = Column(String)
    message_template_id = Column(Integer)
    filing_type = Column(String)
    task_id = Column(Integer, ForeignKey("task.id"))
    entity_id = Column(UUID)
    
    meta = Column(JSON)
    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())

    
class RecipientMessage(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    message_id = Column(UUID, ForeignKey("message.id"), nullable=False)
    recipient = Column(String)
    recipient_id = Column(Integer, ForeignKey("user.id"))


class MessageTemplate(CustomBase):
    id = Column(Integer, primary_key=True)
    short_name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=False)
    template = Column(String)
    active = Column(Boolean, nullable=False, server_default='t')
    
    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True),
                     nullable=False, default=func.now(),
                     onupdate=func.now())

class MessageTemplateMessageType(CustomBase):
    id = Column(Integer, primary_key=True)
    message_template_id = Column(Integer, ForeignKey("message_template.id"), nullable=False)
    message_type = Column(String, nullable=False, unique=True)
    message_template = relationship("MessageTemplate")
    
