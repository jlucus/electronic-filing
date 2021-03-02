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
from app.models.crud.lobbyist import (
    get_lobbying_entity_by_id
)

router = APIRouter()

logger = logging.getLogger("fastapi")

@router.get("/{lobbying_entity_id}")
async def get_lobbyist(
    lobbying_entity_id: str,
    user: User = Depends(get_active_admin_user),
    db_session: Session = Depends(get_db),
):

    # check that we got a UUID
    if not check_uuid4(lobbying_entity_id):
        raise Http400(detail="Lobbying entity ID must be a valid UUID4.")

    try:
        res = await get_lobbying_entity_by_id(db_session, lobbying_entity_id)

        if res is None:
            raise Http400(detail="Lobbying entity does not exist.")

        lobbyist_types = [
            (x.lobbyist_type, LOBBYIST_TYPES[x.lobbyist_type])
            for x in res.lobbyist_types
        ]

        contact_info = [jsonable_encoder(x) for x in res.contact_info
                        if x.active][0]

        # get associated filer users
        filer_users = [jsonable_encoder(x.user) for x in res.filers]

        res = jsonable_encoder(res)
        res['name'] = contact_info['name']
        res['address1'] = contact_info['address1']
        res['address2'] = contact_info['address2']
        res['city'] = contact_info['city']
        res['zipcode'] = contact_info['zipcode']
        res['state'] = contact_info['state']
        res['phone'] = contact_info['phone']

        res['lobbyist_types'] = lobbyist_types
        del res['filers']
        res['filer_users'] = filer_users

        return {"success": True, "data": res}

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)

@router.put("/resend-confirm-email/{lobbying_entity_id}")
async def lobbyist_resend_confirm_email(
    lobbying_entity_id: str,
    user: User = Depends(get_active_admin_user),
    db_session: Session = Depends(get_db),
):

    pass


@router.put("/resend-welcome-email/{lobbying_entity_id}")
async def lobbyist_welcome_confirm_email(
    lobbying_entity_id: str,
    user: User = Depends(get_active_admin_user),
    db_session: Session = Depends(get_db),
):

    pass


@router.post("/review-new-lobbyist/{lobbying_entity_id}")
async def post_review_new_lobbyist(
    lobbying_entity_id: str,
    body: ReviewNewLobbyist,
    user: User = Depends(get_active_admin_user),
    db_session: Session = Depends(get_db),
):

    try:
        if lobbying_entity_id != body.lobbying_entity_id:
            Http400("Lobbying entity ids don't match.")

        await review_new_lobbyist(db_session, body, user)

        # await update_lobbyist(db_session, body)

        return {"success": True }

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)



@router.post("/{lobbying_entity_id}")
async def post_update_lobbyist(
    lobbying_entity_id: str,
    body: UpdateLobbyingEntity,
    user: User = Depends(get_active_admin_user),
    db_session: Session = Depends(get_db),
):

    try:

        if lobbying_entity_id != body.entity_id:
            Http400("Lobbying entity ids don't match.")

        await update_lobbyist(db_session, body)

        return {"success": True }

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)




