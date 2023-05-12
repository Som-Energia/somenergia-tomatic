import json
import datetime
from functools import lru_cache
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth, OAuthError
from jose import JWTError, jwt
from yamlns import namespace as ns
from consolemsg import error
from . import persons
import os
JWT_ALGORITHM='HS256'
CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'

def config(key='', default=Ellipsis):
    keyparts = key.split('.')
    envkey = key.replace('.','_').upper()
    if envkey in os.environ:
        return os.environ[envkey]
    try:
        import dbconfig as configuration
        configuration = ns(configuration.__dict__)
    except ImportError:
        configuration = ns(tomatic=ns())
    if not key:
        return configuration
    for part in keyparts[:-1]:
        configuration = configuration.get(part, ns())
    if default is Ellipsis and keyparts[-1] not in configuration:
        raise KeyError(key)
    return configuration.get(keyparts[-1], default)

@lru_cache
def oauth():
    oauth = OAuth()
    oauth.register(
        name='google',
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        },
        **config('tomatic.oauth')
    )
    return oauth

router = APIRouter()

@router.get('/login')
async def login(request: Request):
    redirect_uri = str(request.url_for('auth'))
    if 'localhost' not in redirect_uri:
        redirect_uri = redirect_uri.replace('http:', 'https:')
    print("Auth redirect uri:", redirect_uri)
    return await oauth().google.authorize_redirect(request, redirect_uri)

def auth_result(token=None, error=None, code=200):
    return HTMLResponse(
        f""""<html><script>
        localStorage.setItem("token", "{token if token else ''}");
        localStorage.setItem("autherror", "{error if error else ''}");
        location.href="/";
        </script><h1>{error if error else ''}</h1></html>
        """, code)

@router.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth().google.authorize_access_token(request)
    except OAuthError as error:
        return auth_result(error=f"Error d'autenticació: {error.error}", code=400)
    user = await oauth().google.parse_id_token(request, token)
    if not user:
        return auth_result(error='Error a la resposta de Google', code=400)

    username = persons.byEmail(user['email'])
    if not username:
        return auth_result(error=f"L'usuari {user['email']} no té accés a l'aplicació", code=400)

    user.update(username = username)
    token = create_access_token(user)
    return auth_result(token=token)

def expiration_timestamp(expiration_delta=None):
    expires_delta = expiration_delta or datetime.timedelta(
        **config('tomatic.jwt.expiration', dict(hours=10))
    )
    utcnow = datetime.datetime.now(datetime.timezone.utc)
    expiration = utcnow + expires_delta
    return int(expiration.timestamp())

@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

def create_access_token(data: dict, expiration_delta: datetime.timedelta = None):
    passthru_fields = (
        'username name email locale family_name given_name picture'
    ).split()
    payload = dict(
        (field, data[field])
        for field in passthru_fields
        if field in data
    )
    payload['exp'] = expiration_timestamp(expiration_delta)
    token = jwt.encode(
        payload,
        config('tomatic.jwt.secret_key'),
        algorithm=JWT_ALGORITHM,
    )
    return token

def auth_error(message):
    error(message)
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def validatedUser(token: str = Depends(oauth2_scheme)):
    environ_user = config('tomatic.auth.dummy', None)
    if environ_user:
        if environ_user.isalpha():
            return dict(
                username = environ_user,
                email = environ_user+'@somenergia.coop',
                exp = expiration_timestamp(),
            )
        return dict(
            username = 'alice',
            email = 'me@here.coop',
            exp = expiration_timestamp(),
        )
    try:
        utcnow = datetime.datetime.now(datetime.timezone.utc)
        payload = jwt.decode(
            token,
            config('tomatic.jwt.secret_key'),
            algorithms=JWT_ALGORITHM,
        )
    except JWTError as e:
        raise auth_error(f"Token decoding failed: {e}")

    # TODO: validate all the fields
    username: str = payload.get("username")
    if username is None:
        raise auth_error("Payload failed")

    return ns(payload)


