import traceback
import logging
import secrets
import datetime
import uuid
import json
from typing import Optional
import pytz
from dateutil.parser import parse
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.core.config import (
    FRONTEND_ROUTES,
    EMAIL_TEMPLATES,
    NEW_LOBBYIST_EMAIL_VERIFY_EXPIRE_MINS,
    NEW_LOBBYIST_PASSWORD_SET_EXPIRE_MINS,
    APP_HOST,
    EFILE_EMAIL,
    LOBBYIST_FORMS,
    FILING_FORM_NAMES_VERSIONS
)
from app.utils.date_utils import (
    get_period_start_end,
    today
)
from app.schemas.lobbyist.new_lobbyist_registration import (
    NewLobbyistRegistration
)
from app.schemas.user.user import (
    UserBasic
)
from app.schemas.filer.filer import (
    FilerBasic
)
from app.schemas.lobbyist.review_new_lobbyist import (
    ReviewNewLobbyist
)
from app.schemas.lobbyist.lobbyist_general import (
    UpdateLobbyingEntity,
    UpdateFilingInProgress
)
from app.schemas.lobbyist.new_lobbyist_filing import (
    NewLobbyistFiling
)
from app.schemas.form_templates.lobbyist import (
    ec601, ec602, ec603, ec604, ec605
)
from app.models.crud.lobbyist import (
    get_lobbying_entity_by_name,
    get_lobbying_entity_by_id,
    get_lobbying_entity_current_contact_info_by_id,
    insert_lobbying_entity,
    update_lobbying_entity,
    insert_lobbying_entity_contact_info,
    assoc_filer_with_lobbying_entity
)
from app.models.entities import (
    LOBBYIST_TYPES
)
from app.models.crud.user import (
    get_filer_user_by_email,
    insert_new_user,
    get_all_active_admin_users
)
from app.models.crud.filer import (
    get_filer_by_user_id,
    insert_new_filer_basic
)
from app.models.crud.entity import (
    insert_entity
)
from app.models.crud.humane_ids import (
    insert_human_readable_id
)
from app.models.crud.messages import (
    get_message_template_by_message_type
)
from app.models.crud.filings import (
    FILED_STATUS,
    get_filing_by_id_and_type,
    create_new_filing,
    upsert_raw_filing,
    get_raw_filing_by_id
)
from app.api.utility.exc import (
    handle_exc,
    Http400
)
from app.utils.auth import (
    create_access_token,
    check_access_token
)
from app.utils.email_utils import (
    render_template_from_disk,
    send_message
)
from app.api.utility.exc import(
    CREDENTIALS_EXCEPTION
)
from app.api.utility.emails import (
    send_templated_email_disk,
    send_templated_email_db,
)
from app.api.utility.lobbyist_helpers import (
    populate_core_new_lobbyist_form,
    populate_lobbyist_amendment_form,
    populate_quarterly_registered_data,
    compute_ec601_fees,
    simplify_fees
)
from app.models.crud.tasks import (
    insert_task,
    get_task_by_ref
)
from app.models.crud.config import (
    get_filing_config_key
)
from app.models.users import (
    User
)
from app.models.filers import (
    Filer
)
from app.models.entities import (
    LobbyingEntity
)
from app.models.filers import (
    Filer,
    FilerContactInfo
)
from app.models.filings import (
    Filing
)
from app.api.utility.lobbyist_validate_ingest import (
    validate_lobbyist_filing
)

logger = logging.getLogger("fastapi")

