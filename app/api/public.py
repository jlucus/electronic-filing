import logging
from typing import Optional
import traceback
from fastapi import APIRouter, Depends, Response, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.db.utils import get_db
from app.models.crud.filings import (
    get_filing_by_public_doc,
    get_lobbyist_filing_by_public_doc,
    get_filing_by_id,
)
from app.models.filings import FILING_TYPE_MAPPING, FILING_TYPE_DESCRIPTION
from app.api.utility.misc import generate_doc_url
from app.api.utility.search import (
    get_all_filings,
    get_all_lobbyist_filings,
    convert_amend_ids_to_efile_ids,
    get_filing_url_by_public_doc_id,
    get_metadata,
)

from app.api.utility.exc import (
    handle_exc,
    Http400,
    Http404,
)


router = APIRouter()

logger = logging.getLogger("general")


@router.get("/search")
async def search(
    query: str,
    start_date: str = None,
    end_date: str = None,
    db_session: Session = Depends(get_db),
):
    try:
        if query is None:
            raise Http400("Search cannot be empty.")

        # get filers that match query by last name
        filings = await get_all_filings(db_session, query, start_date, end_date)
        lobbyist_filings = await get_all_lobbyist_filings(
            db_session, query, start_date, end_date
        )

        if len(filings) == 0 and len(lobbyist_filings) == 0:
            return {"success": "true", "data": []}

        for filing in filings:
            filing["description"] = (
                FILING_TYPE_DESCRIPTION[filing["filing_type"]]
                + "; "
                + filing["filing_subtype"]
            )
            filing["filing_type"] = FILING_TYPE_MAPPING[filing["filing_type"]]
            if filing["doc_public"] == None:
                # filing not electronically filed
                filing["filing_type"] += "; Not electronically filed."
            filing["filer"] = filing["last_name"] + ", " + filing["first_name"]

        for lobbyist in lobbyist_filings:
            lobbyist["description"] = FILING_TYPE_DESCRIPTION[lobbyist["filing_type"]]
            lobbyist["filing_type"] = FILING_TYPE_MAPPING[lobbyist["filing_type"]]
            if lobbyist["doc_public"] == None:
                # filing not electronically filed
                lobbyist["filing_type"] += "; Not electronically filed."

        filings.extend(lobbyist_filings)

        await convert_amend_ids_to_efile_ids(db_session, filings)

        return {"success": "true", "data": filings}

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)


@router.get("/document")
async def get_document(
    doc_id: str = None,
    filing_id: str = None,
    db_session: Session = Depends(get_db),
):
    try:
        if doc_id is None and filing_id is None:
            raise Http400("A document id or filing id must be provided.")

        if doc_id is not None:
            url = await get_filing_url_by_public_doc_id(db_session, doc_id)

            if url is None:
                raise Http404("Filing document was not found.")

            return {"success": "true", "data": {"url": url}}

        else:

            original_filing = await get_filing_by_id(db_session, filing_id)

            original_filing_json = jsonable_encoder(original_filing)

            if len(original_filing_json) == 0:
                raise Http404("Filing document was not found.")

            doc_id = original_filing_json["doc_public"]

            url = await get_filing_url_by_public_doc_id(db_session, doc_id)

            if url is None:
                raise Http404("Filing document was not found.")

            return {"success": "true", "data": {"url": url}}

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)


@router.get("/document/metadata")
async def get_document_metadata(
    doc_id: str = None,
    filing_id: str = None,
    db_session: Session = Depends(get_db),
):

    try:
        if doc_id is None and filing_id is None:
            raise Http400("A document id or filing id must be provided.")

        if doc_id is not None:
            metadata = await get_metadata(db_session, doc_id)

            return {"success": "true", "data": metadata}

        else:
            # need to make this into its own function
            original_filing = await get_filing_by_id(db_session, filing_id)

            original_filing_json = jsonable_encoder(original_filing)

            if len(original_filing_json) == 0:
                raise Http404("Filing document was not found.")

            doc_id = original_filing_json["doc_public"]

            # up to here

            metadata = await get_metadata(db_session, doc_id)

            return {"success": "true", "data": metadata}

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)
