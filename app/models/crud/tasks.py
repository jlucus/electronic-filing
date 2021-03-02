from typing import Optional
from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.models.users import User
from app.models.tasks import Task


async def insert_task(
    *,
    db_session: Session,
    task_ref: str,
    task_type: str,
    assigned_to_user_id: int = False,
    task_short: str,
    task_detail: str,
    task_link: str = None,
    admin_task: bool = False,
    meta: dict = None
):

    new_task = Task()
    new_task.task_ref = task_ref
    new_task.task_type = task_type
    new_task.assigned_to_user_id = assigned_to_user_id
    new_task.task_short = task_short
    new_task.task_detail = task_detail
    new_task.task_link = task_link
    new_task.admin_task = admin_task
    new_task.meta = meta

    db_session.add(new_task)
    db_session.commit()

    return new_task

async def get_task_by_ref(db_session: Session, task_ref: str):

    res = db_session.execute(
        select(Task).filter(Task.task_ref == task_ref)
    ).unique().scalar()

    return res

async def get_all_admin_tasks(db_session: Session):

    res = db_session.execute(
        select(Task)
        .filter(Task.admin_task == True)
        .order_by(Task.updated)
    ).unique().scalars().all()

    return res


async def get_all_open_admin_tasks(db_session: Session):

    res = db_session.execute(
        select(Task)
        .filter(Task.admin_task == True)
        .filter(Task.complete == False)
        .order_by(Task.updated)
    ).unique().scalars().all()

    return res
