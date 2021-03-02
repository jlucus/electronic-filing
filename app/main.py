from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth.exceptions import AuthJWTException
import logging
from app.utils.exception_handlers import authjwt_exception_handler
from app.core.config import API_PREFIX
from app.api import (
    users,
    auth,
    filer,
    filer_lobbyist,
    admin,
    admin_tasks,
    admin_lobbyist,
    public
#    ws,
#    stats,
#    events,
)
#from app.core.config import users_router_prefix
from app.utils.openapi_schema import make_custom_openapi
from app.middlewares.custom_logger import CustomLoggerMiddleware

app = FastAPI(root_path=API_PREFIX)
logging.config.fileConfig('app/core/logging.conf', disable_existing_loggers=False)

origins = [
    "https://efile.pasadev.com",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CustomLoggerMiddleware)

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(filer.router, prefix="/filer", tags=["filer"])
app.include_router(filer_lobbyist.router, prefix="/filer/lobbyist", tags=["filer"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(admin_lobbyist.router, prefix="/admin/lobbyist", tags=["admin"])
app.include_router(admin_tasks.router, prefix="/admin/tasks", tags=["admin"])
app.include_router(public.router, prefix="/public", tags=["public"])

#app.include_router(stats.router, prefix='', tags=['stats'])
#app.include_router(events.router, prefix='', tags=['events'])
#app.include_router(ws.router, prefix='', tags=['websockets'])

app.add_exception_handler(AuthJWTException, authjwt_exception_handler)

app.openapi = make_custom_openapi(app)
