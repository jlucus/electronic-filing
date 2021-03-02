import uuid
import logging
from fastapi import APIRouter, Depends, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, and_, desc
from sqlalchemy.orm import Session
from app.db.utils import get_db
from app.models.users import User
from app.models.messages import Message
from app.api.utility.user import (
    get_active_user,
    get_access_token,
)
from app.api.utility.exc import (
    handle_exc
)
from app.models.users import User


router = APIRouter()

logger = logging.getLogger("fastapi")


