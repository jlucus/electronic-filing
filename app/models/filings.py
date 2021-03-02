from sqlalchemy import (
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
    Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.bases import CustomBase
from app.models.init_helpers import init_uuid4

SEI_SUBTYPES = ["assuming office", "leaving office", "annual", "candidate", "mid-year"]

FILING_TYPES = [
    "ec700",
    "fppc700",
    "fppc801",
    "fppc802",
    "fppc803",
    "fppc806",
    "ec601",
    "ec602",
    "ec603",
    "ec604",
    "ec605",
]

FILING_TYPE_MAPPING = {
    "ec700": "EC-700",
    "fppc700": "FPPC 700",
    "fppc801": "FPPC 801",
    "fppc802": "FPPC 802",
    "fppc803": "FPPC 803",
    "fppc806": "FPPC 806",
    "ec601": "EC-601",
    "ec602": "EC-602",
    "ec603": "EC-603",
    "ec604": "EC-604",
    "ec605": "EC-605",
}

FILING_TYPE_DESCRIPTION = {
    "ec700": "Mid-Year Gift Report",
    "fppc700": "Statement of Economic Interests",
    "fppc801": "Payments to Agency",
    "fppc802": "Ceremonial Role Events and Ticket/Admission Distribution",
    "fppc803": "Behest Payments",
    "fppc806": "Public Official Appointments",
    "ec601": "Lobbyist Firm Registration",
    "ec602": "Organizational Lobbyist Registration",
    "ec603": "Quarterly Lobbying Report (Firm)",
    "ec604": "Quarterly Lobbying Report (Org)",
    "ec605": "Expenditure Lobbyist Quarterly Report",
}

# we need filed fee pending so that
# we can deal with filed lobbyist forms
# for which fee has not been paid
STATUS = [
    "new",
    "in progress",
    "locked",
    "filed fee pending",
    "filed",
    "canceled",
]


class Filing(CustomBase):

    filing_id = Column(UUID, primary_key=True, default=init_uuid4)

    # we assign this only once a form has actually been filed
    e_filing_id = Column(String, ForeignKey("e_filing_id.e_filing_id"))

    # this could be in sei specific data model
    fppc_id = Column(String)

    # this is the id of the currently editing filer
    # or, if no longer editing, the last signing filer.
    # For campaign we'll need to add signers.
    filer_id = Column(UUID, ForeignKey("filer.filer_id"))
    entity_id = Column(UUID)

    efiled = Column(Boolean, nullable=False, server_default="t")

    termination = Column(Boolean, nullable=False, server_default="f")
    amendment = Column(Boolean, nullable=False, server_default="f")

    amends_orig_id = Column(UUID)
    amends_prev_id = Column(UUID)
    amendment_number = Column(Integer)

    form_name = Column(String)
    filing_type = Column(String)
    filing_subtypes = relationship("FilingSubtype")

    status = Column(String, nullable=False)

    doc_public = Column(String)
    doc_private = Column(String)

    filing_date = Column(DateTime)
    period_start = Column(Date)
    period_end = Column(Date)
    deadline = Column(Date)

    created = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated = Column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )

    # this could be in sei specific data model
    fppc_transferred_at = Column(DateTime(timezone=True))

    __table_args__ = (
        Index("idx_filing_id", "filing_id"),
        Index("idx_filer_id", "filer_id"),
    )


class FilingSubtype(CustomBase):
    id = Column(Integer, primary_key=True)
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), nullable=False)
    filing_subtype = Column(String, nullable=False)


class FilingRaw(CustomBase):
    filing_id = Column(UUID, ForeignKey("filing.filing_id"), primary_key=True)
    raw_json = Column(JSON)
    created = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated = Column(
        DateTime(timezone=True), nullable=False, default=func.now(), onupdate=func.now()
    )
