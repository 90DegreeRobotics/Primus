"""
Forever Law — digital episodic spine for NeuroCognica Sleep Architecture v0.1.

Append-only, BLAKE3 hash-chained event log with Chronos-compatible Merkle roots.

This is the Python cognitive-metabolism ledger for CCF. Every wake observation,
sleep boundary, dream candidate, validation decision, and seal is an immutable
event. Semantic memory may change; this log does not.

Storage is JSONL + tip metadata (Windows-portable). Hash and Merkle algorithms
mirror C:\\Chronos\\crates\\chronos_forever_law so seals are auditable the same way.
"""
from __future__ import annotations

import json
import os
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional
from uuid import UUID, uuid4

import blake3


EMPTY_MERKLE_DOMAIN = b"chronos:anchor:empty"


def _canonicalize_json(value: Any) -> Any:
    """Recursively normalize JSON-compatible values for stable hashing."""
    if isinstance(value, dict):
        return {str(k): _canonicalize_json(value[k]) for k in sorted(value.keys(), key=str)}
    if isinstance(value, (list, tuple)):
        return [_canonicalize_json(v) for v in value]
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return _rfc3339(value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            raise ValueError("Forever Law content cannot contain NaN/Inf")
        return value
    if isinstance(value, (str, int, bool)) or value is None:
        return value
    return str(value)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _rfc3339(ts: datetime) -> str:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_rfc3339(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


def blake3_hex(data: bytes) -> str:
    return blake3.blake3(data).hexdigest()


@dataclass
class Event:
    """One sealed, hash-chained Forever Law event."""

    id: str
    timestamp: datetime
    archetype: str
    event_type: str
    content: dict[str, Any]
    parent_hash: Optional[str]
    causation: list[str]
    integrity_hash: str = ""
    layer: int = 0

    def canonical_dict(self) -> dict[str, Any]:
        """Canonical field set used for BLAKE3 sealing (Chronos-compatible)."""
        payload: dict[str, Any] = {
            "id": self.id,
            "timestamp": _rfc3339(self.timestamp),
            "archetype": self.archetype,
            "event_type": self.event_type,
            "content": self.content,
        }
        if self.layer != 0:
            payload["layer"] = self.layer
        payload["parent_hash"] = self.parent_hash
        payload["causation"] = list(self.causation)
        return payload

    def compute_hash(self) -> str:
        # Field order matches Chronos CanonicalEvent. Content must already be
        # canonicalized at append-time (see ForeverLawCodex.append).
        canonical = json.dumps(
            self.canonical_dict(),
            separators=(",", ":"),
            ensure_ascii=False,
            sort_keys=False,
            allow_nan=False,
        )
        return blake3_hex(canonical.encode("utf-8"))

    def seal(self) -> "Event":
        self.integrity_hash = self.compute_hash()
        return self

    def verify_integrity(self) -> bool:
        return bool(self.integrity_hash) and self.compute_hash() == self.integrity_hash

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": _rfc3339(self.timestamp),
            "archetype": self.archetype,
            "event_type": self.event_type,
            "content": self.content,
            "layer": self.layer,
            "parent_hash": self.parent_hash,
            "causation": list(self.causation),
            "integrity_hash": self.integrity_hash,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Event":
        return cls(
            id=str(raw["id"]),
            timestamp=_parse_rfc3339(raw["timestamp"]),
            archetype=str(raw["archetype"]),
            event_type=str(raw["event_type"]),
            content=dict(raw.get("content") or {}),
            layer=int(raw.get("layer") or 0),
            parent_hash=raw.get("parent_hash"),
            causation=[str(x) for x in (raw.get("causation") or [])],
            integrity_hash=str(raw.get("integrity_hash") or ""),
        )


@dataclass
class IntegrityViolation:
    event_id: str
    violation_type: str
    description: str


@dataclass
class IntegrityReport:
    valid: bool
    total_events: int
    corrupted_count: int
    broken_links: int
    violations: list[IntegrityViolation] = field(default_factory=list)
    merkle_root: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "total_events": self.total_events,
            "corrupted_count": self.corrupted_count,
            "broken_links": self.broken_links,
            "merkle_root": self.merkle_root,
            "violations": [
                {
                    "event_id": v.event_id,
                    "violation_type": v.violation_type,
                    "description": v.description,
                }
                for v in self.violations
            ],
        }


@dataclass(frozen=True)
class ChainAnchor:
    window_start: str
    window_end: str
    event_count: int
    merkle_root: str
    latest_event_id: Optional[str]
    latest_event_hash: Optional[str]
    boundary: str  # "T0" | "T1" | "manual"

    def to_dict(self) -> dict[str, Any]:
        return {
            "window_start": self.window_start,
            "window_end": self.window_end,
            "event_count": self.event_count,
            "merkle_root": self.merkle_root,
            "latest_event_id": self.latest_event_id,
            "latest_event_hash": self.latest_event_hash,
            "boundary": self.boundary,
        }


@dataclass(frozen=True)
class AppendOutcome:
    event_id: str
    integrity_hash: str
    parent_hash: Optional[str]
    event_type: str


def compute_merkle_root(events: Iterable[Event]) -> str:
    """BLAKE3 Merkle root over integrity hashes — matches Chronos anchors.rs."""
    level = [
        blake3.blake3(event.integrity_hash.encode("utf-8")).digest()
        for event in events
    ]
    if not level:
        return blake3_hex(EMPTY_MERKLE_DOMAIN)

    while len(level) > 1:
        next_level: list[bytes] = []
        i = 0
        while i < len(level):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else level[i]
            next_level.append(blake3.blake3(left + right).digest())
            i += 2
        level = next_level
    return level[0].hex()


class ForeverLawCodex:
    """
    Append-only sealed cognition ledger.

    Thread-safe for single-process use. Events are never rewritten in place.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.events_path = self.root / "events.jsonl"
        self.meta_path = self.root / "meta.json"
        self.anchors_path = self.root / "anchors.jsonl"
        self._lock = threading.RLock()
        self._events: list[Event] = []
        self._tip_hash: Optional[str] = None
        self._load()

    def _load(self) -> None:
        if self.events_path.exists():
            with self.events_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    event = Event.from_dict(json.loads(line))
                    self._events.append(event)
                    self._tip_hash = event.integrity_hash
        if self.meta_path.exists():
            meta = json.loads(self.meta_path.read_text(encoding="utf-8"))
            tip = meta.get("tip_hash")
            if tip and tip != self._tip_hash and self._events:
                # Tip metadata is advisory; chain tip from events wins.
                pass

    def _persist_meta(self) -> None:
        payload = {
            "tip_hash": self._tip_hash,
            "event_count": len(self._events),
            "updated_at": _rfc3339(utc_now()),
        }
        tmp = self.meta_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        os.replace(tmp, self.meta_path)

    def append(
        self,
        archetype: str,
        event_type: str,
        content: dict[str, Any],
        causation: Optional[list[str]] = None,
        layer: int = 0,
        event_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
    ) -> AppendOutcome:
        with self._lock:
            # Canonicalize before seal so stored bytes == hashed bytes forever.
            content = _canonicalize_json(dict(content))
            event = Event(
                id=event_id or str(uuid4()),
                timestamp=timestamp or utc_now(),
                archetype=archetype,
                event_type=event_type,
                content=content,
                parent_hash=self._tip_hash,
                causation=list(causation or []),
                layer=layer,
            ).seal()

            if not event.verify_integrity():
                raise RuntimeError("Failed to seal Forever Law event")

            with self.events_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event.to_dict(), ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())

            self._events.append(event)
            self._tip_hash = event.integrity_hash
            self._persist_meta()
            return AppendOutcome(
                event_id=event.id,
                integrity_hash=event.integrity_hash,
                parent_hash=event.parent_hash,
                event_type=event.event_type,
            )

    @property
    def tip_hash(self) -> Optional[str]:
        return self._tip_hash

    def __len__(self) -> int:
        return len(self._events)

    def events(self) -> list[Event]:
        return list(self._events)

    def events_since(self, start_exclusive_id: Optional[str] = None) -> list[Event]:
        if not start_exclusive_id:
            return self.events()
        out: list[Event] = []
        seen = False
        for event in self._events:
            if seen:
                out.append(event)
            if event.id == start_exclusive_id:
                seen = True
        return out

    def get(self, event_id: str) -> Optional[Event]:
        for event in self._events:
            if event.id == event_id:
                return event
        return None

    def verify_full_chain(self) -> IntegrityReport:
        violations: list[IntegrityViolation] = []
        corrupted = 0
        broken = 0
        prev_hash: Optional[str] = None

        for index, event in enumerate(self._events):
            if not event.verify_integrity():
                corrupted += 1
                violations.append(
                    IntegrityViolation(
                        event_id=event.id,
                        violation_type="HashMismatch",
                        description="Stored integrity_hash does not match recomputation",
                    )
                )
            if index == 0:
                if event.parent_hash is not None:
                    broken += 1
                    violations.append(
                        IntegrityViolation(
                            event_id=event.id,
                            violation_type="InvalidGenesis",
                            description="Genesis event unexpectedly has parent_hash",
                        )
                    )
            else:
                if event.parent_hash is None:
                    broken += 1
                    violations.append(
                        IntegrityViolation(
                            event_id=event.id,
                            violation_type="MissingParent",
                            description="Non-genesis event missing parent_hash",
                        )
                    )
                elif event.parent_hash != prev_hash:
                    broken += 1
                    violations.append(
                        IntegrityViolation(
                            event_id=event.id,
                            violation_type="BrokenChain",
                            description="parent_hash does not match predecessor integrity_hash",
                        )
                    )
            prev_hash = event.integrity_hash

        root = compute_merkle_root(self._events)
        valid = corrupted == 0 and broken == 0
        return IntegrityReport(
            valid=valid,
            total_events=len(self._events),
            corrupted_count=corrupted,
            broken_links=broken,
            violations=violations,
            merkle_root=root,
        )

    def seal_boundary(
        self,
        boundary: str,
        archetype: str = "sleep_architecture",
        extra: Optional[dict[str, Any]] = None,
    ) -> ChainAnchor:
        """
        Seal the current chain state as a sleep-boundary anchor (T0 / T1).

        Emits a chain_anchor event and appends an external receipt line.
        """
        with self._lock:
            events = list(self._events)
            if events:
                window_start = _rfc3339(events[0].timestamp)
                window_end = _rfc3339(events[-1].timestamp)
                latest_id = events[-1].id
                latest_hash = events[-1].integrity_hash
            else:
                now = _rfc3339(utc_now())
                window_start = now
                window_end = now
                latest_id = None
                latest_hash = None

            merkle_root = compute_merkle_root(events)
            anchor = ChainAnchor(
                window_start=window_start,
                window_end=window_end,
                event_count=len(events),
                merkle_root=merkle_root,
                latest_event_id=latest_id,
                latest_event_hash=latest_hash,
                boundary=boundary,
            )
            content = anchor.to_dict()
            if extra:
                content["extra"] = extra

            outcome = self.append(
                archetype=archetype,
                event_type="chain_anchor",
                content=content,
                layer=0,
            )
            receipt = {
                "anchor_event_id": outcome.event_id,
                "anchor_event_hash": outcome.integrity_hash,
                **anchor.to_dict(),
            }
            with self.anchors_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(receipt, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            return anchor
