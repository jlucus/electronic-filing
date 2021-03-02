import uuid
import logging
import traceback
from fastapi import APIRouter, Depends, Response, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session
from app.core.config import ENFORCE_RECAPTCHA
from app.db.utils import get_db
from app.utils.date_utils import (
    today,
    is_valid_date
)
from app.core.config import (
    FRONTEND_ROUTES
)
from app.schemas.filer.filer import (
    FilerContactInfoSchema
)
from app.models.users import (
    User,
)
from app.models.entities import (
    LOBBYIST_TYPES
)
from app.models.filers import (
    FILER_TYPES
)
from app.models.crud.global_helpers import (
    get_most_recent_entry
)
from app.models.crud.filer import (
    get_filer_by_user_id,
    update_filer_contact_info
)
from app.models.crud.lobbyist import (
    get_lobbying_entities_by_filer_id
)
from app.api.utility.exc import (
    handle_exc,
    Http400,
    CREDENTIALS_EXCEPTION,
    AccountPermissionException,
    EntityNotFoundException
)
from app.api.utility.user import (
    get_active_user
)

router = APIRouter()

logger = logging.getLogger("fastapi")


@router.get("/info")
async def filer_info(
    user: User = Depends(get_active_user),
    db_session: Session = Depends(get_db)
):

    try:
        # user must be filer
        if user.account_type != 'filer':
            raise AccountPermissionException()

        filer = await get_filer_by_user_id(db_session, user.id)
        if filer is None:
            raise AccountPermissionException()
        
        # filer types
        # contact info
        # agencies
        # entities

        filer_types_raw = filer.filer_types

        filer_contact_info = get_most_recent_entry(filer.contact_infos)
        
        if filer_contact_info is None:
            filer_contact_info = {}
        else:
            filer_contact_info = jsonable_encoder(filer_contact_info)
            del filer_contact_info['filer_id']
            del filer_contact_info['id']
            del filer_contact_info['created']
            del filer_contact_info['updated']
            
        filer_types = [
            { "key": x.filer_type,
            "value": FILER_TYPES[x.filer_type] } for x in filer_types_raw]
    
        # entities, at this point only lobbyist
        lobbying_entities = await get_lobbying_entities_by_filer_id(
            db_session,
            filer.filer_id
        )

        entity_list = []
        for entity in lobbying_entities:
            # get most recent contact info
            contact_info = get_most_recent_entry(entity.contact_info)

            xtypes = [LOBBYIST_TYPES[x.lobbyist_type] for x in entity.lobbyist_types]
            xtypes = ", ".join(xtypes)
                
            xd = {
                "name": contact_info.name,
                "entity_type": xtypes,
                "entity_id": entity.entity_id,
                "role": "Filer",
                "active": entity.active,
                "url": None
            }
            if entity.active:
                url = FRONTEND_ROUTES['lobbying_entity_profile'] + "/" + \
                      entity.entity_id
                xd.update({"url": url})

            entity_list.append(xd)

        entity_list.sort(key=lambda x: x['name'])

        res_dict = {
            "filer_id": filer.filer_id,
            "contact_info": filer_contact_info,
            "email": filer.email,
            "filer_types": filer_types,
            "entities": entity_list,
            "sei_agencies": []
        }

        return {"success": True, "data": res_dict}
        
        
    except AccountPermissionException as e:
        # we don't log this
        raise

    except EntityNotFoundException as e:
        # we don't log this
        raise

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)
        

@router.put("/update-contact-info")
async def filer_info(
    payload: FilerContactInfoSchema,
    user: User = Depends(get_active_user),
    db_session: Session = Depends(get_db)
):        

    try:
        # user must be filer
        if user.account_type != 'filer':
            raise AccountPermissionException()

        filer = await get_filer_by_user_id(db_session, user.id)
        if filer is None:
            raise AccountPermissionException()

        # get filer types
        ftypes = [x.filer_type for x in filer.filer_types]

        # blocker filer types
        blockers = ['candidate', 'campaign']
        blocked = False
        for blocker in blockers:
            if blocker in ftypes:
                blocked = True
                break

        if blocked:
            raise Http400("Filer cannot change contact info. "\
                          "Please contact City Clerk's Office.")

        if payload.effective_date is None or not is_valid_date(payload.effective_date):
            payload.effective_date = today()
        
        res = await update_filer_contact_info(db_session, filer, payload)
        if res:
            user.first_name = payload.first_name
            user.last_name = payload.last_name
            user.middle_name = payload.middle_name
            db_session.commit()
        
        return {"success": res}
        
    except AccountPermissionException as e:
        # we don't log this
        raise

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)
        
    
    return None
