import json
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import HTMLResponse, RedirectResponse
from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config
from yamlns import namespace as ns
from . import persons


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
    print(request)
    print(ns(user).dump())
    request.session['user'] = dict(user)
    return HTMLResponse(
        """"<html><script>
        localStorage.setItem("token", "dedanone");
        location.href="/";
        </script></html>
        """)

@router.get('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def validatedUser(token: str = Depends(oauth2_scheme)):
    print(f"Received token {token}")
    if token!='dedanone':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return "david"


