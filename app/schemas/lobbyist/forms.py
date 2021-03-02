import re
from pydantic import BaseModel, validator
from typing import Dict
from app.utils.string_utils import is_uuid
from app.utils.date_utils import get_this_year

class Meta(BaseModel):
    form_name: str
    schema_version: str

class Ec601(BaseModel):

    form: str
    meta: Meta
    filing_id: str
    year: str
    amendment: bool
    amendment_reason: str = None
    amends_id: str = None
    lobbying_entity_contact_info_change: bool
    lobbying_entity_contact_info: dict
    filer: dict
    verification: dict
    schedule_a: list
    schedule_b: list
    schedule_c_1: list
    schedule_c_2: list
    schedule_c_3: list
    schedule_d_1: list
    schedule_d_2: list
    directory: dict
    comments: dict

    
