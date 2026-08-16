"""YouTube tool exposed to the orchestrator (README.md's YouTube integration
deep dive subsection).

Read-only (`youtube.readonly` scope): subscriptions, playlists, and the
Liked Videos playlist. No watch history — there's no API or OAuth scope
for it, a platform limitation since ~2016, not something this build can
close (see task doc). No write path, so nothing here needs a
permission-gate "write" entry.
"""

import asyncio
from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

from . import google_auth


def _list_subscriptions_sync(max_results: int) -> list[dict[str, Any]]:
    service = google_auth.get_service("youtube", "v3")
    results = (
        service.subscriptions()
        .list(part="snippet", mine=True, maxResults=max_results)
        .execute()
    )
    return [
        {"channel": item["snippet"]["title"], "channelId": item["snippet"]["resourceId"]["channelId"]}
        for item in results.get("items", [])
    ]


def _list_playlists_sync(max_results: int) -> list[dict[str, Any]]:
    service = google_auth.get_service("youtube", "v3")
    results = (
        service.playlists()
        .list(part="snippet,contentDetails", mine=True, maxResults=max_results)
        .execute()
    )
    return [
        {
            "id": item["id"],
            "title": item["snippet"]["title"],
            "item_count": item["contentDetails"]["itemCount"],
        }
        for item in results.get("items", [])
    ]


def _liked_videos_sync(max_results: int) -> list[dict[str, Any]]:
    service = google_auth.get_service("youtube", "v3")
    results = (
        service.videos()
        .list(part="snippet", myRating="like", maxResults=max_results)
        .execute()
    )
    return [
        {"id": item["id"], "title": item["snippet"]["title"], "channel": item["snippet"]["channelTitle"]}
        for item in results.get("items", [])
    ]


@tool(
    "youtube_list_subscriptions",
    "List the authenticated user's YouTube channel subscriptions.",
    {"max_results": int},
)
async def youtube_list_subscriptions(args: dict[str, Any]) -> dict[str, Any]:
    results = await asyncio.to_thread(_list_subscriptions_sync, int(args.get("max_results") or 25))
    return {"content": [{"type": "text", "text": str(results)}]}


@tool(
    "youtube_list_playlists",
    "List the authenticated user's YouTube playlists.",
    {"max_results": int},
)
async def youtube_list_playlists(args: dict[str, Any]) -> dict[str, Any]:
    results = await asyncio.to_thread(_list_playlists_sync, int(args.get("max_results") or 25))
    return {"content": [{"type": "text", "text": str(results)}]}


@tool(
    "youtube_liked_videos",
    "List the authenticated user's liked YouTube videos.",
    {"max_results": int},
)
async def youtube_liked_videos(args: dict[str, Any]) -> dict[str, Any]:
    results = await asyncio.to_thread(_liked_videos_sync, int(args.get("max_results") or 25))
    return {"content": [{"type": "text", "text": str(results)}]}


youtube_server = create_sdk_mcp_server(
    "youtube",
    tools=[youtube_list_subscriptions, youtube_list_playlists, youtube_liked_videos],
)
