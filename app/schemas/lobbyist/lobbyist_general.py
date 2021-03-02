import re
from pydantic import BaseModel, validator

class UpdateLobbyingEntity(BaseModel):
    entity_id: str
    entity_name: str
    entity_address1: str
    entity_address2: str = None
    entity_city: str
    entity_zipcode: str
    entity_state: str
    entity_phone: str
    entity_firm: bool
    entity_org: bool
    entity_expenditure: bool

    @validator('*', pre=True)
    def strip_str(cls, v):
        if isinstance(v, str):
            return v.strip()
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

    @validator('entity_expenditure')
    def check_expenditure(cls, v, values, **kwargs):
        if 'entity_firm' in values and 'entity_org' in values:
            if not v and not values['entity_firm'] and not values['entity_org']:
                print(v,values['entity_firm'],values['entity_org'])
                raise ValueError("One of firm, org, or expenditure must be selected.")
        return v
            

    
class UpdateFilingInProgress(BaseModel):

    form: dict

    
