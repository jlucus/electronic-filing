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
    Sequence,
    Numeric
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.bases import CustomBase
from app.utils.date_utils import today
from app.models.init_helpers import init_uuid4

# WARNING: We are using lobbying_entity for the company/org
# that lobbies. We are using lobby_entity for individuals or
# orgs in filings.

LOBBY_ENTITY_TYPES = [
    "client",
    "lobbyist",
    "city_official"
]

class LobbyingLobbyEntity(CustomBase):
    # This can be used across multiple filings
    # A person or a company/organization
    entity_id = Column(UUID, primary_key=True, default=init_uuid4)


class LobbyingLobbyEntityContactInfo(CustomBase):
    # Contact info for a person or company/organization.
    # This is separate, because the same entity can have
    # changing contact info over time, but we need to be able
    # to go back and look at past contact info.
    id = Column(UUID, primary_key=True, default=init_uuid4)
    entity_id = Column(UUID, ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    individual = Column(Boolean, nullable=False, server_default='t')
    name_first = Column(String)
    name_middle = Column(String)
    name_last_or_org = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    city = Column(String)
    zipcode = Column(String)
    state = Column(String)
    country = Column(String, default='US')
    phone = Column(String)    
    
    # this will be used for new data            
    entity_type = Column(String)
    
    # for convenience
    filing_date = Column(DateTime)
    
class LobbyingMuniDecision(CustomBase):
    # A municipal decision on which somebody lobbyies
    decision_id = Column(UUID, primary_key=True, default=init_uuid4)

class LobbyingMuniDecisionInfo(CustomBase):
    # Details on muni decision. These details may change over time
    # so we can have multiple entries here for the same decision.
    # They will be linked to directly from the filing records.
    id = Column(UUID, primary_key=True, default=init_uuid4)
    decision_id = Column(UUID, ForeignKey("lobbying_muni_decision.decision_id"),
                         nullable=False)

    description_short = Column(String, nullable=False)
    description_detail = Column(String)
    outcome_sought = Column(String)


# All data models that have "Filing" in them are specific to an individual
# filing, referenced by filing_id.

class LobbyingFilingMeta(CustomBase):
    # Some lobbying specific extra metadata that we collect for each
    # filing.
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    calendar_year = Column(String, nullable=False)
    amendment_reason = Column(String)

    termination = Column(Boolean, nullable=False, server_default='f')
    start_date = Column(Date)
    end_date = Column(Date)
    registration_filing_id = Column(UUID, ForeignKey("filing.filing_id"))
    
    # a registration amendment allows the lobbyist to change their address.
    # Here we include a reference to their new address (in entity.py).
    lobbying_entity_contact_info_id = (
        Column(Integer,
               ForeignKey("lobbying_entity_contact_info.id"),
               nullable=False)
    )
    filer_contact_info_id = (
        Column(Integer,
               ForeignKey("filer_contact_info.id"),
               nullable=False)
    )
    filer_email = Column(String)
    filer_title = Column(String)
    
    
class LobbyingFilingVerification(CustomBase):
    # Signature part of the filing
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    filer_title = Column(String)
    location = Column(String)
    date = Column(Date, nullable=False)
    signature = Column(String)
    comment = Column(String)
    
class LobbyingFilingDeletedEntity(CustomBase):
    # Amendments to EC-601 and EC-602 allow lobbyists to remove
    # employee lobbyists and clients
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    lobby_entity_contact_info_id = Column(UUID,
                            ForeignKey("lobbying_lobby_entity_contact_info.id"),
                            nullable=False)
    effective_date = Column(Date)
    entity_type = Column(String, nullable=False)
    # Ordinal is important to preserve the order in which
    # information is presented to the user.
    ordinal = Column(Integer, nullable=False, default=-1)

class LobbyingFilingLobbyist(CustomBase):
    # Entries in Schedule A of EC-601
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    lobby_entity_contact_info_id = Column(UUID,
                            ForeignKey("lobbying_lobby_entity_contact_info.id"),
                            nullable=False)
    effective_date = Column(Date)
    ordinal = Column(Integer, nullable=False, default=-1)
    
class LobbyingFilingClient(CustomBase):
    # Entries in Schedule B of EC-601
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    lobby_entity_contact_info_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity_contact_info.id"),
                             nullable=False)
    client_description = Column(String)
    effective_date = Column(Date)
    coalition = Column(Boolean, nullable=False, server_default='f')
    ordinal = Column(Integer, nullable=False, default=-1)

class LobbyingFilingClientCoalitionMember(CustomBase):
    # Entries belonging to clients in Schedule B of EC-601
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    filing_client_id = Column(UUID, ForeignKey("lobbying_filing_client.id"),
                              nullable=False)
    member_lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    member_lobby_entity_contact_info_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity_contact_info.id"),
                             nullable=False)
    client_lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    ordinal = Column(Integer, nullable=False, default=-1)
    
