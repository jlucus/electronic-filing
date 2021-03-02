import re
from pydantic import BaseModel, validator
from app.models.entities import (
    LOBBYIST_TYPES
)

class NewLobbyistRegistration(BaseModel):
    entity_name: str
    entity_address1: str
    entity_address2: str
    entity_city: str
    entity_zipcode: str
    entity_state: str
    entity_phone: str
    entity_type: str  # ['org', 'firm', 'expenditure']
    filer_first_name: str
    filer_middle_name: str = None
    filer_last_name: str
    filer_email: str
    recaptcha: str = None

    @validator('*', pre=True)
    def strip_str(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @validator('filer_email')
    def check_email(cls, v):
        pattern = re.compile('^[a-z0-9]+[\._\+]?[a-z0-9]+[@]\w+[.]\w{2,3}$')
        if pattern.match(v) is None:
            raise ValueError('Please provide a valid email address.')
        return v

    @validator(
        'entity_name',
        'entity_address1',
        'entity_city')
    def check_length(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Name, Address1, and City must '\
                             'be more than 2 characters')
        return v

    @validator('entity_zipcode')
    def check_zip(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Please provide a valid US zip code')
        return v

    @validator('entity_phone')
    def check_phone(cls, v):
        pattern = re.compile("^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$")
        if pattern.match(v) is None:
            raise ValueError("Please supply a standard 10-digit phone number")
        return v

    @validator('entity_state')
    def check_state(cls, v):
        if len(v.strip()) != 2:
            raise ValueError("Please provide a two-letter state")
        return v

    @validator('entity_type')
    def check_entity_type(cls, v):
        if v not in LOBBYIST_TYPES:
            raise ValueError("Please provide a valid lobbyist type.")
        return v
