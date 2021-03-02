import logging
import traceback
from fastapi import HTTPException, status

def handle_exc(inst: Exception):
    logging.error(traceback.format_exc())
    if isinstance(inst, HTTPException):
        raise inst
    else:
        Http500()


def HttpExc(status_code: int, detail: str = "HTTP Exception Encountered"):
    raise HTTPException(
        status_code=status_code,
        detail=detail,
    )


def Http400(detail: str = "Bad Request"):
    HttpExc(status_code=400, detail=detail)


def Http401(detail: str = "Unauthorized"):
    HttpExc(status_code=401, detail=detail)


def Http404(detail: str = "Not Found"):
    HttpExc(status_code=404, detail=detail)


def Http500(detail: str = "Internal Server Error"):
    HttpExc(status_code=500, detail=detail)


STRIPE_WEBHOOK_SIG_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate Stripe webhook event signature",
)


UNREGISTERED_USER_EXCEPTION = HTTPException(
    status_code=404, detail="Username not found"
)


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

class AccountPermissionException(HTTPException):
    def __init__(self):
        self.status_code = 401
        self.detail = "This account is not allowed to perform this action."


class AccountException(HTTPException):
    def __init__(self, detail="Account authorization failure."):
        self.status_code = 401
        self.detail = detail
        
        
class EntityNotFoundException(HTTPException):
    def __init__(self):
        self.status_code = 400
        self.detail = "Entity not found."
        

EXPIRED_CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Expired credentials",
    headers={"WWW-Authenticate": "Bearer"},
)