class LobbyingFilingRegActivity(CustomBase):
    # Entries in EC-601 and EC-602, schedule C
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    # values: fundraising, campaign_service, contract_service
    activity_type = Column(String, nullable=False)
    indiv_lobby_entity_id = Column(UUID,
                                        ForeignKey("lobbying_lobby_entity.entity_id"),
                                        nullable=False)
    indiv_lobby_entity_contact_info_id = Column(UUID,
                            ForeignKey("lobbying_lobby_entity_contact_info.id"),
                            nullable=False)    
    counterparty_lobby_entity_id = Column(UUID,
                                          ForeignKey("lobbying_lobby_entity.entity_id"),
                                          nullable=False)
    counterparty_lobby_entity_contact_info_id = Column(UUID,
                    ForeignKey("lobbying_lobby_entity_contact_info.id"),
                    nullable=False)    
    ordinal = Column(Integer, nullable=False, default=-1)

    
class LobbyingFilingMuniDecision(CustomBase):
    # Muni decisions belonging to clients in schedule B
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    decision_id = Column(UUID, ForeignKey("lobbying_muni_decision.decision_id"),
                         nullable=False)
    decision_info_id = Column(UUID, ForeignKey("lobbying_muni_decision_info.id"),
                              nullable=False)
    # if these two are null, then it's an org lobbyist
    lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"))
    filing_client_id = Column(UUID, ForeignKey("lobbying_filing_client.id"))

    ordinal = Column(Integer, nullable=False, default=-1)
    
class LobbyingFilingComment(CustomBase):
    # comments -- per schedule
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    schedule = Column(String, nullable=False)
    comment = Column(String, nullable=False)

class LobbyingFilingFee(CustomBase):
    # fees paid by the lobbyist
    # We allow multiple records here per filing with different status, so
    # that the City admins can update payment status.
    # We are storing org lobbyists and lobbying firms fees in this
    # data model, so the fee dict will be different
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    fee_dict = Column(JSON)
    filing_fee = Column(Numeric)
    status = Column(String, nullable=False)
    notes = Column(String)
    # possible values: pending, paid, updated

    created = Column(DateTime(timezone=True),
                     nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True),
                     nullable=False, default=func.now(),
                     onupdate=func.now())
    
### EC 602 specific
class LobbyingFilingOrgDescription(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    org_description = Column(String)

class LobbyingFilingContactCount(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    contact_count = Column(Integer)
    
### EC-603, EC-604 specific
# schedule A 1 and 2 in ec603, schedule A in ec604
class LobbyingFilingClientMuniContact(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    contact = Column(Boolean, nullable=False, server_default='f')

    # filing id of the registration this is based on
    reg_filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)

    client_lobby_entity_id = Column(UUID,
                                    ForeignKey("lobbying_lobby_entity.entity_id"))
    client_lobby_entity_contact_info_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity_contact_info.id"))
    
    decision_id = Column(UUID, ForeignKey("lobbying_muni_decision.decision_id"))
    decision_info_id = Column(UUID, ForeignKey("lobbying_muni_decision_info.id"))
    
    decision_specifics = Column(String)
    outcome_specifics = Column(String)

    total_compensation = Column(String)
    contingency = Column(Boolean, nullable=False, server_default='f')

    # only ec604
    total_number_of_contacts = Column(Integer, nullable=False, default=-1)

    ordinal = Column(Integer, nullable=False, default=-1)
      
    
class LobbyingFilingActivityExpense(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    date = Column(Date)

    # filing id of the registration this is based on
    reg_filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    
    employment_related = Column(Boolean, nullable=False)
    amount = Column(String)
    amount_range = Column(String)

    description = Column(String)
    
    ordinal = Column(Integer, nullable=False, default=-1)
    
# this model is for schedule_a_1 and schedule_b
class LobbyingFilingLinkedEntity(CustomBase):
    # entity type: lobbyist, payee, payer, city_official, client
    id = Column(UUID, primary_key=True, default=init_uuid4)

    # can be "ClientMuniContact", "ActivityExpense", "ExpenditureMuni"
    link_type = Column(String, nullable=False)
    linked_to_id = Column(UUID, nullable=False)
    
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)

    entity_type = Column(String, nullable=False)
    lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    lobby_entity_contact_info_id = Column(UUID,
                            ForeignKey("lobbying_lobby_entity_contact_info.id"),
                            nullable=False)
    
    department = Column(String)
    job_title = Column(String)
    # used only for ec605
    amount = Column(String)
    
    ordinal = Column(Integer, nullable=False, default=-1)

class LobbyingFilingCampaignContribution(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)

    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)

    # city_candidate, ballot_measure
    contrib_type = Column(String, nullable=False)

    contributor_lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    contributor_lobby_entity_contact_info_id = Column(UUID,
                            ForeignKey("lobbying_lobby_entity_contact_info.id"),
                            nullable=False)

    committee_lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"))
    committee_lobby_entity_contact_info_id = Column(UUID,
                            ForeignKey("lobbying_lobby_entity_contact_info.id"))
    
    candidate_lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"))
    candidate_lobby_entity_contact_info_id = Column(UUID,
                            ForeignKey("lobbying_lobby_entity_contact_info.id"))    
    
    amount = Column(String)
    date = Column(Date)
        
    ordinal = Column(Integer, nullable=False, default=-1)
    
class LobbyingFilingFundraising(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)

    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)

    description = Column(String)

    # lobbyist or other individual
    lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    lobby_entity_contact_info_id = Column(UUID,
                            ForeignKey("lobbying_lobby_entity_contact_info.id"),
                            nullable=False)

    # this could be a committee or a candidate
    committee_lobby_entity_id = Column(UUID,
                                       ForeignKey("lobbying_lobby_entity.entity_id"),
                                       nullable=False)
    committee_lobby_entity_contact_info_id = Column(UUID,
                                ForeignKey("lobbying_lobby_entity_contact_info.id"),
                                nullable=False)
    
    # this is for netfile data
    date_string = Column(String)

    with_other_persons = Column(Boolean, nullable=False, server_default='f')

    total_amount_raised = Column(String, nullable=False)

    ordinal = Column(Integer, nullable=False, default=-1)


