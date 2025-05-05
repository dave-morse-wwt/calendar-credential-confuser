import os
import re
from datetime import datetime, timedelta, timezone
from typing import Annotated, Union

import google_auth_oauthlib.flow
import jwt
import pydantic
from ccc_logger import logger
from db import init_db
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from google_oauth import load_google_oauth_config
from models.user import User, UserPydantic, UserPydanticInFakeDB
from passlib.context import CryptContext
from starlette.middleware.sessions import SessionMiddleware
from tortoise.exceptions import IntegrityError

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
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)


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


app = FastAPI()
init_db(app)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app.add_middleware(SessionMiddleware, secret_key=os.environ["COOKIE_SECRET_KEY"])


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    def credentials_error(log: str):
        logger.error(log)
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_error("No sub in payload")
    except jwt.InvalidTokenError:
        raise credentials_error("Invalid token")
    user = get_user(fake_users_db, username=username)
    if user is None:
        raise credentials_error(f"get_user({username!r}) returned None")
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


# google
@app.get("/start-auth")
def start_auth(request: Request):
    config = load_google_oauth_config().model_dump(mode="json")
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        config, scopes=["https://www.googleapis.com/auth/calendar.readonly"]
    )
    flow.redirect_uri = "http://localhost:8000/oauth2callback"
    auth_url, state = flow.authorization_url(access_type="offline", prompt="consent")
    request.session["state"] = state
    logger.info("Redirecting user to google - good luck, buddy!")
    return RedirectResponse(auth_url)


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


# our jwt
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
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
    )


# google
@app.get("/oauth2callback")
def oauth2callback(request: Request):
    state_via_session = request.session.get("state")
    if not state_via_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing state parameter",
        )
    state_via_param = request.query_params.get("state")
    if state_via_session != state_via_param:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mismatched state parameter",
        )
    config = load_google_oauth_config().model_dump(mode="json")
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        config,
        scopes=["https://www.googleapis.com/auth/calendar.readonly"],
        state=state_via_session,
    )
    flow.redirect_uri = "http://localhost:8000/oauth2callback"

    auth_response_url = str(request.url)
    flow.fetch_token(authorization_response=auth_response_url)
    credentials = credentials_to_dict(flow.credentials)
    return {"great": "job", "credentials": credentials}


@app.on_event("startup")
async def startup_event():
    config = load_google_oauth_config()


PASSWORD_REGEX = re.compile(
    r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*(?:[!-/]|[:-@]|[\[-~])).{8,128}$"
)


class CreateUser(pydantic.BaseModel):
    name: Annotated[
        str,
        pydantic.Field(
            min_length=2,
            max_length=50,
            strip_whitespace=True,
            description="User's full name, as it will appear to other users",
            examples=["Jane Doe"],
        ),
    ]
    email: pydantic.EmailStr
    password: Annotated[
        str,
        pydantic.Field(
            min_length=8,
            max_length=128,
            description="Password must include uppercase, lowercase, number, and special character",
            examples=["StrongPass123!"],
        ),
    ]

    @pydantic.field_validator("password")
    @classmethod
    def strong_password(cls, v):
        if not PASSWORD_REGEX.match(v):
            raise ValueError(
                "Password must contain at least one uppercase letter, one lowercase letter, "
                "one number, and one special character."
            )
        return v


@app.post("/signup")
async def signup(
    create_user: CreateUser,
):
    try:
        user = await User.create(
            name=create_user.name,
            email=create_user.email,
            hashed_password=get_password_hash(create_user.password),
        )
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="Email already in use")

    return {"id": user.id, "name": user.name, "email": user.email}
