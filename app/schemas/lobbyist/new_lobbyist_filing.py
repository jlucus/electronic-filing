import re
from pydantic import BaseModel, validator
from app.utils.string_utils import is_uuid
from app.utils.date_utils import get_this_year
import uuid

class NewLobbyistFiling(BaseModel):
    lobbying_entity_id: str
    filing_type: str
    year: str
    quarter: str = None
    amends_id: str = None

    @validator('*', pre=True)
    def strip_str(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @validator('lobbying_entity_id',
               'amends_id')
    def check_uuids(cls, v):
        if v is not None:
            if not is_uuid(v):
                raise ValueError('lobbying_entity_id,'\
                                 ' amends_id must be UUID4')
        return v

    @validator('filing_type')
    def check_type(cls, v):
        LOBBYIST_TYPES = ['ec601','ec602','ec603','ec604','ec605']
        if v not in LOBBYIST_TYPES:
            raise ValueError(f"v is a filing type we don't recognize.")
        return v

    @validator('year')
    def check_year(cls, v):
        today_year = int(get_this_year())
        int_year = int(v)
        if int_year < 2020 and int_year > today_year:
            raise ValueError("Invalid year specified")
        return v

    @validator('quarter')
    def check_quarter(cls, v, values, **kwargs):
        if values['filing_type'] in ['ec603','ec604','ec605']:
            if v[0] != 'Q' or v[1] not in ["1","2","3","4"]:
                raise ValueError("Invalid quarter.")
        return v

