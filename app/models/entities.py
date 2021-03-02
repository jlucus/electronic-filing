from sqlalchemy import (
    select,
    Column,
    Integer,
    String,
    Boolean,
    JSON,
    DateTime,
    Date,
    ForeignKey,
    Table,
    Sequence
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.bases import CustomBase
from app.utils.date_utils import today
from app.models.init_helpers import init_uuid4

LOBBYIST_TYPES = {
    "firm": "Lobbying Firm",
    "org": "Organizational Lobbyist",
    "expenditure": "Expenditure Lobbyist"
}
ENTITY_TYPES = [
    "lobbying",
    "campaign"
]


class Entity(CustomBase):
    entity_id = Column(UUID, primary_key=True)
    entity_type = Column(String)
    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True),
                     nullable=False, default=func.now(),
                     onupdate=func.now())

class LobbyingEntity(CustomBase):

    # ids
    # netfile EntityId from csv file
    entity_id = Column(UUID, primary_key=True)

    human_readable_id = Column(String, ForeignKey("human_readable_id.hr_id"))

    # nefile user id from filers.csv ("Filer ID")
    netfile_user_id = Column(String, nullable=True) 

    # alt ids
    # "FilerId" (uuid)  from filers.csv
    netfile_filer_id = Column(UUID, nullable=True) 

    filer_email_confirmed = Column(Boolean, nullable=False, server_default='f')
    filer_email_code = Column(String)

    # has this been reviewed, does not say anything about filing status
    active = Column(Boolean, nullable=False, server_default='f')
    rejected = Column(Boolean, nullable=False, server_default='f')
    reviewed = Column(Boolean, nullable=False, server_default='f')

    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True),
                     nullable=False, default=func.now(),
                     onupdate=func.now())

    lobbyist_types = relationship("LobbyingEntityLobbyistType")
    filers = relationship("Filer",secondary="lobbying_entity_filer",lazy="joined")
    contact_info = relationship("LobbyingEntityContactInfo")


class LobbyingEntityContactInfo(CustomBase):
    id = Column(Integer, primary_key=True)
    entity_id = Column(UUID, ForeignKey("lobbying_entity.entity_id"), nullable=False)
    name = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    zipcode = Column(String)
    state = Column(String)
    country = Column(String)
    phone = Column(String)

    contact_email = Column(String)

    effective_date = Column(Date(), default=today())

    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True),
                     nullable=False, default=func.now(),
                     onupdate=func.now())

class LobbyingEntityActiveYear(CustomBase):
    id = Column(Integer, primary_key=True)
    lobbyist_type = Column(String, nullable=False)
    entity_id = Column(UUID, ForeignKey("lobbying_entity.entity_id"), nullable=False)
    terminated = Column(Boolean, server_default='f', nullable=False)
    termination_date = Column(DateTime(timezone=True))
    year = Column(String, nullable=False)
    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True),
                     nullable=False, default=func.now(),
                     onupdate=func.now())

class LobbyingEntityLobbyistType(CustomBase):
    id = Column(Integer, primary_key=True)
    lobbyist_type = Column(String, nullable=False)
    entity_id = Column(UUID, ForeignKey("lobbying_entity.entity_id"), nullable=False)

class LobbyingEntityFiler(CustomBase):
    id = Column(Integer, primary_key=True)
    entity_id = Column(UUID, ForeignKey("lobbying_entity.entity_id"), nullable=False)
    filer_id = Column(UUID, ForeignKey("filer.filer_id"), nullable=False)
    active = Column(Boolean, nullable=False, server_default='t')


class CampaignEntity(CustomBase):

    entity_id = Column(UUID, primary_key=True)
    # stub for now


#lobbying_contact_query = (
    #select(LobbyingEntityContactInfo)
    #.filter(LobbyingEntityContactInfo.active == True).alias()
    #)

#lobbying_contact_active = aliased(LobbyingEntityContactInfo, lobbying_contact_query)
#LobbyingEntity.__mapper__.add_property('contact_info',
#                                       relationship(lobbying_contact_active, uselist=False,
#                                                    viewonly=True))


