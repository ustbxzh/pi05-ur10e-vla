"""Metrics computed only from explicit episode labels."""

from __future__ import annotations

from collections.abc import Iterable


def success_summary(statuses: Iterable[str]) -> dict[str, int | float | None]:
    values = list(statuses)
    invalid = set(values) - {"success", "failure", "aborted"}
    if invalid:
        raise ValueError(f"unknown statuses: {sorted(invalid)}")
    completed = sum(value in {"success", "failure"} for value in values)
    successes = values.count("success")
    return {
        "attempted": len(values),
        "completed": completed,
        "successes": successes,
        "aborted": values.count("aborted"),
        "success_rate": successes / completed if completed else None,
    }

