import uuid
from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.schemas.lobbyist.new_lobbyist_registration import (
    NewLobbyistRegistration,
)
from app.schemas.lobbyist.lobbyist_general import UpdateLobbyingEntity
from app.api.utility.exc import handle_exc, Http400
from app.models.filers import Filer
from app.models.users import User
from app.models.filings import Filing
from app.models.entities import (
    LOBBYIST_TYPES,
    LobbyingEntity,
    LobbyingEntityContactInfo,
    LobbyingEntityLobbyistType,
    LobbyingEntityFiler,
    LobbyingEntityContactInfo,
)
from app.models.lobbyist_detail import (
    LobbyingLobbyEntity,
    LobbyingLobbyEntityContactInfo,
    LobbyingMuniDecision,
    LobbyingMuniDecisionInfo,
    LobbyingFilingMeta,
    LobbyingFilingVerification,
    LobbyingFilingDeletedEntity,
    LobbyingFilingLobbyist,
    LobbyingFilingClient,
    LobbyingFilingClientCoalitionMember,
    LobbyingFilingRegActivity,
    LobbyingFilingMuniDecision,
    LobbyingFilingComment,
    LobbyingFilingFee,
)

# retrieve data


async def get_lobbying_entity_by_name(
    db_session: Session, name: str
) -> Optional[LobbyingEntity]:

    res = (
        db_session.execute(
            select(LobbyingEntityContactInfo).filter(
                func.lower(LobbyingEntityContactInfo.name) == func.lower(name.strip())
            )
        )
        .unique()
        .scalar()
    )

    if res is not None:
        res = (
            db_session.execute(
                select(LobbyingEntity).filter(LobbyingEntity.entity_id == res.entity_id)
            )
            .unique()
            .scalar()
        )

    return res


async def get_lobbying_entity_filer_ids_by_company(
    db_session: Session,
    company: str,
) -> Optional[LobbyingEntity]:
    res = (
        db_session.execute(
            select(
                LobbyingEntity.netfile_filer_id,
            )
            .join(
                LobbyingEntityContactInfo,
                LobbyingEntityContactInfo.entity_id == LobbyingEntity.entity_id,
            )
            .filter(
                func.lower(LobbyingEntityContactInfo.name).like(
                    "%" + company.strip().lower() + "%"
                )
            )
        )
        .unique()
        .scalars()
        .all()
    )

    return res


async def get_lobbying_entity_by_id(
    db_session: Session,
    entity_id: str,
) -> Optional[LobbyingEntity]:

    res = (
        db_session.execute(
            select(LobbyingEntity).filter(LobbyingEntity.entity_id == entity_id)
        )
        .unique()
        .scalar()
    )

    return res


async def get_lobbying_entity_current_contact_info_by_id(
    db_session: Session,
    entity_id: str,
) -> Optional[LobbyingEntity]:

    res = (
        db_session.execute(
            select(LobbyingEntityContactInfo)
            .filter(LobbyingEntityContactInfo.entity_id == entity_id)
            .order_by(LobbyingEntityContactInfo.updated.desc())
        )
        .unique()
        .scalars()
        .first()
    )

    return res


async def get_lobbying_entities_by_filer_id(db_session: Session, filer_id: str):

    res = (
        db_session.execute(
            select(LobbyingEntity)
            .join(
                LobbyingEntityFiler,
                LobbyingEntityFiler.entity_id == LobbyingEntity.entity_id,
            )
            .filter(LobbyingEntityFiler.filer_id == filer_id)
            .filter(LobbyingEntityFiler.active == True)
        )
        .unique()
        .scalars()
        .all()
    )

    return res


async def get_lobbying_entity_type_by_entity_id(
    db_session: Session,
    entity_id: str,
):
    res = (
        db_session.execute(
            select(LobbyingEntityLobbyistType).filter(
                LobbyingEntityLobbyistType.entity_id == entity_id
            )
        )
        .unique()
        .scalar()
    )

    return res


async def get_registered_lobbyists(db_session: Session, registration: Filing):
    filing_id = registration.filing_id

    res = (
        db_session.execute(
            select(LobbyingLobbyEntityContactInfo)
            .join(
                LobbyingFilingLobbyist,
                LobbyingFilingLobbyist.lobby_entity_contact_info_id
                == LobbyingLobbyEntityContactInfo.id,
            )
            .filter(LobbyingFilingLobbyist.filing_id == filing_id)
            .order_by(LobbyingFilingLobbyist.ordinal)
        )
        .unique()
        .scalars()
        .all()
    )

    return res


