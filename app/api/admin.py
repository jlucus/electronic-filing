import uuid
import logging
import traceback
from fastapi import APIRouter, Depends, Response, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session
from app.db.utils import get_db
from app.schemas.auth import Token
from app.utils.string_utils import check_uuid4
from app.api.utility.exc import (
    handle_exc,
    Http400,
)
from app.api.utility.user import (
    get_active_admin_user,
)
from app.schemas.lobbyist.review_new_lobbyist import (
    ReviewNewLobbyist
)
from app.schemas.lobbyist.lobbyist_general import (
    UpdateLobbyingEntity
)
from app.api.utility.lobbyist import (
    update_lobbyist,
    review_new_lobbyist
)
from app.models.users import User
from app.models.entities import (
    LOBBYIST_TYPES
)
from app.models.crud.filer import (
    get_all_filer_ids_by_start_of_last_name
)

router = APIRouter()

logger = logging.getLogger("general")


@router.get("/filer-search")
async def filer_search(
    search_str: str,
    user: User = Depends(get_active_admin_user),
    db_session: Session = Depends(get_db),
):

    # ultimate:
    # last name,
    # org name
    # org id
    # filer id

    try:

        data = []
        if len(search_str) > 1:
        
            # this is preliminary
            data = await get_all_filer_ids_by_start_of_last_name(
                db_session, search_str
            )

        return {"success": True, "data": data}

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)

    






    
