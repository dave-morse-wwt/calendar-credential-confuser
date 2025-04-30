import sys
from typing import Annotated, Union

import google.oauth2.credentials
import google_auth_oauthlib.flow
from db import init_db
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from google_oauth import load_google_oauth_config
from models.user import UserPydantic, UserPydanticInFakeDB


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "granted_scopes": credentials.granted_scopes,
    }


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserPydanticInFakeDB(**user_dict)


def fake_hash_password(password: str):
    return "fakehashed" + password


app = FastAPI()
init_db(app)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)  # ha ha its just username
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UserPydanticInFakeDB:
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Annotated[UserPydantic, Depends(get_current_user)],
) -> UserPydanticInFakeDB:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

globo_state_secret = None


@app.get("/")
def root():
    global globo_state_secret
    config = load_google_oauth_config().model_dump(mode="json")
    print(f"Config: {config!r}")
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        config, scopes=["https://www.googleapis.com/auth/calendar.readonly"]
    )
    flow.redirect_uri = "http://localhost:8000/oauth2callback"
    auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
    globo_state_secret = state
    return {"authUrl": auth_url}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/items")
def read_items(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"token": token}


@app.get("/users/me")
async def read_users_me(
    current_user: Annotated[UserPydanticInFakeDB, Depends(get_current_active_user)],
):
    return current_user


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # see also OAuth2PasswordRequestFormStrict
    # via https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#oauth2passwordrequestform
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserPydanticInFakeDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {
        "access_token": user.username,
        "token_type": "bearer",
    }  # ha ha our access token is the username


@app.get("/oauth2callback")
def oauth2callback(req: Request):
    global globo_state_secret
    state = globo_state_secret
    if not state:
        return {"error": "State is not set. Please authorize first."}

    config = load_google_oauth_config().model_dump(mode="json")
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        config, scopes=["https://www.googleapis.com/auth/calendar.readonly"]
    )
    flow.redirect_uri = "http://localhost:8000/oauth2callback"

    auth_respone_url = str(req.url)
    flow.fetch_token(authorization_response=auth_respone_url)
    credentials = credentials_to_dict(flow.credentials)
    print(f"CREDENTIALS: {credentials}")
    return {"great": "job", "credentials": credentials}


@app.on_event("startup")
async def startup_event():
    config = load_google_oauth_config()
