"""
Primus Sleep Architecture — desktop operator surface.

Founder path is buttons, not terminals:
  Sleep Now / Status / Verify / Send / Quit

Launches the CCF + Sleep Architecture v0.1 runtime under SovereignConfig.operator().
"""
from __future__ import annotations

import json
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox
from pathlib import Path

import torch

from core.config import SovereignConfig
from main import build_runtime, _apply_wake_plasticity
from memory.steb import Episode


class PrimusOperatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Primus — Sleep Architecture v0.1")
        self.root.geometry("920x640")
        self.root.minsize(720, 480)

        self._busy = False
        self.runtime = None
        self.hidden_state = None

        header = tk.Frame(root, padx=12, pady=10)
        header.pack(fill=tk.X)
        tk.Label(
            header,
            text="PRIMUS",
            font=("Segoe UI Semibold", 22),
        ).pack(anchor="w")
        tk.Label(
            header,
            text="WAKE → SATURATE → NREM → REM → VALIDATE → SEAL",
            font=("Segoe UI", 10),
        ).pack(anchor="w")

        controls = tk.Frame(root, padx=12, pady=4)
        controls.pack(fill=tk.X)
        self.btn_sleep = tk.Button(controls, text="Sleep Now", width=14, command=self.on_sleep)
        self.btn_status = tk.Button(controls, text="Status", width=12, command=self.on_status)
        self.btn_verify = tk.Button(controls, text="Verify Ledger", width=14, command=self.on_verify)
        self.btn_sleep.pack(side=tk.LEFT, padx=(0, 6))
        self.btn_status.pack(side=tk.LEFT, padx=(0, 6))
        self.btn_verify.pack(side=tk.LEFT, padx=(0, 6))

        self.status_var = tk.StringVar(value="Booting operator runtime…")
        tk.Label(root, textvariable=self.status_var, anchor="w", padx=12).pack(fill=tk.X)

        self.log = scrolledtext.ScrolledText(root, height=22, wrap=tk.WORD, font=("Consolas", 10))
        self.log.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        self.log.configure(state=tk.DISABLED)

        input_row = tk.Frame(root, padx=12, pady=8)
        input_row.pack(fill=tk.X)
        self.entry = tk.Entry(input_row, font=("Segoe UI", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.entry.bind("<Return>", lambda _e: self.on_send())
        tk.Button(input_row, text="Send", width=10, command=self.on_send).pack(side=tk.LEFT)

        self.root.after(50, self._boot)

    def _set_busy(self, busy: bool, label: str | None = None):
        self._busy = busy
        state = tk.DISABLED if busy else tk.NORMAL
        for btn in (self.btn_sleep, self.btn_status, self.btn_verify):
            btn.configure(state=state)
        if label:
            self.status_var.set(label)

    def _append(self, text: str):
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, text + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def _boot(self):
        def work():
            try:
                config = SovereignConfig.operator()
                data_root = Path(__file__).resolve().parent.parent / config.DATA_ROOT / "operator"
                runtime = build_runtime(config=config, data_root=data_root)
                self.root.after(0, lambda: self._on_booted(runtime))
            except Exception as exc:
                self.root.after(0, lambda: self._on_boot_fail(exc))

        self._set_busy(True, "Booting…")
        threading.Thread(target=work, daemon=True).start()

    def _on_booted(self, runtime):
        self.runtime = runtime
        self.hidden_state = None
        self._set_busy(False, f"AWAKE · device={runtime['device']} · tip={runtime['codex'].tip_hash or 'genesis'}")
        self._append(
            f"[boot] Sleep Architecture v0.1 ready\n"
            f"  data_root={runtime['data_root']}\n"
            f"  forever_law_events={len(runtime['codex'])}\n"
            f"  canonical_beliefs={len(runtime['canonical'])}\n"
            f"  model_dim={runtime['config'].MODEL_DIM}"
        )
        self.entry.focus_set()

    def _on_boot_fail(self, exc: Exception):
        self._set_busy(True, "BOOT FAILED")
        self._append(f"[error] {exc}")
        messagebox.showerror("Primus boot failed", str(exc))

    def on_send(self):
        if self._busy or self.runtime is None:
            return
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, tk.END)
        self._append(f"[you] {text}")
        self._set_busy(True, "WAKE · acquiring…")

        def work():
            try:
                result = self._wake_turn(text)
                self.root.after(0, lambda: self._on_wake_done(result))
            except Exception as exc:
                self.root.after(0, lambda: self._on_action_fail("wake", exc))

        threading.Thread(target=work, daemon=True).start()

    def _wake_turn(self, text: str) -> dict:
        rt = self.runtime
        config = rt["config"]
        device = rt["device"]
        mind = rt["mind"]
        tokenizer = rt["tokenizer"]
        steb = rt["steb"]
        architecture = rt["architecture"]
        heart = rt["heart"]

        heart.register_activity()
        tokens = tokenizer.encode(text).to(device)
        if tokens.numel() == 0:
            return {"response": "...", "surprise": 0.0, "stored": False}

        with torch.no_grad():
            logits, self.hidden_state, surprise = mind(
                tokens.unsqueeze(0),
                self.hidden_state,
                compute_surprise=True,
            )

        response_tokens = []
        gen_hidden = self.hidden_state
        next_input = tokens[-1:].unsqueeze(0)
        for _ in range(40):
            gen_logits, gen_hidden, _ = mind(next_input, gen_hidden, compute_surprise=False)
            next_logits = gen_logits[0, -1, :] / 0.8
            probs = torch.softmax(next_logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)
            token_id = int(next_token.item())
            eos_id = (
                tokenizer.tokenizer.eos_token_id
                if getattr(tokenizer, "tokenizer", None) is not None
                else None
            )
            if eos_id is not None and token_id == eos_id:
                break
            response_tokens.append(token_id)
            next_input = next_token.view(1, 1)
            if len(response_tokens) > 3 and len(set(response_tokens[-4:])) == 1:
                break

        response = (
            tokenizer.decode(torch.tensor(response_tokens, dtype=torch.long))
            if response_tokens
            else "..."
        )
        if surprise is not None and surprise.size(1) > 1:
            avg_surprise = float(surprise[0, 1:].mean().item())
        else:
            avg_surprise = 0.0

        architecture.saturation.observe_surprise(avg_surprise)
        _apply_wake_plasticity(mind, tokens.cpu(), config, device)

        stored = False
        if avg_surprise > config.MIN_SURPRISE_THRESHOLD:
            episode = Episode(
                token_ids=tokens.detach().cpu(),
                surprise=avg_surprise,
                timestamp=time.time(),
                text=text,
            )
            if steb.push(episode):
                event_id = architecture.record_wake_episode(episode, text=text)
                episode.forever_law_event_id = event_id
                stored = True

        # Homeostatic sleep check after acquisition.
        cycle = heart.heartbeat()
        sat = architecture.measure_saturation()
        return {
            "response": response,
            "surprise": avg_surprise,
            "stored": stored,
            "saturation": sat.to_dict(),
            "cycle": cycle.to_dict() if cycle is not None else None,
            "tip": rt["codex"].tip_hash,
        }

    def _on_wake_done(self, result: dict):
        self._append(
            f"[mind] {result['response']}\n"
            f"  surprise={result['surprise']:.3f} stored={result['stored']} "
            f"composite={result['saturation']['composite']:.3f}"
        )
        if result.get("cycle"):
            c = result["cycle"]
            self._append(
                f"[sleep] cycle complete integrity={c.get('integrity_valid')} "
                f"T1={((c.get('t1') or {}).get('merkle_root') or '')[:16]}…"
            )
        self._set_busy(False, f"AWAKE · tip={(result.get('tip') or 'genesis')[:16]}…")

    def on_sleep(self):
        if self._busy or self.runtime is None:
            return
        self._set_busy(True, "SLEEP · consolidating…")
        self._append("[sleep] operator forced full cycle")

        def work():
            try:
                report = self.runtime["heart"].run_sleep_cycle(force=True, reason="operator_ui")
                self.root.after(0, lambda: self._on_sleep_done(report.to_dict()))
            except Exception as exc:
                self.root.after(0, lambda: self._on_action_fail("sleep", exc))

        threading.Thread(target=work, daemon=True).start()

    def _on_sleep_done(self, report: dict):
        self._append(json.dumps({
            "cycle_id": report.get("cycle_id"),
            "nrem": report.get("nrem"),
            "rem": report.get("rem"),
            "validate": report.get("validate"),
            "integrity_valid": report.get("integrity_valid"),
            "t0": (report.get("t0") or {}).get("merkle_root"),
            "t1": (report.get("t1") or {}).get("merkle_root"),
            "candidates": report.get("candidates"),
        }, indent=2)[:6000])
        ok = bool(report.get("integrity_valid"))
        self._set_busy(False, "AWAKE · sleep sealed" if ok else "AWAKE · sleep integrity FAILED")
        if not ok:
            messagebox.showwarning("Forever Law", "Sleep completed but integrity check failed.")

    def on_status(self):
        if self._busy or self.runtime is None:
            return
        rt = self.runtime
        sat = rt["architecture"].measure_saturation()
        payload = {
            "state": rt["heart"].current_state.value,
            "steb": len(rt["steb"]),
            "forever_law_events": len(rt["codex"]),
            "canonical_beliefs": len(rt["canonical"]),
            "cycles_completed": rt["heart"].cycles_completed,
            "saturation": sat.to_dict(),
            "tip_hash": rt["codex"].tip_hash,
        }
        self._append(json.dumps(payload, indent=2))

    def on_verify(self):
        if self._busy or self.runtime is None:
            return
        report = self.runtime["codex"].verify_full_chain()
        self._append(json.dumps(report.to_dict(), indent=2))
        if not report.valid:
            messagebox.showerror("Forever Law", "Chain integrity FAILED.")
            self.status_var.set("INTEGRITY FAILED")
        else:
            self.status_var.set(f"Integrity OK · events={report.total_events}")

    def _on_action_fail(self, action: str, exc: Exception):
        self._append(f"[error:{action}] {exc}")
        self._set_busy(False, f"ERROR · {action}")
        messagebox.showerror(f"Primus {action} failed", str(exc))


def main():
    root = tk.Tk()
    PrimusOperatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
