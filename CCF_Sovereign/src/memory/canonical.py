"""
Canonical semantic memory — mutable, validated beliefs promoted from sleep.

Forever Law keeps immutable episodic truth.
CanonicalMemory keeps what the system currently believes after validation.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class CanonicalBelief:
    belief_id: str
    text: str
    token_ids: list[int]
    confidence: float
    status: str  # "promoted" | "uncertain"
    source_event_ids: list[str]
    dream_event_id: Optional[str]
    created_at: str
    evidence: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "belief_id": self.belief_id,
            "text": self.text,
            "token_ids": list(self.token_ids),
            "confidence": self.confidence,
            "status": self.status,
            "source_event_ids": list(self.source_event_ids),
            "dream_event_id": self.dream_event_id,
            "created_at": self.created_at,
            "evidence": dict(self.evidence),
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "CanonicalBelief":
        return cls(
            belief_id=str(raw["belief_id"]),
            text=str(raw.get("text") or ""),
            token_ids=[int(x) for x in (raw.get("token_ids") or [])],
            confidence=float(raw.get("confidence") or 0.0),
            status=str(raw.get("status") or "uncertain"),
            source_event_ids=[str(x) for x in (raw.get("source_event_ids") or [])],
            dream_event_id=raw.get("dream_event_id"),
            created_at=str(raw.get("created_at") or _utc_now()),
            evidence=dict(raw.get("evidence") or {}),
        )


class CanonicalMemory:
    """Disk-backed mutable belief store with explicit promotion statuses."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "canonical_beliefs.json"
        self._beliefs: dict[str, CanonicalBelief] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        for item in raw.get("beliefs", []):
            belief = CanonicalBelief.from_dict(item)
            self._beliefs[belief.belief_id] = belief

    def _save(self) -> None:
        payload = {
            "updated_at": _utc_now(),
            "beliefs": [b.to_dict() for b in self._beliefs.values()],
        }
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.path)

    def upsert(self, belief: CanonicalBelief) -> CanonicalBelief:
        self._beliefs[belief.belief_id] = belief
        self._save()
        return belief

    def promote(
        self,
        text: str,
        token_ids: list[int],
        confidence: float,
        source_event_ids: list[str],
        dream_event_id: Optional[str],
        evidence: Optional[dict[str, Any]] = None,
        status: str = "promoted",
    ) -> CanonicalBelief:
        belief = CanonicalBelief(
            belief_id=str(uuid4()),
            text=text,
            token_ids=list(token_ids),
            confidence=float(confidence),
            status=status,
            source_event_ids=list(source_event_ids),
            dream_event_id=dream_event_id,
            created_at=_utc_now(),
            evidence=dict(evidence or {}),
        )
        return self.upsert(belief)

    def all(self) -> list[CanonicalBelief]:
        return list(self._beliefs.values())

    def promoted(self) -> list[CanonicalBelief]:
        return [b for b in self._beliefs.values() if b.status == "promoted"]

    def __len__(self) -> int:
        return len(self._beliefs)
