"""Primus Phase 1 compiler and render witness.

Executes the real ChronoSophia compiler against typed world programs and emits
hash-bound receipts. Evidence labels follow the multi-lane charter:

``generated``  produced synthetically by our own code
``inferred``   derived from other data by our own code
``observed``   a real execution ran and its output was hashed

Nothing in this module labels synthetic output ``observed``.
"""

from .witness import (  # noqa: F401
    CapabilityBinding,
    CapabilityLedger,
    CompilerReceipt,
    EvidenceLabel,
    FailureClass,
    WitnessError,
    WitnessReport,
    bind_capabilities,
    compile_program,
    witness_dataset,
    write_witness_report,
)

__all__ = [
    "CapabilityBinding",
    "CapabilityLedger",
    "CompilerReceipt",
    "EvidenceLabel",
    "FailureClass",
    "WitnessError",
    "WitnessReport",
    "bind_capabilities",
    "compile_program",
    "witness_dataset",
    "write_witness_report",
]
