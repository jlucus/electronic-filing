import os
from dotenv import load_dotenv
from pydantic import BaseModel
#from fastapi.security import OAuth2PasswordBearer

# [Load .env file]

load_dotenv()

# [eFile environment]
EFILE_ENV = os.getenv("EFILE_ENV", "staging")

# [Hosts]

APP_HOST = os.getenv("APP_HOST")
API_HOST = os.getenv("API_HOST")
API_PREFIX = os.getenv("API_PREFIX","")

# timezone
TIMEZONE = "America/Los_Angeles"

# [Router prefixes]

# we can hardcode those, they don't change


# [AUTH]


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_SECONDS = 3600
ACCESS_TOKEN_EXPIRE_SECONDS = os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 300)
COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN")


class AuthJWTSettings(BaseModel):
    authjwt_secret_key: str = SECRET_KEY
    authjwt_token_location: set = {"headers", "cookies"}
    authjwt_cookie_csrf_protect: bool = False
    authjwt_cookie_domain: str = COOKIE_DOMAIN
    authjwt_refresh_cookie_path: str = API_PREFIX+"/auth/refresh"
    authjwt_access_token_expires: int = ACCESS_TOKEN_EXPIRE_SECONDS
    authjwt_refresh_token_expires: int = REFRESH_TOKEN_EXPIRE_SECONDS

# [Database]

PG_URI = os.getenv("PG_URI")
PG_BACKUP_USER_PASS = os.getenv("PG_BACKUP_USER_PASS","postgres:")

# [Authentication]

SAML_ACS_URL_ADMIN = API_HOST+API_PREFIX+"/auth/admin/saml/sso/csd"
SAML_ACS_URL_FILER = API_HOST+API_PREFIX+"/auth/filer/saml/sso/csd"
SAML_METADATA_URL_ADMIN = os.getenv("SAML_METADATA_URL_ADMIN")
SAML_METADATA_URL_FILER = os.getenv("SAML_METADATA_URL_FILER")
SAML_ENTITY_ID_ADMIN = API_HOST+API_PREFIX+"/auth/admin/saml/metadata"
SAML_ENTITY_ID_FILER = API_HOST+API_PREFIX+"/auth/filer/saml/metadata"
SAML_SP_METADATA_ADMIN = os.getenv("SAML_SP_METADATA_ADMIN")
SAML_SP_METADATA_FILER = os.getenv("SAML_SP_METADATA_FILER")

# [AWS]
S3_AWS_ACCESS_KEY_ID = os.getenv("S3_AWS_ACCESS_KEY_ID")
S3_AWS_SECRET_ACCESS_KEY = os.getenv("S3_AWS_SECRET_ACCESS_KEY")
S3_AWS_REGION = os.getenv("S3_AWS_REGION")

if EFILE_ENV in ['prod','production']:
    S3_PUBLIC_BUCKET = "efile-sd-public"
    S3_PRIVATE_BUCKET = "efile-sd-private"
else:
    S3_PUBLIC_BUCKET = "efile-sd-public-"+EFILE_ENV
    S3_PRIVATE_BUCKET = "efile-sd-private-"+EFILE_ENV

# [User creds]
HUMAN_READABLE_ID_PREFIX = "CSD"


# [Recaptcha]

RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY")
ENFORCE_RECAPTCHA = True if os.getenv("ENFORCE_RECAPTCHA", "yes") == "yes" else False

# [Sendgrid]

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")


# [Frontend Routes]

FRONTEND_ROUTES = {
    "admin_auth_saml_fail":
    "/auth/admin/login-saml-fail",

    "admin_auth_saml_success":
    "/auth/admin/login-saml-success",

    "filer_auth_saml_fail":
    "/filer/login-saml-fail",

    "filer_dashboard":
    "/filer/profile",

    "admin_dashboard":
    "/admin/dashboard",

    "lobbyist_new_registration_verify_email":
    "/register/lobbyist/register-confirm-email",

    "lobbyist_new_registration_admin_review":
    "/admin/lobbyist/review-new",

    "filer_set_password":
    "/auth/set_password",

    "user_set_password":
    "/auth/set_password",

    "lobbying_entity_profile":
    "/filer/lobbyist/entity"
}

# email
EFILE_EMAIL="efile@pasadev.com"

PASSWORD_RESET_EXPIRE_MINS = 30
NEW_LOBBYIST_EMAIL_VERIFY_EXPIRE_MINS = 24*60
NEW_LOBBYIST_PASSWORD_SET_EXPIRE_MINS = 24*60

EMAIL_TEMPLATES = {
    "lobbyist_new_registration_verify_email":
    "lobbyist_new_registration_verify_email.html",
    "lobbyist_new_admin_notify":
    "lobbyist_new_admin_notify.html",
    "password_set_reset_email":
    "password_set_reset_email.html"
}

# forms

# this is used for new lobbyist messaging
LOBBYIST_FORMS = {
    "firm" : {
        "register": "EC-601",
        "quarterly": "EC-603",
    },
    "org" : {
        "register": "EC-602",
        "quarterly": "EC-604",
    },
    "expenditure": {
        "quarterly": "EC-605",
    },
}

FILING_FORM_NAMES_VERSIONS = {
    "ec601": "ec601_2021.1",
    "ec602": "ec602_2021.1",
    "ec603": "ec603_2021.1",
    "ec604": "ec604_2021.1",
    "ec605": "ec605_2021.1"
}
