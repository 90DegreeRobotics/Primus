"""GPU benchmark for full-state versus chunked Primus selective scans."""
from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import torch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from substrate.mamba_custom import SelectiveScan


@dataclass(frozen=True)
class BenchmarkShape:
    batch: int
    sequence_length: int
    width: int
    state_width: int


DEFAULT_SHAPES = (
    BenchmarkShape(1, 256, 256, 16),
    BenchmarkShape(1, 512, 384, 16),
    BenchmarkShape(1, 1024, 512, 16),
    BenchmarkShape(2, 1024, 512, 16),
    BenchmarkShape(4, 2048, 1024, 16),
)


def clear_cuda() -> None:
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()


def make_inputs(shape: BenchmarkShape, seed: int):
    generator = torch.Generator(device="cuda").manual_seed(seed)
    x = torch.randn(
        shape.batch,
        shape.sequence_length,
        shape.width,
        device="cuda",
        dtype=torch.float32,
        generator=generator,
    ) * 0.2
    delta = torch.rand(
        shape.batch,
        shape.sequence_length,
        shape.width,
        device="cuda",
        dtype=torch.float32,
        generator=generator,
    ) * 0.05 + 0.001
    transition = -(
        torch.rand(
            shape.width,
            shape.state_width,
            device="cuda",
            dtype=torch.float32,
            generator=generator,
        )
        + 0.1
    )
    input_projection = torch.randn(
        shape.batch,
        shape.sequence_length,
        shape.state_width,
        device="cuda",
        dtype=torch.float32,
        generator=generator,
    ) * 0.1
    output_projection = torch.randn(
        shape.batch,
        shape.sequence_length,
        shape.state_width,
        device="cuda",
        dtype=torch.float32,
        generator=generator,
    ) * 0.1
    skip = torch.randn(
        shape.width,
        device="cuda",
        dtype=torch.float32,
        generator=generator,
    ) * 0.1
    return x, delta, transition, input_projection, output_projection, skip


def scan_function(mode: str, chunk_size: int) -> Callable:
    if mode == "reference":
        return SelectiveScan.forward_scan_reference

    def chunked(*values):
        return SelectiveScan.forward_scan(*values, chunk_size=chunk_size)

    return chunked


def one_measurement(
    mode: str,
    workload: str,
    shape: BenchmarkShape,
    *,
    chunk_size: int,
    iterations: int,
    seed: int,
) -> dict:
    clear_cuda()
    torch.cuda.reset_peak_memory_stats()
    scan = scan_function(mode, chunk_size)
    status = "completed"
    error = None
    elapsed = None
    tokens_per_second = 0.0
    try:
        base = make_inputs(shape, seed)
        for _ in range(1):
            if workload == "forward_backward":
                warm_values = tuple(
                    value.detach().clone().requires_grad_(True)
                    for value in base
                )
                warm = scan(*warm_values)
                warm.square().mean().backward()
                del warm_values
            else:
                with torch.no_grad():
                    warm = scan(*base)
            del warm
        clear_cuda()
        torch.cuda.reset_peak_memory_stats()
        started = time.perf_counter()
        for iteration in range(iterations):
            if workload == "forward_backward":
                values = tuple(
                    value.detach().clone().requires_grad_(True)
                    for value in base
                )
                output = scan(*values)
                output.square().mean().backward()
            else:
                with torch.no_grad():
                    output = scan(*base)
            del output
        torch.cuda.synchronize()
        elapsed = time.perf_counter() - started
        tokens = shape.batch * shape.sequence_length * iterations
        tokens_per_second = tokens / max(elapsed, 1e-9)
    except torch.cuda.OutOfMemoryError as exception:
        status = "oom"
        error = str(exception)
        torch.cuda.empty_cache()
    result = {
        "mode": mode,
        "workload": workload,
        "shape": asdict(shape),
        "chunk_size": chunk_size if mode == "chunked" else None,
        "iterations": iterations,
        "status": status,
        "error": error,
        "elapsed_seconds": elapsed,
        "tokens_per_second": tokens_per_second,
        "peak_allocated_gb": torch.cuda.max_memory_allocated() / 1e9,
        "peak_reserved_gb": torch.cuda.max_memory_reserved() / 1e9,
        "full_state_tensor_gb": (
            shape.batch
            * shape.sequence_length
            * shape.width
            * shape.state_width
            * 4
            / 1e9
        ),
        "chunk_state_tensor_ceiling_gb": (
            shape.batch
            * min(shape.sequence_length, chunk_size)
            * shape.width
            * shape.state_width
            * 4
            / 1e9
        ),
    }
    clear_cuda()
    return result


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--chunk-size", type=int, default=64)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20260826)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is required")
    results = []
    stop_reference = False
    stop_chunked = False
    for shape_index, shape in enumerate(DEFAULT_SHAPES):
        for workload in ("forward", "forward_backward"):
            if not stop_reference:
                result = one_measurement(
                    "reference",
                    workload,
                    shape,
                    chunk_size=args.chunk_size,
                    iterations=args.iterations,
                    seed=args.seed + shape_index,
                )
                results.append(result)
                print(json.dumps(result, sort_keys=True), flush=True)
                if result["status"] == "oom":
                    stop_reference = True
            if not stop_chunked:
                result = one_measurement(
                    "chunked",
                    workload,
                    shape,
                    chunk_size=args.chunk_size,
                    iterations=args.iterations,
                    seed=args.seed + shape_index,
                )
                results.append(result)
                print(json.dumps(result, sort_keys=True), flush=True)
                if result["status"] == "oom":
                    stop_chunked = True
        if stop_reference and stop_chunked:
            break
    payload = {
        "benchmark": "primus_chunked_selective_scan_v1",
        "device": torch.cuda.get_device_name(0),
        "cuda_total_memory_gb": torch.cuda.get_device_properties(0).total_memory / 1e9,
        "chunk_size": args.chunk_size,
        "iterations": args.iterations,
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
