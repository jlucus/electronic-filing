from typing import List, Tuple, Optional
from pydantic import BaseModel, UUID4


# document handling

class DocRef(BaseModel):
    filename: str
    document_id: UUID4


class DocList(BaseModel):
    files: List[DocRef]


# Team

class TeamBody(BaseModel):
    local_name: str
    team_name: str
    team_code: str
    color1: str = '#033369'
    color2: str = '#000'
    color3: str = '#fff'
    logo_url: str = '/logos/nfl-logo.png'
    stadium: str = '<stadium>'
    owner: str = '<owner>'
