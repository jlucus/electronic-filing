from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    JSON,
    DateTime,
    ForeignKey,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.init_helpers import (
    init_uuid4,
)
from app.models.bases import CustomBase

ACCOUNT_TYPES = [
    "public",
    "filer",
    "admin"
]

ROLE_TYPES = {
    "sei_liason": "SEI Liason" ,
    "super_admin": "Super Admin",
}


class User(CustomBase):
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False)
    account_type = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)

    # if this is a City user and authenticating via Okta
    city = Column(Boolean, nullable=False, server_default='f')

    active = Column(Boolean, nullable=False, server_default='t')

    # confirmations
    email_confirmed = Column(Boolean, nullable=False, server_default='f')
    password_set_reset_secret = Column(String)
    password_set_reset_expire = Column(DateTime(timezone=True))
    
    password_hash = Column(String)
    created = Column(DateTime(timezone=True), nullable=False, default=func.now())
    updated = Column(DateTime(timezone=True), nullable=False, default=func.now(),
                     onupdate=func.now())
    
    
    roles = relationship("Role", secondary="user_role", backref="user", lazy="joined")
    
    def __repr__(self):
        return f"<{self.__tablename__}(username={self.email}, ...>"

class Role(CustomBase):
    id = Column(Integer, primary_key=True)
    account_type = Column(String, nullable=False)
    role_name = Column(String, nullable=False)
    role_type = Column(String, nullable=False)
    role_permissions = Column(JSON)
    permissions = Column(JSON)
    created = Column(DateTime(timezone=True), nullable=False, default=func.now())

class UserRole(CustomBase):
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    role_id = Column(Integer, ForeignKey("role.id"))


    
