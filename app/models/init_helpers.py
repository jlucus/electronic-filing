from uuid import uuid4
from datetime import datetime, timezone


# Helpers


def init_uuid4():
    return str(uuid4())


def datetime_now_utc():
    return datetime.now(tz=timezone.utc)
