"""Deterministic diagnostics for a schema-valid non-executable transition witness."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Iterable, Sequence

from .chronos_transition_contract import ChronosTransitionEvidence, ChronosTransitionContractError


class TransitionDiagnosticError(ValueError):
    """Raised when raw observed transition lineage cannot be matched exactly."""


@dataclass(frozen=True)
class ObservedTransitionSequence:
    """Verified observed continuation corresponding to a transition witness."""

    episode_index: int
    task_index: int
    observed_state_sequence: tuple[tuple[float, ...], ...]
    source_transition_ids: tuple[str, ...]


def _vector(value: Sequence[float], name: str) -> tuple[float, ...]:
    try:
        result = tuple(float(item) for item in value)
    except (TypeError, ValueError) as error:
        raise TransitionDiagnosticError(f"{name} is not numeric") from error
    if len(result) != 7 or not all(math.isfinite(item) for item in result):
        raise TransitionDiagnosticError(f"{name} must be a finite 7D vector")
    return result


def resolve_observed_sequence(
    transitions: Iterable[Any], evidence: ChronosTransitionEvidence,
) -> ObservedTransitionSequence:
    """Match the contract’s initial state/actions to one exact observed episode sequence.

    Matching uses only identifiers and recorded initial state/actions. It never
    uses the predicted states to select a target continuation.
    """

    evidence.validate()
    ordered = tuple(sorted(
        (item for item in transitions if int(item.episode_index) == evidence.episode_index),
        key=lambda item: int(item.source_frame_index),
    ))
    if not ordered:
        raise TransitionDiagnosticError("witness episode has no extracted transitions")
    if len({str(item.transition_id) for item in ordered}) != len(ordered):
        raise TransitionDiagnosticError("witness episode contains duplicate transition identifiers")
    starts: list[int] = []
    for index, transition in enumerate(ordered):
        if int(transition.task_index) != evidence.task_index:
            continue
        if _vector(transition.state_t, "observed state") != evidence.observed_initial_state:
            continue
        if _vector(transition.action_t, "observed action") != evidence.observed_action_sequence[0]:
            continue
        starts.append(index)
    matches: list[ObservedTransitionSequence] = []
    for start in starts:
        sequence = ordered[start:start + evidence.horizon]
        if len(sequence) != evidence.horizon:
            continue
        valid = True
        for offset, transition in enumerate(sequence):
            if int(transition.episode_index) != evidence.episode_index:
                valid = False
                break
            if int(transition.task_index) != evidence.task_index:
                valid = False
                break
            if int(transition.source_frame_index) != int(sequence[0].source_frame_index) + offset:
                valid = False
                break
            if _vector(transition.action_t, "observed action") != evidence.observed_action_sequence[offset]:
                valid = False
                break
        if valid:
            matches.append(ObservedTransitionSequence(
                episode_index=evidence.episode_index,
                task_index=evidence.task_index,
                observed_state_sequence=tuple(_vector(item.state_t_plus_1, "observed target state") for item in sequence),
                source_transition_ids=tuple(str(item.transition_id) for item in sequence),
            ))
    if len(matches) != 1:
        raise TransitionDiagnosticError("witness has no unique raw observed transition lineage")
    return matches[0]


def component_absolute_errors(
    observed: ObservedTransitionSequence,
    evidence: ChronosTransitionEvidence,
) -> tuple[tuple[float, ...], ...]:
    """Return exact per-step per-coordinate absolute error for the verified lineage."""

    if len(observed.observed_state_sequence) != evidence.horizon:
        raise TransitionDiagnosticError("observed lineage horizon disagrees with witness")
    errors: list[tuple[float, ...]] = []
    for observed_state, predicted_state in zip(observed.observed_state_sequence, evidence.predicted_state_sequence, strict=True):
        errors.append(tuple(abs(actual - predicted) for actual, predicted in zip(observed_state, predicted_state, strict=True)))
    return tuple(errors)
