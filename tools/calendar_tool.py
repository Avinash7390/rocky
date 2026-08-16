"""Google Calendar tools exposed to the orchestrator (README.md's
Integration Layer and Trigger Layer sections).

list_events is auto-approved by the permission gate; create_event is a
write action and blocks on confirmation — see
hooks/permission_gate.py. Also used by the Phase 7 push-webhook
trigger (see the Trigger Layer section's Calendar push webhook
subsection), not built yet.
"""

import asyncio
from typing import Any

from claude_agent_sdk import create_sdk_mcp_server, tool

from . import google_auth


def _list_events_sync(time_min: str, max_results: int) -> list[dict[str, Any]]:
    service = google_auth.get_service("calendar", "v3")
    results = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return [
        {
            "id": e["id"],
            "summary": e.get("summary"),
            "start": e.get("start"),
            "end": e.get("end"),
        }
        for e in results.get("items", [])
    ]


def _create_event_sync(summary: str, start_iso: str, end_iso: str) -> dict[str, Any]:
    service = google_auth.get_service("calendar", "v3")
    event = {
        "summary": summary,
        "start": {"dateTime": start_iso},
        "end": {"dateTime": end_iso},
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    return {"id": created["id"], "htmlLink": created.get("htmlLink")}


@tool(
    "calendar_list_events",
    "List upcoming Calendar events from the primary calendar starting at "
    "time_min (RFC3339, e.g. '2026-08-16T00:00:00Z').",
    {"time_min": str, "max_results": int},
)
async def calendar_list_events(args: dict[str, Any]) -> dict[str, Any]:
    results = await asyncio.to_thread(
        _list_events_sync, args["time_min"], int(args.get("max_results") or 10)
    )
    return {"content": [{"type": "text", "text": str(results)}]}


@tool(
    "calendar_create_event",
    "Create an event on the primary Calendar. start_iso/end_iso are RFC3339 "
    "datetimes, e.g. '2026-08-20T15:00:00-07:00'.",
    {"summary": str, "start_iso": str, "end_iso": str},
)
async def calendar_create_event(args: dict[str, Any]) -> dict[str, Any]:
    result = await asyncio.to_thread(
        _create_event_sync, args["summary"], args["start_iso"], args["end_iso"]
    )
    return {"content": [{"type": "text", "text": f"Created event: {result['htmlLink']}"}]}


calendar_server = create_sdk_mcp_server(
    "calendar", tools=[calendar_list_events, calendar_create_event]
)