async def review_new_lobbyist(
    db_session: Session,
    form: ReviewNewLobbyist,
    user: User
):

    # get lobbyist
    entity = await get_lobbying_entity_by_id(db_session, str(form.lobbying_entity_id))

    # get task
    task = await get_task_by_ref(db_session, form.task_ref)
    if task.complete:
        # someone else has done it already, we just happily return 200
        return True

    # get the associated filing user
    filer_user = entity.filers[0].user

    if form.action == 'activate':

        entity.active = True
        entity.reviewed = True
        task.complete = True
        task.completed_by_user_id = user.id


        # email code
        filer_user.password_set_reset_secret = secrets.token_hex(16)
        now = datetime.datetime.now(tz=pytz.utc)
        access_token_expires = datetime.timedelta(
            minutes=NEW_LOBBYIST_PASSWORD_SET_EXPIRE_MINS
        )
        filer_user.password_set_reset_expire = now + access_token_expires
        data = { "sub": filer_user.email,
                 "filer": True,
                 "entity_id": entity.entity_id,
                 "email_code": filer_user.password_set_reset_secret,
                 "endpoint": FRONTEND_ROUTES["filer_set_password"]
             }
        access_token = create_access_token(
            data=data,
            expires_delta=access_token_expires
        ).decode('UTF-8')

        # send email verification email
        url = (
            APP_HOST + FRONTEND_ROUTES["filer_set_password"] +
            f"?token={access_token}"
        )

        # get message template
        template = await get_message_template_by_message_type(db_session,
                                                        "lobbyist_new_welcome")

        # set up data
        lobbyist_types = jsonable_encoder(entity.lobbyist_types)

        form_names = []
        for xt in lobbyist_types:
            reg_form = LOBBYIST_FORMS[xt['lobbyist_type']].get('register', None)
            qt_form = LOBBYIST_FORMS[xt['lobbyist_type']].get('quarterly', None)
            if reg_form is not None:
                form_names.append(reg_form)
            elif qt_form is not None:
                form_names.append(qt_form)

        form_name = ", ".join(form_names)
        if len(form_name) > 0:
            form_name += "."

        data = { 'form_name': form_name,
                 'url': url }


        await send_templated_email_db(
            db_session=db_session,
            data=data,
            template=template,
            message_type="lobbyist_new_welcome",
            subject="[eFile San Diego] Welcome!",
            sender=EFILE_EMAIL,
            recipients=[filer_user.email],
            filing_type='lobbyist',
            entity_id=entity.entity_id
        )

    elif form.action == 'reject':

        entity.active = False
        entity.reviewed = True
        entity.rejected = True
        task.complete = True
        task.completed_by_user_id = user.id

        db_session.commit()

        # get message template
        template = await get_message_template_by_message_type(db_session,
                                                        "lobbyist_new_reject")

        data = {}

        await send_templated_email_db(
            db_session=db_session,
            data=data,
            template=template,
            message_type="lobbyist_new_reject",
            subject="[eFile San Diego] Regarding your Lobbyist Registration",
            sender=EFILE_EMAIL,
            recipients=[filer_user.email],
            filing_type='lobbyist',
            entity_id=entity.entity_id
        )


    else:
        Http400(f"Action {form.action} is not supported.")



    db_session.commit()

    return True


async def register_lobbyist_check_email_confirm(
    db_session: Session,
    token: str
):

    res = check_access_token(token)
    if res.get('filer'):

        # get filer user
        user = get_filer_user_by_email(db_session, res['sub'])

        if not user:
            raise CREDENTIALS_EXCEPTION

        # get entity
        entity = await get_lobbying_entity_by_id(db_session, res['entity_id'])

        entity_contact_info = await get_lobbying_entity_current_contact_info_by_id(
            db_session,
            entity.entity_id
        )

        if not entity:
            raise CREDENTIALS_EXCEPTION

        # get filer
        filer = await get_filer_by_user_id(db_session, user.id)
        filer.active = True

        if not entity:
            raise CREDENTIALS_EXCEPTION

        if entity.filer_email_code != res['email_code']:
            raise CREDENTIALS_EXCEPTION

        # already confirmed
        if entity.filer_email_confirmed:
            return {"success": True, "detail": "Email already confirmed."}

        user.email_confirmed = True
        entity.filer_email_confirmed = True

        db_session.commit()

    else:
        raise CREDENTIALS_EXCEPTION

    # get the lobby types of this firm
    lobbyist_types = ", ".join(
        [LOBBYIST_TYPES[x.lobbyist_type] for x in entity.lobbyist_types]
    )



    # now notify city staff
    data = { "lobbyist_type" : lobbyist_types,
             "lobbyist_name" : entity_contact_info.name,
             "filer_first_name" : user.first_name,
             "filer_last_name" : user.last_name,
             "filer_email" : user.email
         }

    # create new task
    task_meta = {'entity_id': entity.entity_id,
                 'filer_user_id': user.id}
    task_ref = str(uuid.uuid4())
    task_link = (
        FRONTEND_ROUTES['lobbyist_new_registration_admin_review']
        + f'/{entity.entity_id}?task_ref={task_ref}'
    )
    task_short = f"Review new lobbyist"
    task_detail = f"{entity_contact_info.name}"
    new_task = await insert_task(
        db_session=db_session,
        task_ref=task_ref,
        task_type="review_new_lobbyist",
        admin_task=True,
        task_short=task_short,
        task_detail=task_detail,
        task_link=task_link,
        meta=task_meta
    )

    admins = get_all_active_admin_users(db_session)
    recipients = [x.email for x in admins]

    await send_templated_email_disk(
        db_session=db_session,
        data=data,
        template_name=EMAIL_TEMPLATES["lobbyist_new_admin_notify"],
        message_type="lobbyist_new_registration_verify_email",
        subject="[eFile San Diego] Please Review new Lobbyist",
        sender=EFILE_EMAIL,
        recipients=recipients,
        task_id=new_task.id,
        filing_type='lobbyist',
        entity_id=entity.entity_id
    )


    return {"success": True}


