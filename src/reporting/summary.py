from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

METRIC_KEYS = (
    "jobs_found",
    "matching_jobs",
    "applications_prepared",
    "applications_submitted",
    "errors",
)


def write_metrics(metrics: Mapping[str, int], path: str | Path = "data/run-metrics.json") -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {key: int(metrics.get(key, 0)) for key in METRIC_KEYS}
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_metrics(path: str | Path = "data/run-metrics.json") -> dict[str, int]:
    target = Path(path)
    if not target.exists():
        return {key: 0 for key in METRIC_KEYS}
    payload = json.loads(target.read_text(encoding="utf-8"))
    return {key: int(payload.get(key, 0)) for key in METRIC_KEYS}


def to_markdown(metrics: Mapping[str, int], *, note: str | None = None) -> str:
    lines = [
        "## AI Job Agent — Daily Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
        f"| Jobs found | {int(metrics.get('jobs_found', 0))} |",
        f"| Matching jobs | {int(metrics.get('matching_jobs', 0))} |",
        f"| Applications prepared | {int(metrics.get('applications_prepared', 0))} |",
        f"| Applications submitted | {int(metrics.get('applications_submitted', 0))} |",
        f"| Errors | {int(metrics.get('errors', 0))} |",
    ]
    if note:
        lines.extend(["", f"> {note}"])
    return "\n".join(lines) + "\n"
