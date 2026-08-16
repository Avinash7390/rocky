"""Spotify tools exposed to the orchestrator, per TRD §11.

All read-only (currently-playing, recently-played, playlists) — no write
path, so nothing here needs a permission-gate "write" entry. spotipy is
synchronous, so each call runs in a thread rather than blocking the event
loop.
"""

import asyncio
from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

from . import spotify_client


def _currently_playing_sync() -> dict[str, Any] | None:
    client = spotify_client.get_client()
    playback = client.current_playback()
    if not playback or not playback.get("item"):
        return None
    item = playback["item"]
    return {
        "track": item.get("name"),
        "artists": [a["name"] for a in item.get("artists", [])],
        "is_playing": playback.get("is_playing"),
        "progress_ms": playback.get("progress_ms"),
    }


def _recently_played_sync(limit: int) -> list[dict[str, Any]]:
    client = spotify_client.get_client()
    results = client.current_user_recently_played(limit=limit)
    return [
        {
            "track": item["track"]["name"],
            "artists": [a["name"] for a in item["track"]["artists"]],
            "played_at": item["played_at"],
        }
        for item in results.get("items", [])
    ]


def _playlists_sync(limit: int) -> list[dict[str, Any]]:
    client = spotify_client.get_client()
    results = client.current_user_playlists(limit=limit)
    return [
        {"id": p["id"], "name": p["name"], "tracks": p["tracks"]["total"]}
        for p in results.get("items", [])
    ]


@tool(
    "spotify_currently_playing",
    "Get the track currently playing on Spotify, if any.",
    {},
)
async def spotify_currently_playing(args: dict[str, Any]) -> dict[str, Any]:
    result = await asyncio.to_thread(_currently_playing_sync)
    text = str(result) if result else "Nothing is currently playing."
    return {"content": [{"type": "text", "text": text}]}


@tool(
    "spotify_recently_played",
    "List recently played tracks (Spotify only exposes the last 50).",
    {"limit": int},
)
async def spotify_recently_played(args: dict[str, Any]) -> dict[str, Any]:
    results = await asyncio.to_thread(_recently_played_sync, int(args.get("limit") or 20))
    return {"content": [{"type": "text", "text": str(results)}]}


@tool(
    "spotify_playlists",
    "List the authenticated user's playlists.",
    {"limit": int},
)
async def spotify_playlists(args: dict[str, Any]) -> dict[str, Any]:
    results = await asyncio.to_thread(_playlists_sync, int(args.get("limit") or 20))
    return {"content": [{"type": "text", "text": str(results)}]}


spotify_server = create_sdk_mcp_server(
    "spotify",
    tools=[spotify_currently_playing, spotify_recently_played, spotify_playlists],
)
