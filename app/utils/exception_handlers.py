from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse
from fastapi import Request

async def authjwt_exception_handler(
    request: Request, exc: AuthJWTException
) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message}
    )
