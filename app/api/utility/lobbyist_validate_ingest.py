import json
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.schemas.lobbyist.forms import (
    Ec601
)
from pydantic.error_wrappers import ValidationError
from app.schemas.lobbyist.lobbyist_general import (
    UpdateFilingInProgress
)
from app.models.filings import (
    Filing,
    FilingRaw
)
from app.api.utility.exc import (
    Http400
)

async def validate_cleanup_ec601(payload):

    ec601 = Ec601(**payload.form)

    # do all sorts of other validation and cleanup, in
    # particular in the directory

    payload.form = ec601.dict()
    
    return payload

async def validate_lobbyist_filing(
    db_session: Session,
    filing: Filing,
    payload: UpdateFilingInProgress,
):
    try:

        if filing.filing_type == 'ec601':
            return await validate_cleanup_ec601(payload)
        
        else:
            raise Http400(detail="Form not yet implemented")

    except ValidationError as e:
        raise Http400(detail=json.loads(e.json()))
        
