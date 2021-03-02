import sys
import json
import urllib3
import pytest
sys.path.append('./')
from app.core.config import (
    API_HOST,
    API_PREFIX
)
from app.utils.client import (
    get_efile_filer_session
)
from helpers.lobbyist_helpers import (
    remove_filing
)


def test_ec601_filing():

    url = API_HOST + API_PREFIX + "/filer/lobbyist/filing/ec601/new"
    email = "ott+jim@pasaconsult.com"
    password = "secret"
    
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    session = get_efile_filer_session(email, password)

    # make the filing
    payload = {
        "lobbying_entity_id": "45352737-d6f5-4f4f-bce7-c9116e0879b7",
        "filing_type": "ec601",
        "year": "2021",
        "quarter": None,
        "amends_id": None
    }

    res = session.post(url, json=payload)
    rjson = res.json()
    filing_id = rjson['filing_id'] 
    assert(rjson.get('filing_id'))
    
    # get the filing
    url = API_HOST + API_PREFIX + f"/filer/lobbyist/filing/ec601/{filing_id}"
    res = session.get(url)
    rjson = res.json()

    # put the filing
    res = session.put(url, json={"form": rjson['data']})
    assert(res.json()['success'])

    # now replace the filing with a test json we have on file
    testfile = "test/data/ec601-mock-data.json"
    with open(testfile,"r") as infile:
        indata = infile.read()

    # replace the filing id
    indata = json.loads(indata)
    indata['filing_id'] = filing_id

    # put the filing
    res = session.put(url, json={"form": indata})
    assert(res.json()['success'])

    # finalize the filing
    furl = url + "/finalize"
    res = session.post(furl, json={"form": indata})
    assert(res.json()['success'])

    # this should now not work
    res = session.put(url, json={"form": indata})
    assert(res.status_code == 400)
    assert(res.json()['detail'] == 'Filing cannot be edited')

    
    
