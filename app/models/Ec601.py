from sqlalchemy import (
    select,
    Column,
    Integer,
    Numeric,
    String,
    Boolean,
    JSON,
    DateTime,
    Date,
    ForeignKey,
    Table,
    Sequence,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.bases import CustomBase
from app.models.init_helpers import init_uuid4



# # Ec601


class Ec601Address(CustomBase): # TODO: <--  could rename to ContactInfo
    id = Column(UUID, primary_key=True, default=init_uuid4)
    line_1 = Column(String, nullable=False)
    line_2 = Column(String, nullable=True)  # optional
    city = Column(String)
    state = Column(String)
    zip = Column(String)
    phone = Column(String)
    path = []  # ["disclosure", "cover", "filer_address"] # also used for schedule_b


# # Ec601 directory


class Ec601EntityAddress(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    entity_id = Column(UUID, ForeignKey("ec601_entity.id"), nullable=False)
    address_id = Column(UUID, ForeignKey("ec601_address.id"), nullable=False)
    # filing_id # <--- Reference filing that this id is from ????


class Ec601Entity(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    is_individual = Column(Boolean, nullable=False)
    name_first = Column(String, nullable=True)
    name_middle = Column(String, nullable=True)
    name_last_or_org = Column(String, nullable=False)
    name_prefix = Column(String, nullable=True)
    name_suffix = Column(String, nullable=True)
    # for netfile data
    name_map = {"id": "@id", "is_individual": "@is_individual"}
    path = ["disclosure", "directory", "entity"]


class Ec601MunicipalDecision(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    description = Column(String, nullable=False)
    outcome_sought = Column(String, nullable=True)
    name_map = {"id": "@id"}
    path = ["disclosure", "directory", "municipal_decision"]


# # Ec601 cover


class Ec601FilerAddress(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filer_id = Column(UUID, ForeignKey("ec601_filer.id"), nullable=False)
    address_id = Column(UUID, ForeignKey("ec601_address.id"), nullable=False)


class Ec601Filer(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)  # from *.efile files
    # netfile_id = Column(String, nullable=True)
    name_map = {"id": "@id"}
    path = ["disclosure", "cover", "filer"]


class Ec601Signature(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    date = Column(Date, nullable=False)
    location = Column(String, nullable=False)
    signer_first_name = Column(String, nullable=False)
    signer_last_name = Column(String, nullable=False)
    signer_title = Column(String, nullable=True)
    path = ["disclosure", "cover", "signature"]


class Ec601Cover(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    calendar_year = Column(String, nullable=False)
    filer_id = Column(UUID, ForeignKey("ec601_filer.id"), nullable=False)
    filer_address_id = Column(UUID, ForeignKey("ec601_address.id"), nullable=False)
    filer_contact_email = Column(String, nullable=True)
    filer_phone = Column(String, nullable=True) #<-- move to FilerAddress
    signature_id = Column(UUID, ForeignKey("ec601_signature.id"), nullable=False)
    path = ["disclosure", "cover"]


# # Ec601 Schedule A


class Ec601ScheduleAEntity(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    schedule_a_id = Column(UUID, ForeignKey("ec601_schedule_a.id"))
    entity_id = Column(UUID, ForeignKey("ec601_entity.id"))


class Ec601ScheduleA(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    count = Column(Integer, nullable=False)
    name_map = {"count": "@count"}
    path = ["disclosure", "schedule_a"]
    # entities = relationship(
    #    "Ec601Entity",
    #    secondary="Ec601ScheduleAEntity",
    #    backref="ec601_schedule_a",
    #    lazy="joined",
    # )


# # Schedule B


class Ec601CoalitionMember(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    schedule_b_id = Column(UUID, ForeignKey("ec601_schedule_b.id"), nullable=True)
    lobbying_client_id = Column(UUID,
                        ForeignKey("ec601_client.id"), nullable=True)
    member_entity_id = Column(UUID, ForeignKey("ec601_entity.id"), nullable=True)
    ordinal = Column(Integer)

class Ec601CoalitionMemberAddress(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    schedule_b_id = Column(UUID, ForeignKey("ec601_schedule_b.id"), nullable=True)
    coalition_member_id = Column(UUID,
                                ForeignKey("ec601_coalition_member.id"), nullable=True)
    address_id = Column(UUID, ForeignKey("ec601_address.id"), nullable=True)

    
class Ec601ClientMunicipalDecision(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    schedule_b_id = Column(UUID, ForeignKey("ec601_schedule_b.id"), nullable=True)
    lobbying_client_id = Column(UUID, ForeignKey("ec601_client.id"), nullable=True)
    decision_id = Column(
        UUID, ForeignKey("ec601_municipal_decision.id"), nullable=False
    )
    ordinal = Column(Integer)

class Ec601ClientAddress(CustomBase): # do records for a specific client differ?
    id = Column(UUID, primary_key=True, default=init_uuid4)
    schedule_b_id = Column(UUID, ForeignKey("ec601_schedule_b.id"), nullable=True)
    client_id = Column(UUID, ForeignKey("ec601_client.id"), nullable=False)
    address_id = Column(UUID, ForeignKey("ec601_address.id"), nullable=False)

class Ec601Client(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    schedule_b_id = Column(UUID, ForeignKey("ec601_schedule_b.id"), nullable=True)
    entity_id = Column(UUID, ForeignKey("ec601_entity.id"), nullable=True)
    client_business_description = Column(String, nullable=True)
    ordinal = Column(Integer)
    # effective_date = Column(Date, nullable=True)  # optional
    # deletion_date # never used, will ignore
    # remove_delete = Column(Boolean, nullable=True)

class Ec601ScheduleB(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    count = Column(Integer, nullable=False)
    name_map = {"count": "@count"}
    path = ["disclosure", "schedule_b"]


# # Schedule C1


class Ec601FundraisingActivity(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    schedule_c1_id = Column(UUID, ForeignKey("ec601_schedule_c1.id"), nullable=False)
    lobbyist_id = Column(UUID, ForeignKey("ec601_entity.id"), nullable=True)
    city_official_id = Column(UUID, ForeignKey("ec601_entity.id"), nullable=True)
    ordinal = Column(Integer)
    
class Ec601ScheduleC1(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    count = Column(Integer, nullable=False)
    name_map = {"count": "@count"}
    path = ["disclosure", "schedule_c_1"]


# # Schedule C2

class Ec601CampaignService(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    schedule_c2_id = Column(UUID, ForeignKey("ec601_schedule_c2.id"), nullable=False)
    lobbyist_id = Column(UUID, ForeignKey("ec601_entity.id"), nullable=True)
    city_official_id = Column(UUID, ForeignKey("ec601_entity.id"), nullable=True)
    ordinal = Column(Integer)

class Ec601ScheduleC2(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    count = Column(Integer, nullable=False)
    name_map = {"count": "@count"}
    path = ["disclosure", "schedule_c_2"]


# # Schedule C3

class Ec601ContractService(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    schedule_c3_id = Column(UUID, ForeignKey("ec601_schedule_c3.id"), nullable=False)
    lobbyist_id = Column(UUID, ForeignKey("ec601_entity.id"), nullable=True)
    other_entity_id = Column(UUID, ForeignKey("ec601_entity.id"), nullable=True) # department_agency_or_board
    ordinal = Column(Integer)

class Ec601ScheduleC3(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    count = Column(Integer, nullable=False)
    name_map = {"count": "@count"}
    path = ["disclosure", "schedule_c_3"]


# # Schedule D1

class Ec601DeletedClient(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    schedule_d1_id = Column(UUID, ForeignKey("ec601_schedule_d1.id"), nullable=False)
    client_id = Column(UUID, ForeignKey("ec601_entity.id"), nullable=False)
    ordinal = Column(Integer)

class Ec601ScheduleD1(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    count = Column(Integer, nullable=False)
    name_map = {"count": "@count"}
    path = ["disclosure", "schedule_d_1"]


# # Schedule D2

class Ec601DeletedLobbyist(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    schedule_d2_id = Column(UUID, ForeignKey("ec601_schedule_d2.id"), nullable=False)
    lobbyist_id = Column(UUID, ForeignKey("ec601_entity.id"), nullable=False)
    ordinal = Column(Integer)

class Ec601ScheduleD2(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    count = Column(Integer, nullable=False)
    name_map = {"count": "@count"}
    path = ["disclosure", "schedule_d_2"]


# Ec601 Filing


class Ec601FilingFee(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    added_lobbyists = Column(Integer, nullable=False)
    added_clients = Column(Integer, nullable=False)
    filing_fee_due = Column(Numeric, nullable=False)
    fee_per_client = Column(Numeric, nullable=True)  # optional
    fee_per_lobbyist = Column(Numeric, nullable=True)  # optional
    path = ["disclosure", "filing_fees"]


class Ec601FilingInformation(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    amendment_sequence_number = Column(Integer, nullable=False)
    amendment_description = Column(String, nullable=True)  # optional
    filing_date = Column(Date, nullable=False)
    amendment_superceded_filing_id = Column(
        String, nullable=True
    )  # this is netfile's integer id
    # amendment_superceded_filing_id = Column(
    #    UUID, ForeignKey("ec601_filing.id"), nullable=False
    # )
    filer_id = Column(UUID, ForeignKey("ec601_filer.id"), nullable=False)
    path = ["disclosure", "filing_information"]


class Ec601Filing(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    efile_id = Column(UUID, nullable=False)
    agency = Column(String, nullable=False)
    version = Column(String, nullable=True)
    type = Column(String, nullable=False)
    allow_municipal_decision_deletion = Column(Boolean, nullable=True)  # optional
    filing_information_id = Column(
        UUID, ForeignKey("ec601_filing_information.id"), nullable=False
    )
    cover_id = Column(UUID, ForeignKey("ec601_cover.id"), nullable=False)
    schedule_a_id = Column(UUID, ForeignKey("ec601_schedule_a.id"), nullable=False)
    schedule_b_id = Column(UUID, ForeignKey("ec601_schedule_b.id"), nullable=False)
    schedule_c1_id = Column(UUID, ForeignKey("ec601_schedule_c1.id"), nullable=False)
    schedule_c2_id = Column(UUID, ForeignKey("ec601_schedule_c2.id"), nullable=False)
    schedule_c3_id = Column(UUID, ForeignKey("ec601_schedule_c3.id"), nullable=False)
    schedule_d1_id = Column(UUID, ForeignKey("ec601_schedule_d1.id"), nullable=False)
    schedule_d2_id = Column(UUID, ForeignKey("ec601_schedule_d2.id"), nullable=False)
    filing_fee_id = Column(UUID, ForeignKey("ec601_filing_fee.id"))
    comment_schedule_a = Column(String, nullable=True)
    comment_schedule_b = Column(String, nullable=True)
    comment_schedule_c = Column(String, nullable=True)
    name_map = {"agency": "@agency", "type": "@type", "version": "@version"}
    path = ["disclosure"]


models = [
    Ec601Entity,
    Ec601Signature,
    Ec601Filer,
    Ec601Filing,
    Ec601FilingFee,
    Ec601FilingInformation,
]
