import sys
sys.path.append('./')
import copy
import logging
import datetime
import traceback
import requests
from app.core.config import (
    API_HOST,
    API_PREFIX
)

EFILE_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    + "AppleWebKit/537.36 (KHTML, like Gecko) "
    + "Chrome/86.0.4240.183 Safari/537.36"
)
EFILE_FILER_AUTH_URL = API_HOST + API_PREFIX + "/auth/filer-login"
EFILE_ME_URL = API_HOST + API_PREFIX + "/auth/me"
HEADERS = {
    "User-Agent": EFILE_USER_AGENT,
}


def get_efile_filer_session(email, password):
    
    efile_session = requests.Session()
    efile_auth_data = {
        "username": email,
        "password": password
    }
    efile_session.headers.update(HEADERS)
    rlogin = efile_session.post(
        EFILE_FILER_AUTH_URL,
        json=efile_auth_data,
        headers=HEADERS,
        verify=False
    )

    rjson = rlogin.json()
    efile_session.headers.update({'Authorization' :
                                  f"Bearer {rjson['access_token']}"})

    return efile_session
                                  
    

if __name__ == "__main__":

    get_efile_filer_session("ott+jim@pasaconsult.com","secret")

