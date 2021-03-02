import sys
import traceback
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
import sqlalchemy.exc
from app.core import config

def check_if_db_exists(uri):
    # This is a helper function because
    # database_exists is currently broken, but will
    # be fixed in furture releases of sqlalchemy-utils.
    
    url = make_url(uri)
    if hasattr(config,"PG_BACKUP_USER_PASS") and config.PG_BACKUP_USER_PASS is not None:
        local_uri = f"postgresql+psycopg2://" + config.PG_BACKUP_USER_PASS +\
            f"@{url.host}/{url.database}"
    else:
        local_uri = f"postgresql+psycopg2://postgres:@{url.host}/{url.database}"

    try:
        engine = create_engine(local_uri)
        engine.execute("select 1")

    except sqlalchemy.exc.OperationalError as e:
        error = str(e)
        if "does not exist" in error:
            return False
        raise
    
    except Exception as e:
        raise 

    return True


def drop_database(uri):

    url = make_url(uri)

    conn = psycopg2.connect(dbname="postgres",
                            host=url.host,
                            user=url.username,
                            password=url.password,
                            port=url.port)

    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"SELECT pg_terminate_backend(pid) FROM "\
                f"pg_stat_activity WHERE datname = '{url.database}'")
    cur.execute(f"drop database {url.database}")

    return True

def create_database(uri):

    url = make_url(uri)

    conn = psycopg2.connect(dbname="postgres",
                            host=url.host,
                            user=url.username,
                            password=url.password,
                            port=url.port)

    conn.autocommit = True
    cur = conn.cursor()

    cur.execute(f"create database {url.database}")

    return True
        
