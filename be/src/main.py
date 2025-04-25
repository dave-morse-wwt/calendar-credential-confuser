from typing import Union

import google.oauth2.credentials
import google_auth_oauthlib.flow
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from google_oauth import load_google_oauth_config


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "granted_scopes": credentials.granted_scopes,
    }


app = FastAPI()


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
