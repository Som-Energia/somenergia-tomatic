import json
import datetime
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from yamlns import namespace as ns
from consolemsg import error
from . import persons
import dbconfig


config = Config('config.fastapi')
print(config.file_values)

oauth = OAuth(config)


CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
oauth.register(
    name='google',
    server_metadata_url=CONF_URL,
    client_kwargs={
        'scope': 'openid email profile'
    }
)

router = APIRouter()

@router.get('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    print(redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get('/auth')
async def auth(request: Request):
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as error:
        return HTMLResponse(f'<h1>{error.error}</h1>', 400)
    user = await oauth.google.parse_id_token(request, token)
    if not user:
        return HTMLResponse(f'<h1>Missing user</h1>', 400)

    username = persons.byEmail(user['email'])
    if not username:
        return HTMLResponse(f'<h1>Not authorized</h1>', 400)
    user.update(username = username)
    token = create_access_token(user)
    return HTMLResponse(
        f""""<html><script>
        localStorage.setItem("token", "{token}");
        location.href="/";
        </script></html>
        """)

@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

from jose import JWTError, jwt
JWT_ALGORITHM='HS256'
def create_access_token(data: dict):
    passthru_fields = (
        'username name email locale family_name given_name picture'
    ).split()
    payload = dict(
        (field, data[field])
        for field in passthru_fields
        if field in data
    )
    expires_delta = datetime.timedelta(
        **dbconfig.tomatic.get('jwt',{}).get('expiration', dict(hours=10))
    )
    utcnow = datetime.datetime.now(datetime.timezone.utc)
    expiration = utcnow + expires_delta
    payload['exp'] = int(expiration.timestamp())
    token = jwt.encode(
        payload,
        dbconfig.tomatic.jwt.secret_key,
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
    try:
        utcnow = datetime.datetime.now(datetime.timezone.utc)
        payload = jwt.decode(
            token,
            dbconfig.tomatic.jwt.secret_key,
            algorithms=JWT_ALGORITHM,
        )
    except JWTError as e:
        raise auth_error(f"Token decoding failed: {e}")

    # TODO: validate all the fields
    username: str = payload.get("username")
    if username is None:
        raise auth_error("Payload failed")

    return ns(payload)


