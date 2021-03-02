from pydantic import BaseModel

class UserBasic(BaseModel):

    email: str
    account_type: str
    first_name: str
    last_name: str
    middle_name: str = None
    city: bool = False
    active: bool = True


class UserResetPassword(BaseModel):

    password: str
    token: str

class ResetPasswordRequest(BaseModel):

    email: str
    recaptcha: str = None
