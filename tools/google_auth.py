"""Shared Google OAuth2 helper for Gmail, Drive, Calendar, and YouTube.

Desktop-app OAuth flow (TRD §11): the first run opens a browser for consent
and caches the resulting token to .google_token.json (gitignored); later
runs reuse the cached token and refresh it silently. One client + one
cached token covers every scope below — Google's consent screen grants a
superset of scopes in a single flow, so there's no need for four separate
logins.
"""

import json
import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/youtube.readonly",
]

_TOKEN_PATH = Path(__file__).parent.parent / ".google_token.json"


class GoogleConfigError(RuntimeError):
    """Raised when the OAuth client credentials are missing."""


def _client_config() -> dict:
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = os.environ.get("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise GoogleConfigError(
            "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env — create "
            "a Desktop app OAuth client at "
            "https://console.cloud.google.com/apis/credentials and enable "
            "the Gmail, Drive, Calendar, and YouTube Data APIs on that "
            "project. See tasks/06-remaining-integrations.md."
        )
    return {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost"],
        }
    }


def get_credentials() -> Credentials:
    """Load cached credentials, refreshing or running the consent flow as needed."""
    creds: Credentials | None = None
    if _TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_info(
            json.loads(_TOKEN_PATH.read_text()), SCOPES
        )

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_config(_client_config(), SCOPES)
        creds = flow.run_local_server(port=0)

    _TOKEN_PATH.write_text(creds.to_json())
    return creds


def get_service(api_name: str, api_version: str) -> Resource:
    return build(api_name, api_version, credentials=get_credentials())