async def get_registered_clients(db_session: Session, registration: Filing):
    filing_id = registration.filing_id

    res = (
        db_session.execute(
            select(LobbyingFilingClient, LobbyingLobbyEntityContactInfo)
            .join(
                LobbyingFilingClient,
                LobbyingFilingClient.lobby_entity_contact_info_id
                == LobbyingLobbyEntityContactInfo.id,
            )
            .filter(LobbyingFilingClient.filing_id == filing_id)
            .order_by(LobbyingFilingClient.ordinal)
        )
        .unique()
        .all()
    )

    return res


async def get_registered_muni_decisions_firm(db_session: Session, registration: Filing):
    filing_id = registration.filing_id

    res = (
        db_session.execute(
            select(LobbyingMuniDecisionInfo, LobbyingFilingMuniDecision)
            .join(
                LobbyingFilingMuniDecision,
                LobbyingFilingMuniDecision.decision_info_id
                == LobbyingMuniDecisionInfo.id,
            )
            .join(
                LobbyingFilingClient,
                LobbyingFilingClient.id == LobbyingFilingMuniDecision.filing_client_id,
            )
            .filter(LobbyingFilingMuniDecision.filing_id == filing_id)
            .order_by(LobbyingFilingMuniDecision.ordinal)
        )
        .unique()
        .all()
    )

    return res


# insert


async def insert_lobbying_entity(
    db_session: Session, form: NewLobbyistRegistration
) -> None:

    new_entity = LobbyingEntity()
    new_entity.entity_id = str(uuid.uuid4())
    db_session.add(new_entity)
    db_session.flush()
    db_session.refresh(new_entity)

    contact = {
        "entity_id": new_entity.entity_id,
        "name": form.entity_name,
        "address1": form.entity_address1,
        "address2": form.entity_address2,
        "city": form.entity_city,
        "state": form.entity_state,
        "zipcode": form.entity_zipcode,
        "phone": form.entity_phone,
    }

    contact_info = LobbyingEntityContactInfo(**contact)
    db_session.add(contact_info)

    # now let's set the type
    if form.entity_type.lower() not in LOBBYIST_TYPES:
        Http400("Lobbyist type not known.")

    lelt = LobbyingEntityLobbyistType()
    lelt.lobbyist_type = form.entity_type.lower()
    lelt.entity_id = new_entity.entity_id
    db_session.add(lelt)

    db_session.commit()

    return new_entity


async def update_lobbying_entity(
    db_session: Session, form: UpdateLobbyingEntity
) -> None:

    entity = await get_lobbying_entity_by_id(db_session, form.entity_id)
    if entity is None:
        raise Http400("Lobbying entity does not exist.")

    new_data = {
        "entity_id": form.entity_id,
        "name": form.entity_name,
        "address1": form.entity_address1,
        "address2": form.entity_address2,
        "city": form.entity_city,
        "zipcode": form.entity_zipcode,
        "state": form.entity_state,
        "phone": form.entity_phone,
    }

    new_contact_info = LobbyingEntityContactInfo(**new_data)
    db_session.add(new_contact_info)

    # entity type
    entity_types = []
    if form.entity_firm:
        entity_types.append("firm")
    if form.entity_org:
        entity_types.append("org")
    if form.entity_expenditure:
        entity_types.append("expenditure")

    res = (
        db_session.execute(
            select(LobbyingEntityLobbyistType).filter(
                LobbyingEntityLobbyistType.entity_id == entity.entity_id
            )
        )
        .unique()
        .scalars()
        .all()
    )

    # check if something is missing
    db_entity_types = [x.lobbyist_type for x in res]

    # first add
    for entity_type in entity_types:
        if entity_type not in db_entity_types:
            lelt = LobbyingEntityLobbyistType()
            lelt.lobbyist_type = entity_type
            lelt.entity_id = entity.entity_id
            db_session.add(lelt)

    # then delete
    for db_entity_type in res:
        if db_entity_type.lobbyist_type not in entity_types:
            db_session.delete(db_entity_type)

    db_session.commit()


# relationships (should be idempotent)


async def assoc_filer_with_lobbying_entity(
    db_session: Session,
    filer_id: str,
    entity_id: str,
    commit=True,
):

    lef = (
        db_session.execute(
            select(LobbyingEntityFiler)
            .filter(LobbyingEntityFiler.filer_id == filer_id)
            .filter(LobbyingEntityFiler.entity_id == entity_id)
        )
        .unique()
        .scalar()
    )

    if lef is None:

        lef = LobbyingEntityFiler()
        lef.filer_id = filer_id
        lef.entity_id = entity_id

        db_session.add(lef)
        if commit:
            db_session.commit()

    return lef


async def insert_lobbying_entity_contact_info(db_session: Session, contact_info: dict):
    new_contact_info = LobbyingEntityContactInfo(**contact_info)
    db_session.add(new_contact_info)
    db_session.commit()
