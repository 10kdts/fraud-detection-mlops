"""Production monitoring primitives: PSI drift and prediction summaries."""

from __future__ import annotations

import json
import math
from pathlib import Path


def population_stability_index(reference: list[float], current: list[float], bins: int = 10) -> float:
    if not reference or not current:
        raise ValueError("reference and current must not be empty")
    ordered = sorted(reference)
    edges = [ordered[min(int(len(ordered) * index / bins), len(ordered) - 1)] for index in range(1, bins)]

    def distribution(values: list[float]) -> list[float]:
        counts = [0] * bins
        for value in values:
            bucket = sum(value > edge for edge in edges)
            counts[bucket] += 1
        return [max(count / len(values), 0.0001) for count in counts]

    expected, actual = distribution(reference), distribution(current)
    return sum((a - e) * math.log(a / e) for e, a in zip(expected, actual))


def drift_status(psi: float) -> str:
    if psi >= 0.25:
        return "critical"
    if psi >= 0.10:
        return "warning"
    return "stable"


def write_monitoring_report(reference: list[float], current: list[float], output: Path) -> dict[str, object]:
    psi = population_stability_index(reference, current)
    report = {"metric": "population_stability_index", "psi": round(psi, 4), "status": drift_status(psi)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

