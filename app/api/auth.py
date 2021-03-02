import traceback
import logging
from fastapi import (
    APIRouter,
    Depends,
    Response,
    Request,
    Form,
)
from starlette.responses import RedirectResponse, PlainTextResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from app.core.config import (
    SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_SECONDS,
    ACCESS_TOKEN_EXPIRE_SECONDS,
    APP_HOST,
    FRONTEND_ROUTES,
    AuthJWTSettings,
    SAML_SP_METADATA_ADMIN,
    SAML_SP_METADATA_FILER,
    ENFORCE_RECAPTCHA
)
from app.db.utils import (
    get_db
)
from app.api.utility.misc import (
    check_recaptcha_response
)
from app.schemas.auth import Login
from app.schemas.user.user import (
    UserResetPassword,
    ResetPasswordRequest
)
from app.models.users import User
from app.api.utility.user import (
    authenticate_admin_user,
    authenticate_filer_user,
    get_active_user,
    get_active_user_from_cookie,
    saml_verify_admin_user,
    user_password_reset_request,
    set_user_password
)
from app.api.utility.exc import (
    Http400,
    Http500,
    handle_exc,
    CREDENTIALS_EXCEPTION,
    AccountException
)
from saml2 import (
    BINDING_HTTP_POST,
    BINDING_HTTP_REDIRECT,
    entity,
)
from app.utils.auth_saml import (
    saml_client
)

router = APIRouter()
user_logger = logging.getLogger("users")
admin_logger = logging.getLogger("admin")
logger = logging.getLogger("general")

# this needs to be in each file
@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()    

@router.get("/me")
async def read_users_me(
    user: User = Depends(get_active_user),
    db_session: Session = Depends(get_db),
):

    try:
        user_dict = jsonable_encoder(user)
        del user_dict['password_hash']

        return {"user": user_dict}

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)


@router.post("/admin-login", operation_id="noauth")
async def admin_login(
    request: Request,
    form: Login,
    Authorize: AuthJWT = Depends(),
    db_session: Session = Depends(get_db)
):
    
    try:
        admin_logger.info(f"Admin login attempt: {form.username}")
        user = authenticate_admin_user(db_session, form.username, form.password)
        if user is None or not user:
            raise CREDENTIALS_EXCEPTION
        access_token = Authorize.create_access_token(
            subject=user.email,
            user_claims={'admin': True}
        )
        refresh_token = Authorize.create_refresh_token(
            subject=user.email, user_claims={'admin': True}
        )
        Authorize.set_refresh_cookies(refresh_token)

        admin_logger.info(f"Admin login succeeded: {form.username}")
        return {"success": True, "access_token": access_token}
        
    except Exception as e:
        admin_logger.info(f"Admin login failed: {form.username}")
        logger.exception(traceback.format_exc())
        handle_exc(e)


@router.post("/filer-login", operation_id="noauth")
async def filer_login(
    request: Request,
    form: Login,
    Authorize: AuthJWT = Depends(),
    db_session: Session = Depends(get_db)
):
    
    try:
        user_logger.info(f"Login attempt: {form.username}")
        user = authenticate_filer_user(db_session, form.username, form.password)
        if user is None or not user:
            raise CREDENTIALS_EXCEPTION
        access_token = Authorize.create_access_token(
            subject=user.email,
            user_claims={'filer': True}
        )
        refresh_token = Authorize.create_refresh_token(
            subject=user.email, user_claims={'filer': True}
        )
        Authorize.set_refresh_cookies(refresh_token)

        user_logger.info(f"Login successful: {form.username}")
        return {"success": True, "access_token": access_token}
        
    except Exception as e:
        user_logger.info(f"Login failed: {form.username}")
        logger.exception(traceback.format_exc())
        handle_exc(e)
        
# "/auth/admin/saml/metadata"
# "/auth/filer/saml/metadata"
# https://efile-test.sandiego.gov/api/v1/auth/admin/saml/metadata

@router.get('/filer/saml/metadata', operation_id="noauth")
async def filer_saml_metadata():
    # the IDP may ask us about our metatadata
    
    try:
        return PlainTextResponse(SAML_SP_METADATA_ADMIN)
        
    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)


