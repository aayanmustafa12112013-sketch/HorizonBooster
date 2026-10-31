# Validation status

The repository contains a focused native optimization and a tiny compiled fixture intended to validate its mixin transformation.

## Checks

The GitHub Actions workflow runs formatting, clippy, standalone Rust tests, and the fixture. A passing workflow validates the declared source transformation and runtime helper against the fixture, not interactive gameplay performance.

Full validation against Horizon requires:
- the exact Horizon commit in `compatibility.json`;
- the exact Horizon Mixins commit in `compatibility.json`;
- the native client dependency set and Rust 1.95 toolchain;
- `python3 tools/horizon.py check`, `test`, and `build`.

No FPS or frame-time improvement is claimed until a repeatable before/after benchmark has been run on the same machine, world, render distance, and settings. The initial change trades less frequent full range scans for potentially longer retention of out-of-range entries.
