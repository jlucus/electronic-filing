import logging
import aiohttp
import urllib
from tenacity import retry, stop_after_attempt, wait_fixed
from app.core.config import RECAPTCHA_SECRET_KEY, S3_PUBLIC_BUCKET, S3_AWS_REGION

logger = logging.getLogger("fastapi")


@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
async def check_recaptcha_response(g_recaptcha_response: str):
    data = {"secret": RECAPTCHA_SECRET_KEY, "response": g_recaptcha_response}
    encdata = urllib.parse.urlencode(data)
    url = "https://www.google.com/recaptcha/api/siteverify"

    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=encdata) as res:
            res = await res.json()

    return res["success"]


def generate_doc_url(filing_type, doc_id):
    url_domain = "https://" + "efile-sd-public-dev" + ".s3-us-west-2.amazonaws.com/"
    if filing_type in ["fppc801", "fppc802", "fppc803", "fppc806"]:
        return url_domain + "ser800/" + doc_id + ".pdf"
    elif filing_type in ["fppc700"]:
        return url_domain + "sei/fppc700/" + doc_id + ".pdf"
    elif filing_type in [
        "ec601",
        "ec602",
        "ec603",
        "ec604",
        "ec605",
    ]:
        return url_domain + "lobbyist/" + filing_type + "/" + doc_id + ".pdf"
