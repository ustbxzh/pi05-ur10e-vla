"""Structured failure labels without fabricated observations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class FailureEntry:
    episode_id: str
    stage: str
    category: str
    evidence_path: str | None
    notes: str


def write_failure_manifest(path: str | Path, failures: list[FailureEntry]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps([asdict(item) for item in failures], indent=2, ensure_ascii=False), encoding="utf-8")

