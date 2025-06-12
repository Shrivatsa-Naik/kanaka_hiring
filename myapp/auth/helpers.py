import msal
import uuid
from flask import current_app, session, url_for

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get('token_cache'):
        cache.deserialize(session['token_cache'])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()

def build_msal_app(cache=None):
    return msal.ConfidentialClientApplication(
        current_app.config['MS_CLIENT_ID'],
        authority=current_app.config['MS_AUTHORITY'],
        client_credential=current_app.config['MS_CLIENT_SECRET'],
        token_cache=cache
    )                             

def get_msal_auth_url(scopes):
    cache = _load_cache()
    msal_app = build_msal_app(cache)
    auth_url = msal_app.get_authorization_request_url(
        scopes,
        state=str(uuid.uuid4()),
        redirect_uri=url_for('auth.authorized_redirect', _external=True)
    )
    
    _save_cache(cache)
    return auth_url

def get_token_from_code(code, scopes):
    cache = _load_cache()
    msal_app = build_msal_app(cache)
    result = msal_app.acquire_token_by_authorization_code(
        code,
        scopes=scopes,
        redirect_uri=url_for("auth.authorized_redirect", _external=True)
    )
    _save_cache(cache)
    return result