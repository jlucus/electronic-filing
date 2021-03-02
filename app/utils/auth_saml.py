import traceback
import logging
import aiohttp
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed
)
from saml2 import (
    BINDING_HTTP_POST,
    BINDING_HTTP_REDIRECT,
    entity,
)
from app.core.config import (
    SAML_METADATA_URL_ADMIN,
    SAML_METADATA_URL_FILER,
    SAML_ACS_URL_ADMIN,
    SAML_ACS_URL_FILER,
    SAML_ENTITY_ID_ADMIN,
    SAML_ENTITY_ID_FILER
)
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config


logger = logging.getLogger("fastapi")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def get_metadata(url):

    async with aiohttp.ClientSession() as client:

        res = await client.get(url, timeout=3)
        return await res.text()


async def saml_client(kind='admin'):

    if kind == 'admin':
        url = SAML_METADATA_URL_ADMIN
        acs_url = SAML_ACS_URL_ADMIN
        entity_id = SAML_ENTITY_ID_ADMIN
    else:
        url = SAML_METADATA_URL_FILER
        acs_url = SAML_ACS_URL_ADMIN
        entity_id = SAML_ENTITY_ID_FILER

    meta = await get_metadata(url)

    settings = {
        'entityid': entity_id,
        'metadata': {
            'inline': [meta],
        },
        'service': {
            'sp': {
                'endpoints': {
                    'assertion_consumer_service': [
                        (acs_url, BINDING_HTTP_REDIRECT),
                        (acs_url, BINDING_HTTP_POST),
                    ],
                },
                # Don't verify that the incoming requests originate from us via
                # the built-in cache for authn request ids in pysaml2
                'allow_unsolicited': True,
                # Don't sign authn requests, since signed requests only make
                # sense in a situation where you control both the SP and IdP
                'authn_requests_signed': False,
                'logout_requests_signed': True,
                'want_assertions_signed': True,
                'want_response_signed': False,
            },
        },
    }    

    spConfig = Saml2Config()
    spConfig.load(settings)
    spConfig.allow_unknown_attributes = True
    saml_client = Saml2Client(config=spConfig)
    return saml_client


