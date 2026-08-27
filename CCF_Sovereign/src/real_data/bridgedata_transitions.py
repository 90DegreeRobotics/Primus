"""Fail-closed extraction of observed one-step BridgeData state transitions.

This module treats the local BridgeData V2 LeRobot intake as immutable evidence.
It accepts neither random-frame sampling nor unbounded materialization of the
acquired shard.  A caller must select complete episode identifiers before
extracting the action-conditioned records used by a later experiment.

The output is observational data only.  It is not a policy, a control system,
a robot-safety result, a renderer, or a promotion mechanism.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


BRIDGEDATA_TRANSITION_VERSION = 1
INTAKE_SCHEMA_VERSION = "bridgedata-intake-v1"
STATE_DIMENSIONS = 7
REQUIRED_DATA_COLUMNS = (
    "observation.state",
    "action",
    "timestamp",
    "frame_index",
    "episode_index",
    "index",
    "task_index",
)
REQUIRED_EPISODE_COLUMNS = (
    "episode_index",
    "tasks",
    "length",
    "data/chunk_index",
    "data/file_index",
    "dataset_from_index",
    "dataset_to_index",
)
REQUIRED_TASK_COLUMNS = ("task", "task_index")
REQUIRED_INTAKE_FILES = (
    "meta_info.json",
    "meta_stats.json",
    "meta_tasks.parquet",
    "meta_episodes_chunk-000_file-000.parquet",
    "data_chunk-000_file-000.parquet",
)


class BridgeDataError(ValueError):
    """Raised when a frozen BridgeData input or derived record is invalid."""


def sha256_file(path: Path) -> str:
    """Return a streamed SHA-256 digest for a local immutable input."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def _require_mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise BridgeDataError(f"{label} must be an object")
    return value


def _require_int(value: Any, label: str) -> int:
    if isinstance(value, bool):
        raise BridgeDataError(f"{label} must be an integer")
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise BridgeDataError(f"{label} must be an integer") from error
    if result != value:
        raise BridgeDataError(f"{label} must be an integer")
    return result


def _finite_vector(value: Any, label: str) -> tuple[float, ...]:
    if not isinstance(value, (list, tuple)) or len(value) != STATE_DIMENSIONS:
        raise BridgeDataError(f"{label} must contain exactly {STATE_DIMENSIONS} values")
    try:
        vector = tuple(float(item) for item in value)
    except (TypeError, ValueError) as error:
        raise BridgeDataError(f"{label} must contain numeric values") from error
    if not all(math.isfinite(item) for item in vector):
        raise BridgeDataError(f"{label} must contain only finite values")
    return vector


def _pyarrow():
    try:
        import pyarrow.parquet as pq
    except ImportError as error:
        raise BridgeDataError(
            "pyarrow is required for BridgeData Parquet extraction"
        ) from error
    return pq


@dataclass(frozen=True)
class EpisodeTask:
    """Declared ownership and provenance range for one data-file episode."""

    episode_index: int
    task_index: int | None
    task: str | None
    length: int
    dataset_from_index: int
    dataset_to_index: int

    def validate(self) -> None:
        if self.episode_index < 0:
            raise BridgeDataError("episode_index must be non-negative")
        if self.task_index is not None and self.task_index < 0:
            raise BridgeDataError("episode task_index must be non-negative when mapped")
        if self.task is not None and not isinstance(self.task, str):
            raise BridgeDataError("episode task must be a string when present")
        if self.length < 1:
            raise BridgeDataError("episode length must be positive")
        if self.dataset_from_index < 0:
            raise BridgeDataError("episode dataset_from_index must be non-negative")
        if self.dataset_to_index <= self.dataset_from_index:
            raise BridgeDataError("episode dataset range must be non-empty")
        if self.dataset_to_index - self.dataset_from_index != self.length:
            raise BridgeDataError("episode length disagrees with dataset index range")


