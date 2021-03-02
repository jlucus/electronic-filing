from typing import Optional
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.models.users import User
from app.models.messages import (
    Message,
    MessageTemplate,
    MessageTemplateMessageType
)


async def insert_message(
    *,
    db_session: Session,
    sender: str,
    recipients: str,
    subject: str,
    message: str,
    message_type: str,
    meta: dict,
    message_template_id: int = None,
    from_id: int = None,
    to_id: int = None,
    recipients_group: str = None,
    task_id: int = None,
    filing_type: str = None,
    entity_id: str = None,
):

    new_msg = Message()
    new_msg.sender = sender
    new_msg.from_id = from_id
    new_msg.to_id = to_id
    new_msg.recipients = recipients
    new_msg.recipients_group = recipients_group
    new_msg.subject = subject
    new_msg.message = message
    new_msg.message_type = message_type
    new_msg.message_template_id = message_template_id
    new_msg.meta = meta
    new_msg.filing_type = filing_type
    new_msg.task_id = task_id
    new_msg.entity_id = entity_id

    
    db_session.add(new_msg)
    db_session.commit()


    
async def get_message_template_by_message_type(
    db_session: Session,
    message_type: str
) -> Optional[MessageTemplate]:

    res = db_session.execute(
        select(MessageTemplateMessageType)
        .filter(MessageTemplateMessageType.message_type == message_type)
    ).unique().scalar()

    return res.message_template