class LobbyingFilingFundraisingDateRange(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    lobbying_filing_fundraising_id = Column(UUID, ForeignKey("lobbying_filing_fundraising.id"),
                                            nullable=False)
    date_start = Column(Date, nullable=False)
    date_end = Column(Date, nullable=False)
    ordinal = Column(Integer, nullable=False, default=-1)

class LobbyingFilingCampaignService(CustomBase):
    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)

    # lobbyist or other individual
    lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    lobby_entity_contact_info_id = Column(UUID,
                            ForeignKey("lobbying_lobby_entity_contact_info.id"),
                            nullable=False)
   
    # committeee
    committee_lobby_entity_id = Column(UUID,
                                       ForeignKey("lobbying_lobby_entity.entity_id"))
    committee_lobby_entity_contact_info_id = Column(UUID,
                                ForeignKey("lobbying_lobby_entity_contact_info.id"))
    
    # candidate
    candidate_lobby_entity_id = Column(UUID,
                                       ForeignKey("lobbying_lobby_entity.entity_id"),
                                       nullable=False)
    candidate_lobby_entity_contact_info_id = Column(UUID,
                                        ForeignKey("lobbying_lobby_entity_contact_info.id"),
                                        nullable=False)    

    contingency = Column(Boolean, nullable=False, server_default='f')
    total_compensation = Column(String, nullable=False)
    service_description = Column(String, nullable=False)

    ballot_measure_committee = Column(Boolean, nullable=False, server_default='f')
    ballot_measure_description = Column(String)
    candidate_office_sought = Column(String)
        
    ordinal = Column(Integer, nullable=False, default=-1)

class LobbyingFilingContractService(CustomBase):

    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    lobby_entity_contact_info_id = Column(UUID,
                            ForeignKey("lobbying_lobby_entity_contact_info.id"),
                            nullable=False)

    service_description = Column(String, nullable=False)
    amount = Column(String, nullable=False)

    # department_agency_or_board
    city_lobby_entity_id = Column(UUID,
                                       ForeignKey("lobbying_lobby_entity.entity_id"))
    city_lobby_entity_contact_info_id = Column(UUID,
                                ForeignKey("lobbying_lobby_entity_contact_info.id"))

    ordinal = Column(Integer, nullable=False, default=-1)


# specific to ec605
class LobbyingFilingPreparer(CustomBase):

    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)

    preparer_lobby_entity_id = Column(UUID,
                             ForeignKey("lobbying_lobby_entity.entity_id"),
                             nullable=False)
    preparer_lobby_entity_contact_info_id = Column(UUID,
                            ForeignKey("lobbying_lobby_entity_contact_info.id"),
                            nullable=False)

    title = Column(String)
    
class LobbyingFilingExpenditureMuni(CustomBase):

    id = Column(UUID, primary_key=True, default=init_uuid4)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)

    decision_id = Column(UUID, ForeignKey("lobbying_muni_decision.decision_id"),
                         nullable=False)
    decision_info_id = Column(UUID, ForeignKey("lobbying_muni_decision_info.id"),
                              nullable=False)
    
    total_payments = Column(String)

    ordinal = Column(Integer, nullable=False, default=-1)
