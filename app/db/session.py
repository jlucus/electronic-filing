from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from app.core import config


# main glass db

engine = create_engine(config.PG_URI, future=True, pool_pre_ping=True)

db_session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
)

LocalSession = sessionmaker(autocommit=False, autoflush=False,
                            bind=engine, future=True)