async def update_lobbyist(
    db_session: Session,
    form: UpdateLobbyingEntity
):

    return await update_lobbying_entity(db_session, form)



async def register_new_lobbyist(
    db_session: Session,
    form: NewLobbyistRegistration,
):

    # do we have the lobbying entity already?

    res = await get_lobbying_entity_by_name(db_session, form.entity_name)

    if res is not None:
        Http400("Lobbyist name already registered.")

    # create the entity
    new_entity = await insert_lobbying_entity(db_session, form)


    # create general entity assoc object
    new_general_entity = await insert_entity(db_session,
                                             new_entity.entity_id,
                                             "lobbying")

    # create new human readable ID for this lobbyist

    new_human_readable_id = await insert_human_readable_id(
         db_session,
         object_id=str(new_entity.entity_id),
         object_type="lobbying_entity",
         hr_id_prefix="lobbyist"
    )


    # check if we know the user
    user = get_filer_user_by_email(db_session, form.filer_email)


    if user is None:
        # we have to make the user
        new_user = UserBasic(
            email=form.filer_email,
            account_type="filer",
            city=False,
            active=True,
            first_name=form.filer_first_name,
            middle_name=form.filer_middle_name,
            last_name=form.filer_last_name
        )

        user = await insert_new_user(db_session, new_user)

        # now let's make a new filer
        new_filer = FilerBasic(user_id=user.id,
                               first_name=form.filer_first_name,
                               middle_name=form.filer_middle_name,
                               last_name=form.filer_last_name)

        filer = await insert_new_filer_basic(db_session, new_filer)

    else:
        # get the filer
        filer = await get_filer_by_user_id(db_session, user.id)

    if filer is None:
        raise Http400("Filer user could not be found.")
        
    # now associate the filer with the lobbying entity
    lef = await assoc_filer_with_lobbying_entity(db_session, filer.filer_id,
                                                 new_entity.entity_id)

    # email code
    new_entity.filer_email_code = secrets.token_hex(16)
    access_token_expires = datetime.timedelta(
        minutes=NEW_LOBBYIST_EMAIL_VERIFY_EXPIRE_MINS
    )
    data = { "sub": user.email,
             "filer": True,
             "entity_id": new_entity.entity_id,
             "email_code": new_entity.filer_email_code,
             "endpoint": FRONTEND_ROUTES["lobbyist_new_registration_verify_email"]
         }
    access_token = create_access_token(
        data=data,
        expires_delta=access_token_expires
    ).decode('UTF-8')

    # send email verification email
    url = (
        APP_HOST + FRONTEND_ROUTES["lobbyist_new_registration_verify_email"] +
        f"?token={access_token}"
    )

    await send_templated_email_disk(
        db_session=db_session,
        data={'url': url},
        template_name=EMAIL_TEMPLATES["lobbyist_new_registration_verify_email"],
        message_type="lobbyist_email_confirmation",
        subject="[eFile San Diego] Please Confirm your Email",
        sender=EFILE_EMAIL,
        recipients=[user.email],
        to_id=user.id,
        filing_type='lobbyist',
        entity_id=new_entity.entity_id
    )


    # add filing type to user
    # save message in message db

    db_session.commit()


async def get_lobbyist_filer_user(
    db_session: Session,
    lobbying_entity: LobbyingEntity,
    user: User
) -> Optional[Filer]:

    filer = await get_filer_by_user_id(db_session, user.id)
    if filer is None:
        return None

    filer_ids = [x for x in lobbying_entity.filers if x.filer_id == filer.filer_id]

    if len(filer_ids) > 0:
        return filer
    else:
        return None

