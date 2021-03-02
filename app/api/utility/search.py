from fastapi import APIRouter, Depends, Response, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.models.crud.filer import get_all_filer_ids_by_last_name
from app.models.crud.filings import (
    get_filing_by_id,
    get_all_lobbyist_filings_by_all_filer_ids,
    get_all_filings_by_all_filer_ids,
    get_filing_by_public_doc,
    get_filing_metadata_by_public_doc,
    get_lobbyist_filing_metadata_by_public_doc,
)
from app.models.crud.lobbyist import (
    get_lobbying_entity_filer_ids_by_company,
)
from app.models.crud.humane_ids import (
    get_e_filer_id_by_orig_amendment,
    get_e_filer_id_by_prev_amendment,
)
from app.models.filings import FILING_TYPE_MAPPING, FILING_TYPE_DESCRIPTION
from app.api.utility.misc import generate_doc_url


async def get_all_filings(
    db_session: Session,
    query: str,
    start_date: str,
    end_date: str,
) -> list:
    filers = await get_all_filer_ids_by_last_name(db_session, query)

    # get all filings for each id
    all_filings = await get_all_filings_by_all_filer_ids(
        db_session, filers, start_date, end_date
    )

    filings_json = jsonable_encoder(all_filings)

    return filings_json


async def get_all_lobbyist_filings(
    db_session: Session,
    query: str,
    start_date: str,
    end_date: str,
) -> list:
    lobbyist = await get_lobbying_entity_filer_ids_by_company(db_session, query)

    all_lobbyist_filings = await get_all_lobbyist_filings_by_all_filer_ids(
        db_session, lobbyist, start_date, end_date
    )

    all_lobbyist_filings_json = jsonable_encoder(all_lobbyist_filings)

    return all_lobbyist_filings_json


async def convert_amend_ids_to_efile_ids(
    db_session: Session,
    filings: list,
):
    # change ammend to e_filing_id
    amendment_orig = []
    amendment_prev = []
    for each in filings:
        # We need to convert these values
        if each["amendment"]:
            amendment_orig.append(each["amends_orig_id"])
            amendment_prev.append(each["amends_prev_id"])

    amendment_orig_efile_ids = await get_e_filer_id_by_orig_amendment(
        db_session, amendment_orig
    )

    amendment_prev_efile_ids = await get_e_filer_id_by_prev_amendment(
        db_session, amendment_prev
    )

    amendment_orig_efile_ids_list = jsonable_encoder(amendment_orig_efile_ids)
    amendment_prev_efile_ids_list = jsonable_encoder(amendment_prev_efile_ids)

    amendment_orig_efile_ids_dict = {}
    amendment_prev_efile_ids_dict = {}

    for each in amendment_orig_efile_ids_list:
        amendment_orig_efile_ids_dict[each["amends_orig_id"]] = each["e_filing_id"]

    for each in amendment_prev_efile_ids_list:
        amendment_prev_efile_ids_dict[each["amends_prev_id"]] = each["e_filing_id"]

    for each in filings:
        if each["amendment"] == True:
            if each["amends_orig_id"] in amendment_orig_efile_ids_dict:
                each["amends_orig_id"] = {
                    "orig_id": each["amends_orig_id"],
                    "human_id": amendment_orig_efile_ids_dict[each["amends_orig_id"]],
                }
            else:
                each["amends_orig_id"] = {
                    "orig_id": each["amends_orig_id"],
                    "human_id": "Not electronically filed",
                }
    for each in filings:
        if each["amendment"] == True:
            if each["amends_prev_id"] in amendment_prev_efile_ids_dict:
                each["amends_prev_id"] = {
                    "prev_id": each["amends_prev_id"],
                    "human_id": amendment_prev_efile_ids_dict[each["amends_prev_id"]],
                }
            else:
                each["amends_prev_id"] = {
                    "prev_id": each["amends_prev_id"],
                    "human_id": "Not electronically filed",
                }


async def get_filing_url_by_public_doc_id(db_session: Session, public_doc_id):
    filing = await get_filing_by_public_doc(db_session, public_doc_id)

    filing_json = jsonable_encoder(filing)

    if filing_json is None:
        return filing_json

    return generate_doc_url(filing_json["filing_type"], public_doc_id)


async def get_filing_metadata_by_public_doc_id(db_session: Session, public_doc_id):
    filing_metadata = await get_filing_metadata_by_public_doc(db_session, public_doc_id)

    filing_metadata_json = jsonable_encoder(filing_metadata)

    return filing_metadata_json


async def get_lobbyist_filing_metadata_by_public_doc_id(
    db_session: Session, public_doc_id
):
    lobbyist_filing_metadata = await get_lobbyist_filing_metadata_by_public_doc(
        db_session, public_doc_id
    )

    lobbyist_filing_metadata_json = jsonable_encoder(lobbyist_filing_metadata)

    return lobbyist_filing_metadata_json


async def get_all_previous_filing_amendments(db_session: Session, filing_id: str):
    # Dangerous Code!
    # Must definitely refactor this!
    amendments = []
    index = 0
    id = await get_filing_by_id(db_session, filing_id)
    amendments.append(jsonable_encoder(id))
    while True:
        if not amendments[index]["amendment"]:
            break
        id = await get_filing_by_id(db_session, amendments[index]["amends_prev_id"])
        amendments.append(jsonable_encoder(id))
        index += 1

    # remove first as it is original
    amendments.pop(0)

    return amendments


async def get_metadata(db_session: Session, public_doc_id):
    metadata = await get_filing_metadata_by_public_doc_id(db_session, public_doc_id)

    if metadata is None:
        metadata = await get_lobbyist_filing_metadata_by_public_doc_id(
            db_session, public_doc_id
        )
    else:
        # We know not a series 600
        metadata["name"] = metadata["last_name"] + ", " + metadata["first_name"]

    metadata["filing_description"] = FILING_TYPE_DESCRIPTION[metadata["filing_type"]]
    metadata["filing_type"] = FILING_TYPE_MAPPING[metadata["filing_type"]]

    # get all amendments if available
    if metadata["amendment"]:
        all_amendments = await get_all_previous_filing_amendments(
            db_session, metadata["filing_id"]
        )

        metadata["all_amendments"] = all_amendments

    return metadata
