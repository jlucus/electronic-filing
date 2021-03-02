import uuid
import logging
import traceback
from fastapi import APIRouter, Depends, Response, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session
from app.db.utils import get_db
from app.schemas.auth import Token
from app.api.utility.exc import (
    handle_exc,
    Http400,
)

from app.api.utility.user import (
    get_active_admin_user,
)
from app.models.users import User
from app.models.crud.tasks import (
    get_all_open_admin_tasks
)

router = APIRouter()

logger = logging.getLogger("fastapi")


@router.get("/open")
async def get_open_tasks(
    user: User = Depends(get_active_admin_user),
    db_session: Session = Depends(get_db),
):

    try:
        res = await get_all_open_admin_tasks(db_session)
        res = jsonable_encoder(res)

        return {"success": True, "data": res}

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)



