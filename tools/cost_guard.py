"""Daily spend cap for query() calls, per TRD §16.

A local JSON ledger is enough at personal scale — no need for a database
just to track a running total against a cap. Used by agent_main.py (the
unified entrypoint), since that's the one most likely to run multi-tool,
multi-turn sessions where cost can add up.
"""

import json
import os
from datetime import date
from pathlib import Path

_LEDGER_PATH = Path(__file__).parent.parent / ".cost_ledger.json"


class BudgetExceededError(RuntimeError):
    """Raised when today's spend has already hit the configured cap."""


def _today_key() -> str:
    return date.today().isoformat()


def _load() -> dict[str, float]:
    if _LEDGER_PATH.exists():
        return json.loads(_LEDGER_PATH.read_text())
    return {}


def _save(ledger: dict[str, float]) -> None:
    _LEDGER_PATH.write_text(json.dumps(ledger, indent=2))


def check_budget() -> None:
    """Raise BudgetExceededError if today's spend already hit the cap."""
    cap = float(os.environ.get("DAILY_SPEND_CAP_USD", "5.00"))
    spent = _load().get(_today_key(), 0.0)
    if spent >= cap:
        raise BudgetExceededError(
            f"Daily spend cap (${cap:.2f}) reached: already spent ${spent:.4f} "
            "today. Raise DAILY_SPEND_CAP_USD in .env, or wait until tomorrow."
        )


def record_spend(cost_usd: float | None) -> None:
    """Add cost_usd (from a ResultMessage.total_cost_usd) to today's running total."""
    if not cost_usd:
        return
    ledger = _load()
    key = _today_key()
    ledger[key] = ledger.get(key, 0.0) + cost_usd
    _save(ledger)