async def create_new_lobbyist_filing(
    db_session: Session,
    filing_id: str,
    entity: LobbyingEntity,
    filer: Filer,
    payload: NewLobbyistFiling
):

    # check amendment
    if payload.amends_id is not None:

        prev = await get_filing_by_id_and_type(
            db_session,
            payload.amends_id,
            payload.filing_type
        )

        if prev is None or prev.status not in FILED_STATUS:
            raise Http400(detail="Filing to amend not found.")

        amends_id = payload.amends_id
        if prev.amends_orig_id is not None:
            amends_orig_id = prev.amends_orig_id
            amendment_number = prev.amendment_number + 1
        else:
            amends_orig_id = prev.filing_id
            amendment_number = 1

    period_start, period_end = get_period_start_end(payload.year, payload.quarter)

    # create the filing dict
    filing_dict = {
        "filing_id" : filing_id,
        "status": "new",
        "entity_id": entity.entity_id,
        "form_name": FILING_FORM_NAMES_VERSIONS[payload.filing_type],
        "filing_type": payload.filing_type,
        "period_start": period_start,
        "period_end": period_end
    }

    # amendment?
    if payload.amends_id is not None:
        filing_dict['amendment'] = True
        filing_dict['amends_prev_id'] = amends_id
        filing_dict['amends_orig_id'] = amends_orig_id
        filing_dict['amendment_number'] = amendment_number

    # there's a deadline if this is a legit quarterly
    if payload.filing_type in ['ec603','ec604','ec605'] \
       and payload.quarter is not None:
        key = f"{payload.quarter} deadline"
        year = payload.year
        deadline_config = await get_filing_config_key(
            db_session,
            key,
            "lobbyist",
            payload.filing_type,
            payload.year
        )
        if deadline_config is None:
            raise Http400(detail="Could not determine deadline")

        filing_dict['deadline'] = deadline_config.value


    filing = await create_new_filing(db_session, filing_dict)

    if payload.filing_type == 'ec601':
        if not filing.amendment:
            form = ec601()
            form = await populate_core_new_lobbyist_form(
                db_session, payload, 'ec601', form, entity, filing
            )
        else:
            form = await populate_lobbyist_amendment_form(
                db_session, payload, filing
            )
    elif payload.filing_type == 'ec603':
        if not filing.amendment:
            form = ec603()
            form = await populate_core_new_lobbyist_form(
                db_session, payload, 'ec603', form, entity, filing
            )
        else:
            raise Http400("EC-603 amendment not yet implemented.")
            
    else:
        raise Http400("Filing type not yet implemented")

    filing_raw = await upsert_raw_filing(db_session, form)

    return None

async def get_filing_in_progress(
    db_session: Session,
    filing: Filing,
    filer: Filer
):

    raw = await get_raw_filing_by_id(db_session, filing.filing_id)
    if raw is None:
        return None

    filer_contact = filer.contact_infos
    filer_contact.sort(key=lambda x: x.updated, reverse=True)
    
    if len(filer_contact) == 0:
        raise Http500(detail="Filer has no associated contact info.")
    filer_contact = filer_contact[0]

    raw_dict = raw.raw_json
    raw_dict['filer'] = {
        "filer_id": filer.filer_id,
        "first_name": filer_contact.first_name,
        "middle_name": filer_contact.middle_name,
        "last_name": filer_contact.last_name,
        "address1": filer_contact.address1,
        "address2": filer_contact.address2,
        "city": filer_contact.city,
        "zipcode": filer_contact.zipcode,
        "state": filer_contact.state,
        "phone": filer_contact.phone,
        "email": filer.email
    }

    if filing.filing_type in ['ec603','ec604']:
        # load lobbyist contact data
        contact_info = await get_lobbying_entity_current_contact_info_by_id(
            db_session,
            filing.entity_id
        )
        if contact_info is None:
            raise Http400(detail="Lobbying entity is missing contact info.")

        finfo = raw_dict['lobbying_entity_contact_info']
        cinfo = jsonable_encoder(contact_info)
        for key in finfo.keys():
            finfo[key] = cinfo[key]

        raw_dict = await populate_quarterly_registered_data(
            db_session,
            filing.filing_type,
            raw_dict,
            filing
        )
    
    return raw_dict

async def update_filing_in_progress(
    db_session: Session,
    filing: Filing,
    payload: UpdateFilingInProgress
):

    filing.status = "in progress"

    res = await upsert_raw_filing(db_session, payload.form)

    db_session.commit()

    return True