@router.get('/admin/saml/metadata', operation_id="noauth")
async def admin_saml_metadata():
    # the IDP may ask us about our metatadata

    try:
        return PlainTextResponse(SAML_SP_METADATA_FILER)
        
    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)

@router.post('/admin/saml/sso/csd', operation_id="noauth")
async def saml_idp_initiated(
    request: Request,
    response: Response,
    Authorize: AuthJWT = Depends(),
    db_session: Session = Depends(get_db)
):

    try:
        res = dict(await request.form())
        saml_c = await saml_client(kind='admin')
        
        authn_response = saml_c.parse_authn_request_response(
            res['SAMLResponse'],
            entity.BINDING_HTTP_POST)
        authn_response.get_identity()
        user_info = authn_response.get_subject()
        username = user_info.text

        admin_logger.info(f"Admin SAML login attempt: {username}")
        user = saml_verify_admin_user(db_session, username)
        if user is None or not user:
            raise Exception("User unknown or not a City user.")

        access_token = Authorize.create_access_token(
            subject=user.email,
            user_claims={'admin': True}
        )
        refresh_token = Authorize.create_refresh_token(
            subject=user.email, user_claims={'admin': True}
        )
        Authorize.set_refresh_cookies(refresh_token)

        response.status_code = 303
        response.headers["location"] = APP_HOST+FRONTEND_ROUTES['admin_auth_saml_success']
        admin_logger.info(f"Admin SAML login succeeded: {username}")
        return response
        
    except Exception as e:
        logger.exception(traceback.format_exc())
        return RedirectResponse(
            url=APP_HOST+FRONTEND_ROUTES['admin_auth_saml_fail'],
            status_code=303,
        )


@router.get('/admin/saml/login/csd')
async def saml_sp_initiated():

    try:
        saml_c = await saml_client(kind='admin')
        reqid, info = saml_c.prepare_for_authenticate()
        redirect_url = None

        redirect_url =  dict(info['headers'])['Location']

        if redirect_url is None:
            Http500(detail="Server error in SAML authentication.")

        return {"success": True, "url": redirect_url}

    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)



@router.get('/refresh', operation_id="noauth")
async def refresh(
    user: User = Depends(get_active_user_from_cookie),
    Authorize: AuthJWT = Depends()
):
    try:
        # set the user group
        if user.account_type == 'admin':
            user_claims = {'admin': True}
            admin_logger.info(f"Admin refresh token: {user.email}")
        elif user.account_type == 'filer':
            user_claims = {'filer': True}
            user_logger.info(f"User refresh token: {user.email}")
        elif user.account_type == 'public':
            user_claims = {'public': True}
            user_logger.info(f"Public refresh token: {user.email}")
        
        access_token = Authorize.create_access_token(subject=user.email,
                                                     user_claims=user_claims)
        refresh_token = Authorize.create_refresh_token(subject=user.email,
                                                       user_claims=user_claims)
        Authorize.set_refresh_cookies(refresh_token)

        return {"success": True, "access_token": access_token}
        
    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)
        

@router.post('/set-password', operation_id="noauth")
async def set_reset_password(
    payload: UserResetPassword,
    db_session: Session = Depends(get_db),
):

    try:
        res = await set_user_password(db_session, payload)

        return {"success": res}
        
    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)

@router.post('/reset-password-request', operation_id="noauth")
async def reset_password_request(
    payload: ResetPasswordRequest,
    db_session: Session = Depends(get_db),
):

    try:
        res = await check_recaptcha_response(payload.recaptcha)

        if ENFORCE_RECAPTCHA and res is False:
           Http400(detail="Recaptcha validation failed.")

        res = await user_password_reset_request(db_session, payload)

        return {"success": True}

    except AccountException:
        raise
           
    except Exception as e:
        logger.exception(traceback.format_exc())
        handle_exc(e)
        
        
@router.get("/logout")
async def log_user_out(
    response: Response,
    Authorize: AuthJWT = Depends()
):

    Authorize.unset_jwt_cookies(response)
    
    return {"success": True, "detail": "user signed out"}

