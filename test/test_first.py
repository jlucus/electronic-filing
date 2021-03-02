import sys
import pytest
import urllib3
sys.path.append('./')
from app.core.config import (
    API_HOST,
    API_PREFIX
)
from app.utils.client import (
    get_efile_filer_session
)




def test_get_filer_session():

    email = "ott+jim@pasaconsult.com"
    password = "secret"

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    res = get_efile_filer_session(email, password)

    assert(res.headers.get("Authorization") is not None)

    
def test_get_filer_info():
    
    email = "ott+jim@pasaconsult.com"
    password = "secret"

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session = get_efile_filer_session(email, password)
 
    url = API_HOST + API_PREFIX + "/filer/info"
    
    res = session.get(url)
    rjson = res.json()
    
    assert(rjson['success'])

    

    

    
