import re
import uuid
from dateutil.parser import parse
import datetime


# conversion helpers


def pascal_to_snake(a_string):
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("_", a_string).lower()


def to_date(s):
    return parse(s).date()


def to_float2(s):
    return round(float(s), 2)

def to_bool(s):
    return True if s.lower() == "true" else False

# "type" check helpers


def is_str(s):
    try:
        return isinstance(s, str)
    except:
        return False


def is_uuid(id, version=4):
    # we are ignoring version...
    try:
        uuid_obj = uuid.UUID(id, version=None)
        return str(uuid_obj) == id
    except Exception:
        return False


def check_uuid4(id):
    return is_uuid(id, 4)


def is_float(s):
    try:
        float(s)
        return True
    except Exception:
        return False


def is_int(s):
    try:
        int(s)
        return True
    except Exception:
        return False


def is_bool(s):
    try:
        low_s = s.lower()
        return low_s == "true" or low_s == "false"
    except Exception:
        return False


def is_date(s):
    try:
        date = parse(s).date()
        return isinstance(date, datetime.date)
    except Exception:
        return False
