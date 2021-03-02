from pydantic import BaseModel

class Token(BaseModel):
    token: str

class Login(BaseModel):
    username: str
    password: str

class Password(BaseModel):
    token: str
    password: str


