import logging
import traceback
import uuid
from fastapi import APIRouter, Depends, Response, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session
from app.core.config import ENFORCE_RECAPTCHA
from app.db.utils import get_db
from app.schemas.auth import Token
from app.utils.string_utils import (
    is_uuid
)
from app.api.utility.exc import (
    handle_exc,
    Http400,
    CREDENTIALS_EXCEPTION,
    AccountPermissionException,
    EntityNotFoundException
)
from app.schemas.lobbyist.new_lobbyist_registration import (
    NewLobbyistRegistration
)
from app.schemas.lobbyist.new_lobbyist_filing import (
    NewLobbyistFiling,
)
from app.schemas.lobbyist.lobbyist_general import (
    UpdateFilingInProgress
)
from app.models.users import (
    User,
)
from app.models.entities import (
    LOBBYIST_TYPES
)
from app.models.crud.lobbyist import (
    get_lobbying_entity_by_id
)
from app.models.crud.global_helpers import (
    get_most_recent_entry
)
from app.models.crud.filings import (
    get_filing_by_id,
    get_raw_filing_by_id
)
from app.api.utility.user import (
    get_active_user
)
from app.api.utility.misc import (
    check_recaptcha_response
)
from app.api.utility.lobbyist import (
    register_new_lobbyist,
    register_lobbyist_check_email_confirm,
    get_lobbyist_filer_user,
    create_new_lobbyist_filing,
    get_filing_in_progress,
    update_filing_in_progress,
    calculate_filing_fees,
    finalize_lobbyist_filing
)


router = APIRouter()

logger = logging.getLogger("fastapi")

@router.post("/register-confirm-email", operation_id="noauth")
async def register_lobbyist_confirm_email(
    req: Request,
    token: Token,
    db_session: Session = Depends(get_db),
):
    try:
        res = await register_lobbyist_check_email_confirm(db_session, token)

        return res

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)


@router.post("/register", operation_id="noauth")
async def register_lobbyist(
    req: Request,
    form: NewLobbyistRegistration,
    db_session: Session = Depends(get_db),
):
    try:
        xd = await req.json()
        res = await check_recaptcha_response(form.recaptcha)

        if ENFORCE_RECAPTCHA and res is False:
           Http400("Recaptcha validation failed.")

        res = await register_new_lobbyist(db_session, form)

        return {"success": True}


    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)

@router.post("/filing/{filing_type}/new")
async def create_filing(
    filing_type: str,
    payload: NewLobbyistFiling,
    user: User = Depends(get_active_user),
    db_session: Session = Depends(get_db),
):

    try:
        # user must be filer
        if user.account_type != 'filer':
            raise AccountPermissionException()

        if filing_type.strip() != payload.filing_type:
            raise Http400("Filing types in params and payload dont' match!")

        if payload.amends_id is not None:
            if not is_uuid(payload.amends_id):
                raise Http400(detail="Amends ID must be UUID or null.")
            filing = await get_filing_by_id(db_session, payload.amends_id)
            if filing is None:
                raise Http400(detail="Filing to be amended not found.")

        # user must be associated with this lobbying entity id
        entity = await get_lobbying_entity_by_id(db_session, payload.lobbying_entity_id)
        if entity is None:
            raise EntityNotFoundException()

        filer = await get_lobbyist_filer_user(db_session, entity, user)
        if filer is None:
            raise AccountPermissionException()

        # generate a unique id for this model

        filing_id = str(uuid.uuid4())

        # at this point we have established that the account is authorized
        # further protections we need
        # no new 601/602 for a year in which a previous exists
        # no new 603/604/605 for a Q for which one exists
        # if a form belonging to a different lobbyist types is
        # filed, upon filing (not upon creating) the lobbyist becomes
        # also the new type

        res = await create_new_lobbyist_filing(
            db_session,
            filing_id,
            entity,
            filer,
            payload
        )

        return { "success": True, "filing_id": filing_id }

    except AccountPermissionException as e:
        # we don't log this
        raise

    except EntityNotFoundException as e:
        # we don't log this
        raise

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)


@router.get("/filing/{filing_type}/{filing_id}")
async def get_filing(
    filing_type: str,
    filing_id: str,
    user: User = Depends(get_active_user),
    db_session: Session = Depends(get_db),
):

    try:
        if not is_uuid(filing_id):
            raise Http400("Filing ID must be UUID")

        if filing_type not in ['ec601','ec602','ec603','ec604','ec605']:
            raise Http400("Unknown filing type!")

        # user must be filer
        if user.account_type != 'filer':
            raise AccountPermissionException()

        filing = await get_filing_by_id(db_session, filing_id)
        if filing is None:
            raise Http400(detail="Filing not found")

        # user must be associated with this lobbying entity id
        entity = await get_lobbying_entity_by_id(db_session, filing.entity_id)
        if entity is None:
            raise EntityNotFoundException()

        filer = await get_lobbyist_filer_user(db_session, entity, user)
        if filer is None:
            raise AccountPermissionException()

        if filing.status not in ['new', 'in progress']:
            if filing.status == 'locked':
                raise Http400(detail="Filing is locked.")
            else:
                raise Http400(detail="Filing cannot be edited")

        if filing.filing_type != filing_type:
            raise Http400(detail="Filing doesn't match filing type.")

        raw = await get_filing_in_progress(db_session, filing, filer)
        if raw is None:
            raise Http400(detail="Filing data not available.")

        return { "success": True, "data": jsonable_encoder(raw) }

    except AccountPermissionException as e:
        # we don't log this
        raise

    except EntityNotFoundException as e:
        # we don't log this
        raise

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)


