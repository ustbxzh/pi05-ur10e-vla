# Reproduction Protocol

Status: **Protocol Design — Not Yet Executed**

1. Record source snapshot identity, Python/driver versions and the OpenPI commit marker.
2. Collect mock data and run `validate_ur10e_dataset.py`.
3. After hardware approval, collect UR10e episodes and archive immutable dataset metadata.
4. Compute norm stats with the exact dataset repo id and save them with the run manifest.
5. Run the named LoRA profile, recording all overrides and checkpoint hashes.
6. Start the upstream policy server from a local verified checkpoint.
7. Run predefined mock, then guarded real rollouts; record aborts as attempts.
8. Populate experiment/result templates only from retained logs and evidence.

TODO: add actual environment lock, commands, hashes and outputs after execution. No hardware, training or evaluation result is claimed by this document.

