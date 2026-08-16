"""Spotify OAuth2 (Authorization Code) helper, per TRD §11.

Read-only use case (currently-playing, recently-played, playlists) — no
write scopes requested. First call opens a browser for consent and caches
the token to .spotify_token.json (gitignored); later calls reuse and
refresh it silently via spotipy's own cache handler.
"""

import os
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth

SCOPES = "user-read-currently-playing user-read-recently-played playlist-read-private"

_CACHE_PATH = Path(__file__).parent.parent / ".spotify_token.json"


class SpotifyConfigError(RuntimeError):
    """Raised when the OAuth client credentials are missing."""


def get_client() -> spotipy.Spotify:
    client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.environ.get("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8080/callback")
    if not client_id or not client_secret:
        raise SpotifyConfigError(
            "Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env — create "
            "an app at https://developer.spotify.com/dashboard and add "
            f"{redirect_uri} as a redirect URI. See "
            "tasks/06-remaining-integrations.md."
        )
    auth_manager = SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=SCOPES,
        cache_path=str(_CACHE_PATH),
        open_browser=True,
    )
    return spotipy.Spotify(auth_manager=auth_manager)
