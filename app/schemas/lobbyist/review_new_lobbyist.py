from pydantic import BaseModel, validator
from app.utils.string_utils import check_uuid4


class ReviewNewLobbyist(BaseModel):
    lobbying_entity_id: str
    task_ref: str
    action: str

    @validator('lobbying_entity_id', pre=True, always=True)
    def check_lobbying_entity_id(cls, v):
        if not check_uuid4(v):
            raise ValueError("Lobbying entity id must be a valid uuid.")
        return v


    @validator('*', pre=True)
    def strip_str(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


    @validator('action')
    def check_action(cls, v):
        if v not in ['activate','reject']:
            raise ValueError("Action can either be activate or reject.")
        return v


    