@dataclass(frozen=True)
class BridgeDataTransition:
    """One observed and provenance-proven state[t] + action[t] -> state[t+1]."""

    transition_id: str
    episode_index: int
    task_index: int
    task: str
    source_index: int
    target_index: int
    source_frame_index: int
    target_frame_index: int
    source_timestamp: float
    target_timestamp: float
    state_t: tuple[float, ...]
    action_t: tuple[float, ...]
    state_t_plus_1: tuple[float, ...]

    def validate(self) -> None:
        if not self.transition_id:
            raise BridgeDataError("transition_id is required")
        if self.episode_index < 0 or self.task_index < 0 or not self.task:
            raise BridgeDataError("transition identifiers are invalid")
        if self.target_index != self.source_index + 1:
            raise BridgeDataError("transition global indices are not consecutive")
        if self.target_frame_index != self.source_frame_index + 1:
            raise BridgeDataError("transition frame indices are not consecutive")
        if not self.target_timestamp > self.source_timestamp:
            raise BridgeDataError("transition timestamp must increase")
        _finite_vector(self.state_t, "transition state_t")
        _finite_vector(self.action_t, "transition action_t")
        _finite_vector(self.state_t_plus_1, "transition state_t_plus_1")

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for name in ("state_t", "action_t", "state_t_plus_1"):
            payload[name] = list(payload[name])
        return payload

    def canonical_json(self) -> str:
        return _canonical_json(self.to_dict())

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BridgeDataTransitionConfig:
    """Caller-declared bounded selection and continuity contract."""

    selected_episode_indices: frozenset[int]
    max_transitions: int | None = None
    expected_frame_period_seconds: float = 0.2
    timestamp_tolerance_seconds: float = 0.001
    parquet_batch_size: int = 8_192

    def validate(self) -> None:
        if not isinstance(self.selected_episode_indices, frozenset):
            raise BridgeDataError("selected_episode_indices must be a frozenset")
        if not self.selected_episode_indices:
            raise BridgeDataError("at least one complete selected episode is required")
        if any(
            isinstance(value, bool) or not isinstance(value, int) or value < 0
            for value in self.selected_episode_indices
        ):
            raise BridgeDataError("selected_episode_indices must contain non-negative integers")
        if self.max_transitions is not None and self.max_transitions <= 0:
            raise BridgeDataError("max_transitions must be positive when specified")
        if not math.isfinite(self.expected_frame_period_seconds) or self.expected_frame_period_seconds <= 0:
            raise BridgeDataError("expected_frame_period_seconds must be positive and finite")
        if not math.isfinite(self.timestamp_tolerance_seconds) or self.timestamp_tolerance_seconds < 0:
            raise BridgeDataError("timestamp_tolerance_seconds must be finite and non-negative")
        if self.parquet_batch_size < 1:
            raise BridgeDataError("parquet_batch_size must be positive")


@dataclass(frozen=True)
class BridgeDataReceipt:
    """Immutable summary of verified sources and selected observed transitions."""

    transition_version: int
    manifest_path: str
    manifest_sha256: str
    source_files: dict[str, dict[str, Any]]
    data_rows: int
    selected_episode_count: int
    selected_frame_count: int
    expected_selected_frame_count: int
    transition_count: int
    expected_unbounded_transition_count: int
    capped: bool
    rejected_cross_episode_pairs: int
    rejected_nonconsecutive_frame_pairs: int
    rejected_nonconsecutive_index_pairs: int
    rejected_timestamp_pairs: int
    transition_set_sha256: str
    config: dict[str, Any]
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["notes"] = list(self.notes)
        return payload

    def canonical_json(self) -> str:
        return _canonical_json(self.to_dict())

    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BridgeDataIntake:
    """Verified local evidence with episode/task lineage for one data shard."""

    root: Path
    manifest_path: Path
    manifest_sha256: str
    data_path: Path
    episode_path: Path
    task_path: Path
    data_rows: int
    source_files: dict[str, dict[str, Any]]
    episodes: dict[int, EpisodeTask]


@dataclass(frozen=True)
class BridgeDataTransitionDataset:
    """A bounded immutable selection of real observed one-step transitions."""

    receipt: BridgeDataReceipt
    transitions: tuple[BridgeDataTransition, ...]


