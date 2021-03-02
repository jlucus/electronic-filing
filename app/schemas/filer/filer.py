import re
from pydantic import BaseModel, validator

class FilerBasic(BaseModel):

    user_id: int
    first_name: str
    middle_name: str
    last_name: str


class FilerContactInfoSchema(BaseModel):

    first_name: str
    middle_name: str = None
    last_name: str
    
    address1: str
    address2: str = None
    city: str
    zipcode: str
    state: str
    phone: str

    effective_date: str = None
    country: str = "US"

    hide_details: bool = True

    @validator('*', pre=True)
    def strip_str(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
    
    @validator(
        'first_name',
        'last_name',
        'address1',
        'city')
    def check_length(cls, v):
        if len(v.strip()) < 3:
            raise ValueError('Name, Address1, and City must '\
                             'be more than 2 characters')
        return v

    @validator('zipcode')
    def check_zip(cls, v):
        if len(v.strip()) < 5:
            raise ValueError('Please provide a valid US zip code')
        return v

    @validator('phone')
    def check_phone(cls, v):
        pattern = re.compile("^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$")
        if pattern.match(v) is None:
            raise ValueError("Please supply a standard 10-digit phone number")
        return v

    @validator('state')
    def check_state(cls, v):
        if len(v.strip()) != 2:
            raise ValueError("Please provide a two-letter state")
        return v

    
    
    
