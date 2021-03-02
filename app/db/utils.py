import sys
from sqlalchemy import create_engine, inspect
from sqlalchemy.schema import CreateSchema
from app.models.bases import CustomBase
from app.db.helpers import (
    check_if_db_exists,
    drop_database,
    create_database
)
from app.core.config import PG_URI
from app.db.session import (
    LocalSession
)

# helpers


def get_db():
    try:
        db_session = LocalSession()
        yield db_session
    finally:
        db_session.close()



def create_db():
    if not check_if_db_exists(PG_URI):
        create_database(PG_URI)
    engine = create_engine(PG_URI)
    CustomBase.metadata.create_all(engine)

    return engine
    

def delete_db():
    if check_if_db_exists(PG_URI):
        drop_database(PG_URI)
 

def recreate_db():
    delete_db()
    engine = create_db()
    return engine
