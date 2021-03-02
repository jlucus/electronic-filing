import logging
from sqlalchemy.orm import Session
from app.models.messages import (
    MessageTemplate
)
from app.models.crud.user import (
    get_all_active_admin_users
)
from app.models.crud.messages import (
    insert_message
)
from app.utils.email_utils import (
    render_template_from_disk,
    render_template_from_db,
    send_message
)

logger = logging.getLogger("fastapi")

async def send_pcg_email(
    *,
    data: dict,
    subject: str,
    sender: str,
    recipients: list,
):

    html = render_template_from_disk(data,
                                     "pcg_email.html")

    meta = send_message(sender, recipients, subject, html)

    return True


async def send_templated_email_disk(
    *,
    db_session: Session,
    data: dict,
    template_name: str,
    message_type: str,
    subject: str,
    sender: str,
    recipients: list = None,
    recipients_group: str = None,
    from_id: int = None,
    to_id: int = None,
    task_id: int = None,
    filing_type: str = None,
    entity_id: str = None,
):

    html = render_template_from_disk(data,
                                     template_name)

    if recipients_group is not None and recipients_group == "admin":
        admin_users = get_all_active_admin_users(Session)
        recipients = [x.email for x in admin_users]

    meta = send_message(sender, recipients, subject, html)

    recipients = ", ".join(recipients)

    html = " ".join(html.split()).strip()

    await insert_message(
        db_session=db_session,
        sender=sender,
        recipients=recipients,
        subject=subject,
        message=html,
        message_type=message_type,
        meta=meta,
        from_id=from_id,
        to_id=to_id,
        recipients_group=recipients_group,
        task_id=task_id,
        filing_type=filing_type,
        entity_id=entity_id,
    )

    return True


async def send_templated_email_db(
    *,
    db_session: Session,
    data: dict,
    template: MessageTemplate,
    message_type: str,
    subject: str,
    sender: str,
    recipients: list = None,
    recipients_group: str = None,
    from_id: int = None,
    to_id: int = None,
    task_id: int = None,
    filing_type: str = None,
    entity_id: str = None,
):

    html = render_template_from_db(data,
                                   template)

    if recipients_group is not None and recipients_group == "admin":
        admin_users = get_all_active_admin_users(Session)
        recipients = [x.email for x in admin_users]

    meta = send_message(sender, recipients, subject, html)

    recipients = ", ".join(recipients)

    html = " ".join(html.split()).strip()

    await insert_message(
        db_session=db_session,
        sender=sender,
        recipients=recipients,
        subject=subject,
        message=html,
        message_type=message_type,
        message_template_id=template.id,
        meta=meta,
        from_id=from_id,
        to_id=to_id,
        recipients_group=recipients_group,
        task_id=task_id,
        filing_type=filing_type,
        entity_id=entity_id
    )

    return True