mfd_a = [
    {"lobbyist_entity_id": "123"},
    {"lobbyist_entity_id": "124"},
    {"lobbyist_entity_id": "125"}
]
mfd_b = [
    {"client_entity_id": "abc"},
    {"client_entity_id": "xyz"},
    {"client_entity_id": "xyzz"}
]
mfd_dir = {
    "entity": [
        {
            "id": "124",
            "effective_date": "2021-10-05"
        },
        {
            "id": "125",
            "effective_date": "2021-08-05"
        },        
        {
            "id": "123",
            "effective_date": "2021-01-01"
        },
        {
            "id": "abc",
            "effective_date": "2021-01-01"
        },
        {
            "id": "xyz",
            "effective_date": "2021-10-05"
        },
        {
            "id": "xyzz",
            "effective_date": "2021-10-06"
        },        
    ]
}


async def calculate_filing_fees(
    db_session: Session,
    filing: Filing
):

    raw = await get_raw_filing_by_id(db_session, filing.filing_id)
    if raw is None:
        raise Http400("Failed to fetch raw filing data")

#    filing.amendment = True
#    filing.amends_prev_id = "d7a31cbb-bf39-4e67-937e-1c52de4a07a0"
    
    if filing.amendment:
        raw_prev = await get_raw_filing_by_id(db_session, filing.amends_prev_id)
        raw_filing_prev = dict(raw_prev.raw_json)
        
    raw_filing = dict(raw.raw_json)
    
    year = raw_filing["year"]

    res = await get_filing_config_key(
        db_session,
        "fees",
        "lobbyist",
        filing.filing_type,
        year)

    config = json.loads(res.value)

    # d7a31cbb-bf39-4e67-937e-1c52de4a07a0
    
    # fake data
#    raw_filing["schedule_a"] = mfd_a
#    raw_filing["schedule_b"] = mfd_b
#    raw_filing["directory"] = mfd_dir


    # load as date
    for sched in config['fee_schedule']:
        sched['start'] = parse(sched['start']).date()
        sched['end'] = parse(sched['end']).date()
    for entity in raw_filing['directory']['entity']:
        entity['effective_date'] = parse(entity['effective_date']).date()


    if filing.filing_type == 'ec601':

        # if this is an amendment, we remove all the lobbyists
        # and clients from schedule A and B that are already present
        # in the previous filing
        if filing.amendment:
            # lobbyists
            prev_ids = [x['lobbyist_entity_id'] for x in raw_filing_prev["schedule_a"]]
            new_schedule_a = []
            for lobbyist in raw_filing["schedule_a"]:
                if lobbyist['lobbyist_entity_id'] not in prev_ids:
                    new_schedule_a.append(lobbyist)
            raw_filing['schedule_a'] = new_schedule_a
            # clients
            prev_ids = [x['client_entity_id'] for x in raw_filing_prev["schedule_b"]]
            new_schedule_b = []
            for client in raw_filing["schedule_b"]:
                if client['client_entity_id'] not in prev_ids:
                    new_schedule_b.append(client)
            raw_filing['schedule_b'] = new_schedule_b
        
        lobbyists = compute_ec601_fees("lobbyist", "schedule_a",
                                       raw_filing, config)

        clients = compute_ec601_fees("client", "schedule_b",
                                     raw_filing, config)

        lobbyist_fees = sum([x['fee']*x['count'] for x in lobbyists])
        client_fees = sum([x['fee']*x['count'] for x in clients])
        
        res_dict = {
            "lobbyists": { "details": lobbyists,
                          "fees": lobbyist_fees
                      },
            "clients": { "details": clients,
                         "fees": client_fees
                     }
        }

        return res_dict

    elif filing.filing_type == 'ec602':

        if filing.amendment:
            return { "fee": 0.0}

        raise Http500(detail="Not yet implemented")

    else:
        return None

async def finalize_lobbyist_filing(
    db_session: Session,
    filing: Filing,
    filer: Filer,
    payload: UpdateFilingInProgress
):

    # validate
    payload = await validate_lobbyist_filing(db_session, filing, payload)
    
    # save the shit out of the filing:
    await update_filing_in_progress(db_session, filing, payload)

    if filing.filing_type in ['ec601','ec602']:
        fees = await calculate_filing_fees(db_session, filing)
        fees = simplify_fees(fees, filing)
        payload.form['fees'] = fees
        # save it again
        await update_filing_in_progress(db_session, filing, payload)
    
    if payload.form['lobbying_entity_contact_info_change']:
        contact_info = payload.form['lobbying_entity_contact_info']
        contact_info['entity_id'] = filing.entity_id
        await insert_lobbying_entity_contact_info(db_session, contact_info)

    # need to change this for fees
    filing.status = "filed"
    filing.date = today()
    filing.filer_id = filer.filer_id

    db_session.commit()

    return True
    
