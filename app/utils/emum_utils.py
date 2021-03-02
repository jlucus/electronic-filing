from enum import Enum
from app.utils.string import pascal_to_snake


def enum_to_kvs(enum_, as_snake=True):
    key = pascal_to_snake(enum_.__name__) if as_snake else enum_.__name__
    vals = [item.name for item in enum_]
    return {key: vals}