def _load_manifest(manifest_path: Path) -> tuple[dict[str, Any], str]:
    if not manifest_path.is_file():
        raise BridgeDataError(f"intake manifest does not exist: {manifest_path}")
    manifest_sha256 = sha256_file(manifest_path)
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BridgeDataError("intake manifest is not valid UTF-8 JSON") from error
    if not isinstance(manifest, dict):
        raise BridgeDataError("intake manifest root must be an object")
    if manifest.get("schema_version") != INTAKE_SCHEMA_VERSION:
        raise BridgeDataError("intake manifest schema_version is not supported")
    source = _require_mapping(manifest.get("source"), "intake manifest source")
    if source.get("upstream") != "BridgeData V2":
        raise BridgeDataError("intake manifest upstream must be BridgeData V2")
    design = _require_mapping(
        manifest.get("initial_evaluation_design"), "initial_evaluation_design"
    )
    if design.get("source_partition") != (
        "one acquired data shard; split must be derived by episode_id, never random frame split"
    ):
        raise BridgeDataError("intake manifest must forbid random-frame splitting")
    if design.get("input") != ["observation.state[t]", "action[t]"]:
        raise BridgeDataError("intake manifest input contract is not the declared 7D state/action task")
    if design.get("target") != "observation.state[t+1]":
        raise BridgeDataError("intake manifest target contract is not next state")
    return manifest, manifest_sha256


