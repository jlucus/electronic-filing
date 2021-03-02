#!/usr/bin/env python
import os
import sys
import binascii
import base64
from datetime import datetime, timezone
import logging
import traceback
import csv
import pandas as pd # try databale instead at some point

sys.path.append(os.getcwd())
from fastapi.encoders import jsonable_encoder
from app.models.users import User
from app.models.stats import (
    Team,
    Quarterback,
    RunningBack,
    Receiver,
)
from app.models.events import PlayerSpot
from app.db.session import LocalSession
from app.db.utils import (
    delete_meta,
    recreate_meta,
)


logging.basicConfig(level=logging.INFO)


def init_users(db_session):

    try:

        # Test Users


        jane = {
            "username": "Jane",
            "password_hash": "$2b$12$yuKDlfzEqBX5ahJosf84IeOGxkIg..iFxmW2vswuSDEbtaiNGPp.e", #
            "created": datetime.now(tz=timezone.utc),
        }

        jack = {
            "username": "Jack",
            "password_hash": "$2b$12$jHFt8DOHEz5IH1RNCR.CW.e/PaQxfdGOLfJ/3DX87Zd7DyHtzbmR.", # secret
            "created": datetime.now(tz=timezone.utc),
        }


        # Create records for all users

        users = [jane, jack]

        for user in users:
            db_session.add(User(**user))
        db_session.commit()
    except Exception as inst:
        print(f"Exception (init_users:user): {inst}")
        db_session.rollback()
        return


def init_db():
    print("* Recreate tables in meta schema")
    recreate_meta()

    db_session = LocalSession()

    print("* Populate users")
    init_users(db_session)


def delete_db():
    print("* Delete tables in meta schema")
    delete_meta()


def main():
    print("\n ** This program will completely delete db tables. **\n")

    options = [
        ("Delete tables in meta db?", delete_db),
        ("Initialize tables in meta db?", init_db),
        #("Initialize team data?", init_teams),
        #("Initialize quarterback table?", init_quarterbacks),
    ]

    for option in options:
        option_text = option[0]
        option_func = option[1]
        choice = ""
        while choice.lower() not in ["y", "n"]:
            choice = input("\n" + option_text + " [y/n]")
            if choice.lower() == "y":
                option_func()


if __name__ == "__main__":
    main()
