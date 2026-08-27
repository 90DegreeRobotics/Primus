"""Fail-hard tests for the Phase 1 compiler witness.

These tests include failure cases deliberately. A gate that proves only that
valid input validates has not tested the boundary.

Tests that require the real compiler skip cleanly when the binary is absent,
and the skip is visible. A skipped test is never reported as a pass.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from world_compile.witness import (  # noqa: E402
    CapabilityLedger,
    EvidenceLabel,
    FailureClass,
    WitnessError,
    bind_capabilities,
    compile_program,
    load_programs,
    witness_dataset,
    write_witness_report,
)
from world_schema import to_s3v_json  # noqa: E402
from world_schema.trajectory_generator import (  # noqa: E402
    TrajectoryGeneratorConfig,
    generate_dataset,
)

COMPILER = Path(r"C:\chronos2\target\release\chronos.exe")
LEDGER = Path(r"C:\chronos2\data\capability_ledger.json")

LEDGER_STUB = [
    {"id": "geometry.core_primitives", "kind": "geometry", "status": "available"},
    {"id": "geometry.katana", "kind": "geometry", "status": "unavailable"},
]


def _small_dataset():
    # train_count must be at least 8: the generator refuses fewer, because
    # eight is the minimum that covers every training family while keeping the
    # composition holdout isolated. Kept at the floor to keep the gate fast.
    config = TrajectoryGeneratorConfig(
        seed=20_260_826,
        train_count=8,
        held_out_object_count=1,
        held_out_operation_count=1,
        held_out_composition_count=1,
    )
    return generate_dataset(config)


def _programs(dataset):
    for attr in ("programs", "records", "items"):
        value = getattr(dataset, attr, None)
        if value:
            return tuple(value)
    raise AssertionError("could not locate programs on generated dataset")


class CapabilityBindingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="witness_cap_"))
        self.ledger_path = self.tmp / "ledger.json"
        self.ledger_path.write_text(json.dumps(LEDGER_STUB), encoding="utf-8")
        self.ledger = CapabilityLedger.load(self.ledger_path)
        self.program = _programs(_small_dataset())[0]

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_declared_available_is_not_trusted_without_the_ledger(self):
        """The generator hardcodes AVAILABLE. The ledger must decide."""
        bindings = bind_capabilities(self.program, self.ledger)
        self.assertTrue(bindings, "fixture declared no capabilities")
        for b in bindings:
            self.assertEqual(b.declared_status, "available")
            self.assertIsNotNone(b.ledger_status)
            self.assertTrue(b.bound)

    def test_normalized_match_is_reported_not_hidden(self):
        """`geometry_core_primitives` binds to `geometry.core_primitives`.

        It must be recorded as a normalized, not exact, match.
        """
        bindings = bind_capabilities(self.program, self.ledger)
        b = bindings[0]
        self.assertEqual(b.declared_id, "geometry_core_primitives")
        self.assertEqual(b.ledger_id, "geometry.core_primitives")
        self.assertFalse(b.exact_match, "normalized match must not claim exact")

    def test_unbound_capability_fails_closed(self):
        empty = self.tmp / "empty_ledger.json"
        empty.write_text("[]", encoding="utf-8")
        bindings = bind_capabilities(self.program, CapabilityLedger.load(empty))
        for b in bindings:
            self.assertFalse(b.bound)
            self.assertFalse(b.executable)
            self.assertIs(b.failure, FailureClass.CAPABILITY_UNBOUND)

    def test_unavailable_ledger_route_is_not_executable(self):
        unavailable = self.tmp / "unavailable.json"
        unavailable.write_text(
            json.dumps(
                [{"id": "geometry.core_primitives", "status": "unavailable"}]
            ),
            encoding="utf-8",
        )
        bindings = bind_capabilities(
            self.program, CapabilityLedger.load(unavailable)
        )
        for b in bindings:
            self.assertTrue(b.bound)
            self.assertFalse(
                b.executable,
                "an unavailable ledger route must never be executable",
            )
            self.assertIs(b.failure, FailureClass.CAPABILITY_UNAVAILABLE)

    def test_missing_ledger_file_raises(self):
        with self.assertRaises(WitnessError):
            CapabilityLedger.load(self.tmp / "nope.json")


class EvidenceLabelTests(unittest.TestCase):
    """Charter §6: nothing is `observed` unless something actually ran."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="witness_label_"))
        self.ledger_path = self.tmp / "ledger.json"
        self.ledger_path.write_text(json.dumps(LEDGER_STUB), encoding="utf-8")
        self.program = _programs(_small_dataset())[0]

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_absent_compiler_is_generated_never_observed(self):
        receipt = compile_program(
            self.program,
            compiler_exe=self.tmp / "does_not_exist.exe",
            workdir=self.tmp / "work",
            ledger=CapabilityLedger.load(self.ledger_path),
        )
        self.assertIs(receipt.failure, FailureClass.COMPILER_ABSENT)
        self.assertIs(receipt.evidence_label, EvidenceLabel.GENERATED)
        self.assertNotEqual(receipt.evidence_label, EvidenceLabel.OBSERVED)
        self.assertFalse(receipt.witnessed)

    def test_report_never_claims_a_render(self):
        report = witness_dataset(
            [self.program],
            compiler_exe=self.tmp / "does_not_exist.exe",
            ledger_path=self.ledger_path,
            workdir=self.tmp / "work2",
        )
        claims = report.to_dict()["claims"]
        self.assertFalse(claims["render_observed"])
        self.assertFalse(claims["visual_correctness_proven"])
        self.assertFalse(claims["learned_world_dynamics_proven"])
        self.assertFalse(claims["model_training_started"])
        self.assertFalse(claims["candidate_promoted"])
        self.assertFalse(report.render_witness_attempted)


class ReportWriterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="witness_write_"))
        self.ledger_path = self.tmp / "ledger.json"
        self.ledger_path.write_text(json.dumps(LEDGER_STUB), encoding="utf-8")
        self.program = _programs(_small_dataset())[0]
        self.report = witness_dataset(
            [self.program],
            compiler_exe=self.tmp / "absent.exe",
            ledger_path=self.ledger_path,
            workdir=self.tmp / "work",
        )

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_writes_report_to_new_destination(self):
        path = write_witness_report(self.report, self.tmp / "out")
        self.assertTrue(path.is_file())
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(payload["program_count"], 1)
        self.assertIn("ledger_sha256", payload)

    def test_existing_destination_is_refused(self):
        dest = self.tmp / "out2"
        write_witness_report(self.report, dest)
        with self.assertRaises(WitnessError):
            write_witness_report(self.report, dest)


@unittest.skipUnless(
    COMPILER.is_file() and LEDGER.is_file(),
    f"real compiler or ledger absent: {COMPILER} / {LEDGER}",
)
class RealCompilerTests(unittest.TestCase):
    """These run the actual ChronoSophia binary. Read-only, no chronos2 writes."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="witness_real_"))
        self.program = _programs(_small_dataset())[0]

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_real_compiler_accepts_fixture_and_receipt_is_observed(self):
        receipt = compile_program(
            self.program,
            compiler_exe=COMPILER,
            workdir=self.tmp / "work",
            ledger=CapabilityLedger.load(LEDGER),
        )
        self.assertEqual(receipt.exit_code, 0, receipt.stderr)
        self.assertIs(receipt.evidence_label, EvidenceLabel.OBSERVED)
        self.assertTrue(receipt.envelope_round_trip_ok)
        self.assertTrue(receipt.witnessed)
        self.assertIs(receipt.failure, FailureClass.NONE)

    def test_compiler_acceptance_does_not_prove_envelope_integrity(self):
        """The measured gap this module exists to cover.

        `s3v validate` accepts a plan whose Primus envelope has been
        destroyed. Compiler exit code 0 therefore does not imply the Primus
        payload survived, and the witness must check the envelope separately.
        """
        s3v = json.loads(to_s3v_json(self.program))
        s3v["title"] = "not-a-valid-envelope"
        artifact = self.tmp / "corrupt.s3v.json"
        artifact.write_text(json.dumps(s3v), encoding="utf-8")

        proc = subprocess.run(  # noqa: S603
            [str(COMPILER), "s3v", "validate", str(artifact)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertEqual(
            proc.returncode,
            0,
            "expected the compiler to accept a destroyed envelope; if this "
            "now fails the compiler has been hardened and this finding "
            "should be re-evaluated",
        )

        from world_schema import from_s3v_json

        with self.assertRaises(Exception):
            from_s3v_json(json.dumps(s3v))

    def test_malformed_json_is_rejected_by_the_real_compiler(self):
        artifact = self.tmp / "malformed.s3v.json"
        artifact.write_text("{ this is not json", encoding="utf-8")
        proc = subprocess.run(  # noqa: S603
            [str(COMPILER), "s3v", "validate", str(artifact)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        self.assertNotEqual(proc.returncode, 0)

    def test_whole_dataset_witness_is_hash_bound(self):
        programs = _programs(_small_dataset())
        report = witness_dataset(
            programs,
            compiler_exe=COMPILER,
            ledger_path=LEDGER,
            workdir=self.tmp / "work_all",
        )
        self.assertEqual(len(report.receipts), len(programs))
        self.assertTrue(report.compiler_present)
        for r in report.receipts:
            self.assertEqual(len(r.program_sha256), 64)
            self.assertEqual(len(r.s3v_sha256), 64)
        self.assertFalse(report.to_dict()["claims"]["render_observed"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