@router.put("/filing/{filing_type}/{filing_id}")
async def put_filing(
    filing_type: str,
    filing_id: str,
    payload: UpdateFilingInProgress,
    user: User = Depends(get_active_user),
    db_session: Session = Depends(get_db),
):

    try:
        if not is_uuid(filing_id):
            raise Http400("Filing ID must be UUID")

        print(payload.form)
        if payload.form['filing_id'] != filing_id:
            raise Http400("Filing ID mismatch.")

        if filing_type not in ['ec601','ec602','ec603','ec604','ec605']:
            raise Http400("Unknown filing type!")

        # user must be filer
        if user.account_type != 'filer':
            raise AccountPermissionException()

        filing = await get_filing_by_id(db_session, filing_id)
        if filing is None:
            raise Http400(detail="Filing not found")

        # user must be associated with this lobbying entity id
        entity = await get_lobbying_entity_by_id(db_session, filing.entity_id)
        if entity is None:
            raise EntityNotFoundException()

        filer = await get_lobbyist_filer_user(db_session, entity, user)
        if filer is None:
            raise AccountPermissionException()

        if filing.status not in ['new', 'in progress']:
            if filing.status == 'locked':
                raise Http400(detail="Filing is locked.")
            else:
                raise Http400(detail="Filing cannot be edited")

        if filing.filing_type != filing_type:
            raise Http400(detail="Filing doesn't match filing type.")

        await update_filing_in_progress(db_session, filing, payload)

        return { "success": True }

    except AccountPermissionException as e:
        # we don't log this
        raise

    except EntityNotFoundException as e:
        # we don't log this
        raise

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)


@router.get("/filing/{filing_type}/{filing_id}/fees")
async def get_filing_fees(
    filing_type: str,
    filing_id: str,
    user: User = Depends(get_active_user),
    db_session: Session = Depends(get_db),
):

    try:
        if not is_uuid(filing_id):
            raise Http400("Filing ID must be UUID")

        if filing_type not in ['ec601','ec602']:
            raise Http400("Fees are assessed only on forms EC-601 and EC-602.")

        # user must be filer
        if user.account_type != 'filer':
            raise AccountPermissionException()

        filing = await get_filing_by_id(db_session, filing_id)
        if filing is None:
            raise Http400(detail="Filing not found")

        # user must be associated with this lobbying entity id
        entity = await get_lobbying_entity_by_id(db_session, filing.entity_id)
        if entity is None:
            raise EntityNotFoundException()

        filer = await get_lobbyist_filer_user(db_session, entity, user)
        if filer is None:
            raise AccountPermissionException()

        if filing.status not in ['new', 'in progress', 'locked']:
            raise Http400(detail="Filing status invalid for this operation.")

        res = await calculate_filing_fees(db_session, filing)

        return {"success": True, "data": res}

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)


@router.post("/filing/{filing_type}/{filing_id}/finalize")
async def finalize_filing(
    filing_type: str,
    filing_id: str,
    payload: UpdateFilingInProgress,
    user: User = Depends(get_active_user),
    db_session: Session = Depends(get_db),
):

    try:
        print("****", filing_id)
        if not is_uuid(filing_id):
            raise Http400("Filing ID must be UUID")

        if filing_id != payload.form['filing_id']:
            raise Http400("Filing IDs in route and body don't match.")
        
        # user must be filer
        if user.account_type != 'filer':
            raise AccountPermissionException()

        filing = await get_filing_by_id(db_session, filing_id)
        if filing is None:
            raise Http400(detail="Filing not found")

        # user must be associated with this lobbying entity id
        entity = await get_lobbying_entity_by_id(db_session, filing.entity_id)
        if entity is None:
            raise EntityNotFoundException()

        filer = await get_lobbyist_filer_user(db_session, entity, user)
        if filer is None:
            raise AccountPermissionException()

        if filing.status not in ['new', 'in progress', 'locked']:
            raise Http400(detail="Filing status invalid for this operation.")

        res = await finalize_lobbyist_filing(db_session, filing, filer, payload)

        return {"success": res }

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)
        

@router.get("/entity/{lobbying_entity_id}")
async def get_lobbying_entity_info(
    lobbying_entity_id: str,
    user: User = Depends(get_active_user),
    db_session: Session = Depends(get_db)
):

    try:
        
        if not is_uuid(lobbying_entity_id):
            raise Http400("Lobbying entity ID must be UUID")

        # user must be filer
        if user.account_type != 'filer':
            raise AccountPermissionException()

        # user must be associated with this lobbying entity id
        entity = await get_lobbying_entity_by_id(db_session, lobbying_entity_id)
        if entity is None:
            raise EntityNotFoundException()

        filer = await get_lobbyist_filer_user(db_session, entity, user)
        if filer is None:
            raise AccountPermissionException()

        contact_info = jsonable_encoder(get_most_recent_entry(entity.contact_info))
        del contact_info['id']
        del contact_info['updated']
        del contact_info['created']

        lobbyist_types = [
            (x.lobbyist_type, LOBBYIST_TYPES[x.lobbyist_type])
            for x in entity.lobbyist_types
        ]

        filers = []
        for filer in entity.filers:
            cinfo = jsonable_encoder(get_most_recent_entry(filer.contact_infos))
            del cinfo['id']
            del cinfo['updated']
            del cinfo['created']
            cinfo['active'] = filer.active
            filers.append(cinfo)

        filers.sort(key=lambda x: x['last_name'])
        
        return_dict = {
            "lobbyist_types": lobbyist_types,
            "contact_info": contact_info,
            "human_readable_id": "Not yet implemented",
            "status": [],
            "current_filings": [],
            "filers": filers
        }

        return { "success": True, "data": return_dict }

    except (AccountPermissionException, EntityNotFoundException) as e:
        pass
        
    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)



        
        
