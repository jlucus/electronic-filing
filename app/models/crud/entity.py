from typing import Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from app.models.entities import (
    ENTITY_TYPES,
    Entity,
    LobbyingEntity,
    LobbyingEntityContactInfo,
    LobbyingEntityLobbyistType,
    LobbyingEntityFiler,
)


# select

async def get_current_lobbying_entity_contact_info_by_entity_id(
    db_session: Session,
    entity_id: str,
):
       return db_session.execute(
            select(LobbyingEntityContactInfo)
            .filter(LobbyingEntityContactInfo.entity_id == entity_id)
            .order_by(LobbyingEntityContactInfo.created.desc())
        ).scalars().first()


# insert

async def insert_entity(
    db_session: Session,
    entity_id: str,
    entity_type: str,
) -> Optional[Entity]:

    new_entity = Entity()
    new_entity.entity_id = entity_id
    new_entity.entity_type = entity_type

    db_session.add(new_entity)

    return new_entity



