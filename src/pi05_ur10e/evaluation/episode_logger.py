"""Append-only JSONL episode event logger."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path


@dataclass(frozen=True)
class EpisodeRecord:
    episode_id: str
    task: str
    status: str
    checkpoint: str
    notes: str = ""


class EpisodeLogger:
    def __init__(self, path: str | Path):
        self.path = Path(path)

    def append(self, record: EpisodeRecord) -> None:
        if record.status not in {"success", "failure", "aborted"}:
            raise ValueError("status must be success, failure, or aborted")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {**asdict(record), "recorded_at": datetime.now(timezone.utc).isoformat()}
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, ensure_ascii=False) + "\n")