def _verified_file_evidence(root: Path, manifest: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    raw_files = manifest.get("files")
    if not isinstance(raw_files, list) or not raw_files:
        raise BridgeDataError("intake manifest files must be a non-empty list")
    verified: dict[str, dict[str, Any]] = {}
    for raw_evidence in raw_files:
        evidence = _require_mapping(raw_evidence, "intake file evidence")
        relative_path = evidence.get("relative_path")
        if not isinstance(relative_path, str) or not relative_path:
            raise BridgeDataError("intake file evidence relative_path is required")
        relative = Path(relative_path)
        if relative.is_absolute() or ".." in relative.parts:
            raise BridgeDataError("intake file evidence path escapes the intake root")
        if relative_path in verified:
            raise BridgeDataError("intake manifest repeats a file evidence path")
        expected_hash = str(evidence.get("sha256", "")).lower()
        expected_bytes = evidence.get("bytes")
        if len(expected_hash) != 64 or any(char not in "0123456789abcdef" for char in expected_hash):
            raise BridgeDataError(f"intake file evidence has invalid SHA-256: {relative_path}")
        expected_bytes = _require_int(expected_bytes, f"intake file bytes for {relative_path}")
        if expected_bytes < 0:
            raise BridgeDataError("intake file byte count must be non-negative")
        path = (root / relative).resolve()
        try:
            path.relative_to(root.resolve())
        except ValueError as error:
            raise BridgeDataError("intake file evidence path escapes the intake root") from error
        if not path.is_file():
            raise BridgeDataError(f"frozen intake file is missing: {relative_path}")
        actual_bytes = path.stat().st_size
        if actual_bytes != expected_bytes:
            raise BridgeDataError(
                f"frozen intake byte count mismatch for {relative_path}: "
                f"expected {expected_bytes}, got {actual_bytes}"
            )
        actual_hash = sha256_file(path)
        if actual_hash != expected_hash:
            raise BridgeDataError(
                f"frozen intake SHA-256 mismatch for {relative_path}: "
                f"expected {expected_hash}, got {actual_hash}"
            )
        verified[relative_path] = {
            "path": str(path),
            "bytes": actual_bytes,
            "sha256": actual_hash,
        }
    if not set(REQUIRED_INTAKE_FILES).issubset(verified):
        missing = sorted(set(REQUIRED_INTAKE_FILES) - set(verified))
        raise BridgeDataError("intake manifest lacks required frozen files: " + ", ".join(missing))
    return dict(sorted(verified.items()))


def _required_columns(schema_names: Iterable[str], required: tuple[str, ...], label: str) -> None:
    missing = sorted(set(required) - set(schema_names))
    if missing:
        raise BridgeDataError(f"{label} Parquet schema lacks required columns: {', '.join(missing)}")


def _load_episode_tasks(episode_path: Path, task_path: Path, data_rows: int) -> dict[int, EpisodeTask]:
    pq = _pyarrow()
    task_file = pq.ParquetFile(task_path)
    _required_columns(task_file.schema_arrow.names, REQUIRED_TASK_COLUMNS, "task")
    task_lookup: dict[str, int] = {}
    seen_task_indices: set[int] = set()
    for row in task_file.read(columns=list(REQUIRED_TASK_COLUMNS)).to_pylist():
        task_name = row["task"]
        task_index = _require_int(row["task_index"], "task_index")
        # The published task catalog can retain blank rows for tasks absent
        # from this bounded data file. They carry no selected-episode lineage
        # and are ignored; any selected episode still requires an exact,
        # non-empty task-string mapping below.
        if not isinstance(task_name, str) or not task_name:
            continue
        if task_name in task_lookup or task_index in seen_task_indices:
            raise BridgeDataError("task table contains duplicate task or task_index")
        task_lookup[task_name] = task_index
        seen_task_indices.add(task_index)

    episode_file = pq.ParquetFile(episode_path)
    _required_columns(episode_file.schema_arrow.names, REQUIRED_EPISODE_COLUMNS, "episode")
    episodes: dict[int, EpisodeTask] = {}
    ranges: list[tuple[int, int, int]] = []
    for row in episode_file.read(columns=list(REQUIRED_EPISODE_COLUMNS)).to_pylist():
        if _require_int(row["data/chunk_index"], "data/chunk_index") != 0 or _require_int(
            row["data/file_index"], "data/file_index"
        ) != 0:
            continue
        raw_tasks = row["tasks"]
        if not isinstance(raw_tasks, list) or len(raw_tasks) != 1:
            raise BridgeDataError("selected-data episode must declare exactly one task string")
        task_name = raw_tasks[0]
        if not isinstance(task_name, str):
            raise BridgeDataError("episode task must be a string")
        # An unrelated episode can reference a blank/missing catalog entry in
        # published metadata. Retain its range for provenance, but it is
        # ineligible for extraction until an exact catalog mapping exists.
        mapped_task_index = task_lookup.get(task_name)
        episode = EpisodeTask(
            episode_index=_require_int(row["episode_index"], "episode_index"),
            task_index=mapped_task_index,
            task=task_name if mapped_task_index is not None else None,
            length=_require_int(row["length"], "episode length"),
            dataset_from_index=_require_int(row["dataset_from_index"], "dataset_from_index"),
            dataset_to_index=_require_int(row["dataset_to_index"], "dataset_to_index"),
        )
        episode.validate()
        if episode.episode_index in episodes:
            raise BridgeDataError("episode metadata repeats an episode_index")
        if episode.dataset_to_index > data_rows:
            raise BridgeDataError("episode metadata range exceeds the selected data file")
        episodes[episode.episode_index] = episode
        ranges.append((episode.dataset_from_index, episode.dataset_to_index, episode.episode_index))
    if not episodes:
        raise BridgeDataError("no episode metadata refers to data/chunk-000/file-000")
    ordered_ranges = sorted(ranges)
    for previous, current in zip(ordered_ranges, ordered_ranges[1:]):
        if current[0] < previous[1]:
            raise BridgeDataError("episode metadata contains overlapping dataset ranges")
    return dict(sorted(episodes.items()))


def load_bridgedata_intake(manifest_path: str | Path) -> BridgeDataIntake:
    """Verify all manifest-bound inputs and return episode/task lineage.

    This verifies every listed frozen input before opening the data Parquet
    payload.  It does not derive transition records and therefore cannot begin
    a training-like workload by itself.
    """

    resolved_manifest = Path(manifest_path).expanduser().resolve()
    manifest, manifest_sha256 = _load_manifest(resolved_manifest)
    root = resolved_manifest.parent.resolve()
    source_files = _verified_file_evidence(root, manifest)
    data_path = Path(source_files["data_chunk-000_file-000.parquet"]["path"])
    episode_path = Path(source_files["meta_episodes_chunk-000_file-000.parquet"]["path"])
    task_path = Path(source_files["meta_tasks.parquet"]["path"])
    pq = _pyarrow()
    data_file = pq.ParquetFile(data_path)
    _required_columns(data_file.schema_arrow.names, REQUIRED_DATA_COLUMNS, "data")
    data_rows = int(data_file.metadata.num_rows)
    if data_rows < 2:
        raise BridgeDataError("data Parquet must contain at least two rows")
    episodes = _load_episode_tasks(episode_path, task_path, data_rows)
    return BridgeDataIntake(
        root=root,
        manifest_path=resolved_manifest,
        manifest_sha256=manifest_sha256,
        data_path=data_path,
        episode_path=episode_path,
        task_path=task_path,
        data_rows=data_rows,
        source_files=source_files,
        episodes=episodes,
    )


def transition_set_sha256(transitions: Iterable[BridgeDataTransition]) -> str:
    """Return an order-sensitive digest of the exact extracted transition set."""

    materialized = tuple(transitions)
    ids = [transition.transition_id for transition in materialized]
    if len(ids) != len(set(ids)):
        raise BridgeDataError("transition set contains duplicate transition IDs")
    payload = "\n".join(
        f"{transition.transition_id}:{transition.sha256()}" for transition in materialized
    ) + "\n"
    return hashlib.sha256(payload.encode("ascii")).hexdigest()


def _selected_episode_map(
    intake: BridgeDataIntake, config: BridgeDataTransitionConfig
) -> dict[int, EpisodeTask]:
    unknown = sorted(set(config.selected_episode_indices) - set(intake.episodes))
    if unknown:
        raise BridgeDataError("selected episode identifiers are absent from frozen metadata: " + ", ".join(map(str, unknown[:10])))
    selected = {
        episode_index: intake.episodes[episode_index]
        for episode_index in sorted(config.selected_episode_indices)
    }
    unmapped = [
        episode_index
        for episode_index, episode in selected.items()
        if episode.task_index is None or not episode.task
    ]
    if unmapped:
        raise BridgeDataError(
            "selected episode lacks an exact non-empty frozen task-table mapping: "
            + ", ".join(map(str, unmapped[:10]))
        )
    return selected


def _row_from_parquet(raw: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "state": _finite_vector(raw["observation.state"], "observation.state"),
        "action": _finite_vector(raw["action"], "action"),
        "timestamp": float(raw["timestamp"]),
        "frame_index": _require_int(raw["frame_index"], "frame_index"),
        "episode_index": _require_int(raw["episode_index"], "episode_index"),
        "index": _require_int(raw["index"], "index"),
        "task_index": _require_int(raw["task_index"], "task_index"),
    }


def derive_bridgedata_transitions(
    intake: BridgeDataIntake,
    config: BridgeDataTransitionConfig,
) -> BridgeDataTransitionDataset:
    """Extract only selected, consecutive, observed state-transition records.

    The Parquet source is streamed in row order.  A transition exists only when
    the two records prove same-episode, consecutive frame/index identifiers,
    declared task ownership, and the expected positive 5 Hz timestamp interval.
    The selected episode set is mandatory; no all-shard materialization path is
    available.
    """

    if not isinstance(intake, BridgeDataIntake):
        raise BridgeDataError("derive_bridgedata_transitions requires a verified BridgeDataIntake")
    config.validate()
    selected_episodes = _selected_episode_map(intake, config)
    expected_frames = sum(episode.length for episode in selected_episodes.values())
    expected_unbounded_transitions = sum(
        max(0, episode.length - 1) for episode in selected_episodes.values()
    )
    observed_frames: dict[int, int] = {episode_index: 0 for episode_index in selected_episodes}
    transitions: list[BridgeDataTransition] = []
    rejected_cross_episode_pairs = 0
    rejected_nonconsecutive_frame_pairs = 0
    rejected_nonconsecutive_index_pairs = 0
    rejected_timestamp_pairs = 0
    previous: dict[str, Any] | None = None

    pq = _pyarrow()
    data_file = pq.ParquetFile(intake.data_path)
    for batch in data_file.iter_batches(
        batch_size=config.parquet_batch_size,
        columns=list(REQUIRED_DATA_COLUMNS),
    ):
        for raw_row in batch.to_pylist():
            row = _row_from_parquet(raw_row)
            episode_index = row["episode_index"]
            if episode_index not in selected_episodes:
                previous = None
                continue
            episode = selected_episodes[episode_index]
            if row["task_index"] != episode.task_index:
                raise BridgeDataError(
                    f"data task_index disagrees with episode metadata for episode {episode_index}"
                )
            if not episode.dataset_from_index <= row["index"] < episode.dataset_to_index:
                raise BridgeDataError(
                    f"data index lies outside its declared episode range for episode {episode_index}"
                )
            if not math.isfinite(row["timestamp"]):
                raise BridgeDataError("timestamp must be finite")
            observed_frames[episode_index] += 1
            if previous is not None:
                if row["episode_index"] != previous["episode_index"]:
                    rejected_cross_episode_pairs += 1
                elif row["frame_index"] != previous["frame_index"] + 1:
                    rejected_nonconsecutive_frame_pairs += 1
                elif row["index"] != previous["index"] + 1:
                    rejected_nonconsecutive_index_pairs += 1
                elif abs(
                    (row["timestamp"] - previous["timestamp"])
                    - config.expected_frame_period_seconds
                ) > config.timestamp_tolerance_seconds:
                    rejected_timestamp_pairs += 1
                elif config.max_transitions is None or len(transitions) < config.max_transitions:
                    transition = BridgeDataTransition(
                        transition_id=(
                            f"bridgedata-e{episode_index}-f{previous['frame_index']}"
                            f"-i{previous['index']}"
                        ),
                        episode_index=episode_index,
                        task_index=episode.task_index,
                        task=episode.task,
                        source_index=previous["index"],
                        target_index=row["index"],
                        source_frame_index=previous["frame_index"],
                        target_frame_index=row["frame_index"],
                        source_timestamp=previous["timestamp"],
                        target_timestamp=row["timestamp"],
                        state_t=previous["state"],
                        action_t=previous["action"],
                        state_t_plus_1=row["state"],
                    )
                    transition.validate()
                    transitions.append(transition)
            previous = row

    observed_total = sum(observed_frames.values())
    missing_episode_frames = {
        episode_index: (episode.length, observed_frames[episode_index])
        for episode_index, episode in selected_episodes.items()
        if observed_frames[episode_index] != episode.length
    }
    if missing_episode_frames:
        raise BridgeDataError(
            "selected data rows do not exactly cover declared complete episode lengths: "
            + _canonical_json({str(key): list(value) for key, value in missing_episode_frames.items()})
        )
    if rejected_nonconsecutive_frame_pairs:
        raise BridgeDataError("selected complete episode contains non-consecutive frame indices")
    if rejected_nonconsecutive_index_pairs:
        raise BridgeDataError("selected complete episode contains non-consecutive global indices")
    if rejected_timestamp_pairs:
        raise BridgeDataError("selected complete episode violates the declared timestamp continuity")
    if not transitions:
        raise BridgeDataError("selected episodes yielded no verified consecutive transitions")
    capped = config.max_transitions is not None and len(transitions) < expected_unbounded_transitions
    receipt = BridgeDataReceipt(
        transition_version=BRIDGEDATA_TRANSITION_VERSION,
        manifest_path=str(intake.manifest_path),
        manifest_sha256=intake.manifest_sha256,
        source_files=intake.source_files,
        data_rows=intake.data_rows,
        selected_episode_count=len(selected_episodes),
        selected_frame_count=observed_total,
        expected_selected_frame_count=expected_frames,
        transition_count=len(transitions),
        expected_unbounded_transition_count=expected_unbounded_transitions,
        capped=capped,
        rejected_cross_episode_pairs=rejected_cross_episode_pairs,
        rejected_nonconsecutive_frame_pairs=rejected_nonconsecutive_frame_pairs,
        rejected_nonconsecutive_index_pairs=rejected_nonconsecutive_index_pairs,
        rejected_timestamp_pairs=rejected_timestamp_pairs,
        transition_set_sha256=transition_set_sha256(transitions),
        config={
            "selected_episode_indices": sorted(config.selected_episode_indices),
            "max_transitions": config.max_transitions,
            "expected_frame_period_seconds": config.expected_frame_period_seconds,
            "timestamp_tolerance_seconds": config.timestamp_tolerance_seconds,
            "parquet_batch_size": config.parquet_batch_size,
        },
        notes=(
            "Observed BridgeData state/action rows only; no policy, control, safety, or physical-action claim.",
            "Every emitted record requires same-episode and consecutive frame/index proof.",
            "The caller supplied complete episode identifiers before extraction; random-frame selection is unavailable.",
            "No model training, candidate creation, renderer operation, parent mutation, or promotion occurs in this module.",
        ),
    )
    return BridgeDataTransitionDataset(receipt=receipt, transitions=tuple(transitions))
