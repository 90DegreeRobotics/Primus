"""
Circadian controller — drives NeuroCognica Sleep Architecture v0.1.

Sleep is entered on measurable saturation (and/or idle), then executed as:
seal T0 → NREM → REM → VALIDATE → seal T1
"""
from __future__ import annotations

import time
from typing import Optional

from core.config import SovereignConfig, SystemState
from lifecycles.sleep_architecture import SleepArchitecture, SleepCycleReport
from memory.saturation import SaturationReport


class CircadianController:
    """Day/night metabolism for the Sovereign Mind."""

    def __init__(self, config: SovereignConfig, architecture: Optional[SleepArchitecture] = None):
        self.config = config
        self.current_state = SystemState.AWAKE
        self.last_activity_time = time.time()
        self.architecture = architecture
        self.mind = None
        self.steb = None
        self.last_saturation: Optional[SaturationReport] = None
        self.last_cycle: Optional[SleepCycleReport] = None
        self.cycles_completed = 0

    def attach(self, architecture: SleepArchitecture) -> None:
        self.architecture = architecture
        self.mind = architecture.mind
        self.steb = architecture.steb

    def heartbeat(self) -> Optional[SleepCycleReport]:
        """
        Periodic homeostatic check.
        Returns a SleepCycleReport when a cycle runs, else None.
        """
        if self.current_state != SystemState.AWAKE:
            return None

        sat = None
        if self.architecture is not None:
            sat = self.architecture.measure_saturation()
            self.last_saturation = sat

        user_active = self._check_user_activity()
        idle_timeout_s = float(self.config.IDLE_TIMEOUT_MINUTES) * 60.0
        idle_ready = (time.time() - self.last_activity_time) >= idle_timeout_s

        should_sleep = False
        reason = ""
        if sat is not None and sat.should_sleep_hard and self.config.FORCE_SLEEP_ON_HARD_SATURATION:
            should_sleep = True
            reason = f"hard_saturation:{','.join(sat.reasons) or 'composite'}"
        elif sat is not None and sat.should_sleep_soft and (idle_ready or not user_active):
            should_sleep = True
            reason = f"soft_saturation_idle:{','.join(sat.reasons) or 'composite'}"
        elif idle_ready and self.steb is not None and len(self.steb) > 0:
            should_sleep = True
            reason = "idle_with_episodic_pressure"

        if should_sleep:
            print(f"[Circadian] Sleep trigger: {reason}")
            return self.run_sleep_cycle(force=False, reason=reason)
        return None

    def run_sleep_cycle(self, force: bool = False, reason: str = "") -> SleepCycleReport:
        if self.architecture is None:
            raise RuntimeError("SleepArchitecture not attached to CircadianController")

        print(f"[Circadian] Entering sleep cycle (force={force}, reason={reason or 'manual'})")
        self.current_state = SystemState.NREM
        try:
            report = self.architecture.run_cycle(force=force or len(self.architecture.steb) == 0)
            self.last_cycle = report
            self.cycles_completed += 1
            print(
                "[Circadian] Sleep cycle complete: "
                f"nrem={report.nrem.success} rem={report.rem.success} "
                f"validate={report.validate.success} integrity={report.integrity_valid} "
                f"T0={report.t0['merkle_root'][:12] if report.t0 else '?'}… "
                f"T1={report.t1['merkle_root'][:12] if report.t1 else '?'}…"
            )
            if not report.integrity_valid:
                print("[Circadian] WARNING: Forever Law integrity check FAILED after sleep")
            if report.nrem.error:
                print(f"[Circadian] NREM error: {report.nrem.error}")
            if report.rem.error:
                print(f"[Circadian] REM error: {report.rem.error}")
            if report.validate.error:
                print(f"[Circadian] VALIDATE error: {report.validate.error}")
            return report
        finally:
            self.current_state = SystemState.AWAKE
            self._initiate_wake_protocol()

    def transition_to(self, new_state: SystemState):
        """Legacy transition helper used by older tests."""
        print(f"[Circadian] Transitioning from {self.current_state.value} to {new_state.value}")
        if new_state in (SystemState.NREM, SystemState.DEEP_SLEEP):
            self.run_sleep_cycle(force=False, reason="legacy_transition")
        elif new_state == SystemState.AWAKE:
            self._initiate_wake_protocol()
            self.current_state = SystemState.AWAKE
        else:
            self.current_state = new_state

    def _check_user_activity(self) -> bool:
        idle_timeout_s = float(self.config.IDLE_TIMEOUT_MINUTES) * 60.0
        return (time.time() - self.last_activity_time) < idle_timeout_s

    def register_activity(self):
        self.last_activity_time = time.time()

    def _initiate_sleep_protocol(self) -> bool:
        """Backward-compatible sleep entry used by older tests."""
        try:
            report = self.run_sleep_cycle(force=False, reason="legacy_sleep_protocol")
            return bool(report.nrem.success)
        except Exception as exc:
            print(f"[Circadian] Error during consolidation: {exc}")
            return False

    def _initiate_wake_protocol(self):
        print("[Circadian] System Waking Up...")
        self.last_activity_time = time.time()
