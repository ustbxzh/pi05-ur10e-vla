# Failure Analysis Protocol

Status: **Protocol Design — Not Yet Executed**

For every failed or aborted episode, retain episode id, task, checkpoint hash, dataset/norm-stat identity, RTC mode, failure stage, category, operator note and evidence path. Suggested categories are perception/prompt mismatch, grasp, collision avoidance, workspace clipping, controller rejection, communication timeout, chunk discontinuity and operator abort.

Do not silently exclude aborted runs. Separate policy failures from integration/safety stops. Report denominator rules before evaluation and derive success rates only with `evaluation.metrics.success_summary` or an equivalent reviewed script.

TODO: define task-specific success criteria and inter-rater review before real evaluation.

