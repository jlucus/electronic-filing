from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    JSON,
    Date,
    DateTime,
    ForeignKey,
    Table,
    Sequence
)
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, aliased
from sqlalchemy.sql import func
from app.models.init_helpers import (
    init_uuid4,
)
from app.models.bases import CustomBase
from app.models.users import User
from app.utils.date_utils import today

FILER_TYPES = {
    "sei": "Statement of Economic Interest",
    "sei-87200": "Statement of Economic Interest 87200",
    "sei-EC700": "Statement of Economic Interest EC-700 Gift Report",
    "lobbyist": "Lobbyist",
    "campaign": "Campaign",
    "candidate": "Candidate",
    "ser800": "Series 800"
}

ID_SEQ = Sequence('filer_id_sequence', minvalue=100000, start=100000)

class FilerContactInfo(CustomBase):
    id = Column(Integer, primary_key=True)
    
    # Filers can change their names, but nevertheless all filings
    # should be discoverable base on any of their names
    
    filer_id = Column(UUID, ForeignKey("filer.filer_id"), nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)

    # address data
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    zipcode = Column(String)
    state = Column(String)
    country = Column(String, nullable=False, default="US")
    phone = Column(String)

    # normally, the email never changes, however, we have historic netfile
    # data to deal with, so we'll also store email hre
    email = Column(String)
    
    # this may be needed for particular kinds of filers
    # who must report changes of address right away and if
    # the addressed changed earlier than allowed they may
    # get dinged by the Ethic's commission
    effective_date = Column(Date(), default=today())

    hide_details = Column(Boolean, nullable=False, server_default='t')
    
    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True),
                     nullable=False, default=func.now(),
                     onupdate=func.now())

# This gives us a scalar name, accessible via filer.name.first_name etc.
# There must only be one FilerName that is active at a time.



class Filer(CustomBase):

    filer_id = Column(UUID, primary_key=True, default=init_uuid4)

    # there can be filers that are not efile users
    user_id = Column(Integer, ForeignKey("user.id"))

    # this info is also in user, but we need to have it separately here
    # because there can be filers that are not users
    email = Column(String)

    human_readable_id = Column(String, ForeignKey("human_readable_id.hr_id"))
    
    # legacy
    netfile_filer_id = Column(String)
    netfile_user_id = Column(String)
    
    active = Column(Boolean)
    
    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True),
                     nullable=False, default=func.now(),
                     onupdate=func.now())
    filer_types = relationship("FilerFilerType")

    user = relationship("User")
    contact_infos = relationship("FilerContactInfo")

#    name = relationship(filer_name_active, uselist=False, viewonly=True)


# a filer can be multiple filer types
 
class FilerFilerType(CustomBase):
    id = Column(Integer, primary_key=True)
    filer_id = Column(UUID, ForeignKey("filer.filer_id"), nullable=False)
    filer_type = Column(String, nullable=False)
    

    
#filer_name_query = select(FilerName).filter(FilerName.active == True).alias()
#filer_name_active = aliased(FilerName, filer_name_query)
#Filer.__mapper__.add_property('name', relationship(filer_name_active, uselist=False, viewonly=True))
