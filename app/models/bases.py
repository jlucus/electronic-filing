from sqlalchemy.orm import (
    declared_attr,
    declarative_base as db,
)
from app.utils.string_utils import pascal_to_snake


class MyBase:
    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls):
        return pascal_to_snake(cls.__name__)


class MetaCustom(MyBase):
    __table_args__ = {"schema": "public"}


CustomBase = db(cls=MyBase)
