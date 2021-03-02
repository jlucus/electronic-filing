import logging
import time
from typing import Dict
from fastapi import FastAPI, Depends, Request, Body
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from starlette.middleware.base import BaseHTTPMiddleware
import json
from app.core.config import AuthJWTSettings

# this needs to be in each file
@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()

general_logger = logging.getLogger("general")
admin_logger = logging.getLogger("admin")
users_logger = logging.getLogger("users")

class CustomLoggerMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        Authorize: AuthJWT = AuthJWT(request)

        username: str = None
        if (request.url.path == '/auth/refresh'):
            try:
                Authorize.jwt_refresh_token_required()
                username = Authorize.get_jwt_subject()
            except Exception as e:
                pass
        else:
            try:
                Authorize.jwt_optional()
                username = Authorize.get_jwt_subject()
            except AuthJWTException as e:
                username = None

        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        response.headers["X-Process-Time"] = f"{process_time:.2f}"

        general_logger.info(f"{request.client.host} {request.method} {request.url.path} {response.status_code} {process_time:.2f}")

        if username != None:
            msg = f"{request.client.host} {username} {request.method} {request.url.path} {response.status_code} {process_time:.2f}"
            if request.url.path.startswith('/admin'):
                admin_logger.info(msg)
            else:
                users_logger.info(msg)

        return response
