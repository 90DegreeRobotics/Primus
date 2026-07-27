"""
EXECUTION TRACE LOGGER
Captures high-signal training data from live system interactions.
Implements Day/Night circadian learning loop infrastructure.

Day Phase: Log interactions, code execution, errors, corrections
Night Phase: Distill traces into training examples for consolidation

Architect: Council (Reformed)
Date: February 2026
Version: 1.0 - From Doctrine to Practice
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum


class TraceType(Enum):
    """Categories of execution traces for targeted learning."""
    INTERACTION = "interaction"  # User prompt + system response
    CODE_EXECUTION = "code_execution"  # Code run + stdout/stderr/exit
    ERROR_CORRECTION = "error_correction"  # Error + correction + explanation
    TEST_RESULT = "test_result"  # Test run + pass/fail + diff
    STATE_TRANSITION = "state_transition"  # Awake/Sleep transitions
    SURPRISE = "surprise"  # High free-energy events (STEB worthy)


@dataclass
class ExecutionTrace:
    """
    A single execution event with full provenance.
    Designed for conversion to instruction/response training pairs.
    """
    trace_id: str
    trace_type: TraceType
    timestamp: str

    # Core content
    input_prompt: Optional[str] = None
    output_response: Optional[str] = None

    # Execution specifics
    code_snippet: Optional[str] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    exit_code: Optional[int] = None

    # Error recovery
    error_message: Optional[str] = None
    correction: Optional[str] = None
    explanation: Optional[str] = None

    # Test results
    test_name: Optional[str] = None
    test_passed: Optional[bool] = None
    test_diff: Optional[str] = None

    # Context
    system_state: Optional[str] = None  # AWAKE, DEEP_SLEEP, etc.
    surprise_score: Optional[float] = None  # Free energy measure

    # Provenance
    source_file: Optional[str] = None
    context_hash: str = ""
    quality_score: float = 0.0

    def __post_init__(self):
        """Generate trace ID and context hash."""
        if not self.trace_id:
            content = f"{self.timestamp}{self.trace_type.value}{self.input_prompt or ''}"
            self.trace_id = hashlib.sha256(content.encode()).hexdigest()[:16]

        if not self.context_hash:
            content_parts = [
                self.input_prompt or "",
                self.output_response or "",
                self.code_snippet or ""
            ]
            self.context_hash = hashlib.sha256("".join(content_parts).encode()).hexdigest()[:16]


class ExecutionTraceLogger:
    """
    Logs execution traces during Day phase for Night phase consolidation.
    Implements quality gates and format conversion for training.
    """

    def __init__(self, output_dir: str = "training_data/traces"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.traces: List[ExecutionTrace] = []

        # Quality thresholds
        self.MIN_PROMPT_LENGTH = 10
        self.MIN_RESPONSE_LENGTH = 20
        self.MAX_ERROR_LENGTH = 5000

    def log_interaction(self, prompt: str, response: str,
                       system_state: str = "AWAKE",
                       surprise_score: Optional[float] = None) -> None:
        """Log a user interaction (Day phase acquisition)."""
        trace = ExecutionTrace(
            trace_id="",
            trace_type=TraceType.INTERACTION,
            timestamp=datetime.now().isoformat(),
            input_prompt=prompt,
            output_response=response,
            system_state=system_state,
            surprise_score=surprise_score
        )
        self._add_trace(trace)

    def log_code_execution(self, code: str, stdout: str, stderr: str,
                          exit_code: int, source_file: Optional[str] = None) -> None:
        """Log code execution with full I/O capture."""
        trace = ExecutionTrace(
            trace_id="",
            trace_type=TraceType.CODE_EXECUTION,
            timestamp=datetime.now().isoformat(),
            code_snippet=code,
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code,
            source_file=source_file
        )
        self._add_trace(trace)

    def log_error_correction(self, error: str, correction: str,
                            explanation: str, code_before: Optional[str] = None,
                            code_after: Optional[str] = None) -> None:
        """Log error + correction pairs (gold for preventing repeat mistakes)."""
        trace = ExecutionTrace(
            trace_id="",
            trace_type=TraceType.ERROR_CORRECTION,
            timestamp=datetime.now().isoformat(),
            error_message=error,
            correction=correction,
            explanation=explanation,
            input_prompt=code_before,
            output_response=code_after
        )
        self._add_trace(trace)

    def log_test_result(self, test_name: str, passed: bool,
                       diff: Optional[str] = None,
                       stdout: Optional[str] = None) -> None:
        """Log test execution results."""
        trace = ExecutionTrace(
            trace_id="",
            trace_type=TraceType.TEST_RESULT,
            timestamp=datetime.now().isoformat(),
            test_name=test_name,
            test_passed=passed,
            test_diff=diff,
            stdout=stdout
        )
        self._add_trace(trace)

    def log_state_transition(self, from_state: str, to_state: str,
                            reason: str) -> None:
        """Log circadian state changes (wake/sleep transitions)."""
        trace = ExecutionTrace(
            trace_id="",
            trace_type=TraceType.STATE_TRANSITION,
            timestamp=datetime.now().isoformat(),
            system_state=f"{from_state} -> {to_state}",
            explanation=reason
        )
        self._add_trace(trace)

    def _add_trace(self, trace: ExecutionTrace) -> None:
        """Add trace to buffer with quality check."""
        if self._meets_quality_threshold(trace):
            trace.quality_score = self._compute_quality_score(trace)
            self.traces.append(trace)

    def _meets_quality_threshold(self, trace: ExecutionTrace) -> bool:
        """Quality gate for trace worthiness."""
        # Interaction quality
        if trace.trace_type == TraceType.INTERACTION:
            if not trace.input_prompt or len(trace.input_prompt) < self.MIN_PROMPT_LENGTH:
                return False
            if not trace.output_response or len(trace.output_response) < self.MIN_RESPONSE_LENGTH:
                return False

        # Code execution quality
        if trace.trace_type == TraceType.CODE_EXECUTION:
            if not trace.code_snippet or len(trace.code_snippet) < 10:
                return False

        # Error correction quality
        if trace.trace_type == TraceType.ERROR_CORRECTION:
            if not trace.error_message or not trace.correction:
                return False
            # Truncate massive error dumps
            if trace.error_message and len(trace.error_message) > self.MAX_ERROR_LENGTH:
                trace.error_message = trace.error_message[:self.MAX_ERROR_LENGTH] + "\n[... truncated]"

        return True

    def _compute_quality_score(self, trace: ExecutionTrace) -> float:
        """Assign quality score based on training value."""
        score = 0.5  # Base

        # High-value traces
        if trace.trace_type == TraceType.ERROR_CORRECTION:
            score += 0.3  # Error corrections are gold
        if trace.surprise_score and trace.surprise_score > 2.5:
            score += 0.2  # High-surprise events
        if trace.exit_code == 0 and trace.code_snippet:
            score += 0.1  # Successful executions
        if trace.test_passed is False:
            score += 0.15  # Failed tests teach boundaries

        return min(score, 1.0)

    def flush_to_disk(self, filename: Optional[str] = None) -> Path:
        """Write traces to disk (end of day or explicit save)."""
        if not filename:
            filename = f"execution_traces_{self.session_id}.jsonl"

        output_file = self.output_dir / filename

        with open(output_file, 'w', encoding='utf-8') as f:
            for trace in self.traces:
                # Convert enum to string for JSON serialization
                trace_dict = asdict(trace)
                trace_dict['trace_type'] = trace.trace_type.value
                f.write(json.dumps(trace_dict, ensure_ascii=False) + '\n')

        print(f"✅ Flushed {len(self.traces)} traces to {output_file}")
        return output_file

    def convert_to_training_format(self, output_file: Optional[Path] = None) -> Path:
        """
        Convert execution traces to instruction/response training pairs.
        This is the Night Phase distillation.
        """
        if not output_file:
            output_file = self.output_dir / f"training_from_traces_{self.session_id}.jsonl"

        training_samples = []

        for trace in self.traces:
            samples = self._trace_to_training_samples(trace)
            training_samples.extend(samples)

        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in training_samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')

        print(f"✅ Converted {len(training_samples)} training samples to {output_file}")
        return output_file

    def _trace_to_training_samples(self, trace: ExecutionTrace) -> List[Dict[str, str]]:
        """Convert a single trace to one or more training samples."""
        samples = []

        if trace.trace_type == TraceType.INTERACTION:
            samples.append({
                "instruction": trace.input_prompt or "",
                "input": "",
                "output": trace.output_response or ""
            })

        elif trace.trace_type == TraceType.CODE_EXECUTION:
            if trace.exit_code == 0:
                samples.append({
                    "instruction": "Execute the following code and predict the output:",
                    "input": trace.code_snippet or "",
                    "output": f"Exit code: {trace.exit_code}\nStdout:\n{trace.stdout or '(empty)'}"
                })
            else:
                samples.append({
                    "instruction": "Analyze this code execution failure:",
                    "input": f"Code:\n{trace.code_snippet}\n\nError:\n{trace.stderr}",
                    "output": f"The code failed with exit code {trace.exit_code}. " +
                             (trace.explanation or "Review the error output for debugging.")
                })

        elif trace.trace_type == TraceType.ERROR_CORRECTION:
            samples.append({
                "instruction": "Fix the following error:",
                "input": f"Error:\n{trace.error_message}\n\nOriginal code:\n{trace.input_prompt or '(not provided)'}",
                "output": f"Correction:\n{trace.correction}\n\nExplanation:\n{trace.explanation}"
            })

        elif trace.trace_type == TraceType.TEST_RESULT:
            if not trace.test_passed:
                samples.append({
                    "instruction": f"Analyze why test '{trace.test_name}' failed:",
                    "input": trace.test_diff or trace.stdout or "",
                    "output": "The test failed. Review the diff and correct the implementation to match expected behavior."
                })

        return samples

    def get_summary(self) -> Dict[str, Any]:
        """Get session summary statistics."""
        type_counts = {}
        for trace in self.traces:
            t = trace.trace_type.value
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "session_id": self.session_id,
            "total_traces": len(self.traces),
            "type_distribution": type_counts,
            "avg_quality_score": sum(t.quality_score for t in self.traces) / max(len(self.traces), 1),
            "high_value_traces": sum(1 for t in self.traces if t.quality_score > 0.7)
        }


if __name__ == "__main__":
    # Demo usage
    logger = ExecutionTraceLogger()

    # Simulate day phase logging
    logger.log_interaction(
        prompt="Explain the CCF architecture",
        response="CCF is a Chrono-Compressive Field implementing circadian learning...",
        system_state="AWAKE",
        surprise_score=1.2
    )

    logger.log_code_execution(
        code="print('Hello Primus')",
        stdout="Hello Primus\n",
        stderr="",
        exit_code=0
    )

    logger.log_error_correction(
        error="ImportError: No module named 'nonexistent'",
        correction="pip install required_package",
        explanation="The module was missing from requirements.txt"
    )

    # Flush raw traces
    trace_file = logger.flush_to_disk()

    # Convert to training format (Night phase)
    training_file = logger.convert_to_training_format()

    # Print summary
    summary = logger.get_summary()
    print(f"\n{'='*60}")
    print(f"SESSION SUMMARY:")
    print(json.dumps(summary, indent=2))
    print(f"{'='*60}")
