import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Annotated, Union

import google.oauth2.credentials
import google_auth_oauthlib.flow
import jwt
import pydantic
from db import init_db
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from google_oauth import load_google_oauth_config
from models.user import UserPydantic, UserPydanticInFakeDB
from passlib.context import CryptContext

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


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
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}


class Token(pydantic.BaseModel):
    access_token: str
    token_type: str


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    print(f"{encoded_jwt=}")
    return encoded_jwt


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserPydanticInFakeDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


# def fake_hash_password(password: str):
#     return "fakehashed" + password


app = FastAPI()
init_db(app)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    print("get_current_user here")
    print(f"{token=} {JWT_SECRET_KEY=} {ALGORITHM=} hash={'fakehash'}")

    def credentials_exception(s: str):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {s}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        print(f"{token=} {JWT_SECRET_KEY=} {ALGORITHM=}")
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        print(f"{payload=}")
        username = payload.get("sub")
        if username is None:
            raise credentials_exception("No sub in payload")
    except jwt.InvalidTokenError:
        raise credentials_exception("Invalid token")
    user = get_user(fake_users_db, username=username)
    if user is None:
        raise credentials_exception("get_user failed")
    return user


async def get_current_active_user(
    current_user: Annotated[UserPydantic, Depends(get_current_user)],
) -> UserPydanticInFakeDB:
    print("get_current_active_user here")
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
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    # see also OAuth2PasswordRequestFormStrict
    # via https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#oauth2passwordrequestform
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    # user_dict = fake_users_db.get(form_data.username)
    # if not user_dict:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    # user = UserPydanticInFakeDB(**user_dict)
    # hashed_password = fake_hash_password(form_data.password)
    # if not hashed_password == user.hashed_password:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    return Token(
        access_token=access_token,
        token_type="bearer",
    )


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
