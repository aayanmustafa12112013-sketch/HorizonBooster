# Horizon Optimizer

Horizon Optimizer is a native source-mixin mod for Horizon. It targets the chunk-streaming update path and reduces how often the engine performs its periodic full sweep of loaded columns and proto chunks.

## Current optimization

Horizon already runs a range sweep immediately when the player's chunk center or render radius changes. Otherwise, it periodically scans loaded chunk/proto collections to unload work that moved out of range.

This mod changes the periodic interval from **8 streaming ticks to 16**. The immediate area-change sweep remains untouched. The goal is to reduce recurring scan overhead on CPU-limited systems; it is not a replacement for Sodium and does not currently add new GPU culling, mesh batching, or shader optimizations.

## Compatibility

- Horizon revision: `ba6344a59cb9e755b730dcf02285fc0d33b97d3c` (Nightly 2026-10-30)
- Horizon Mixins: `d9c83d7096b7ea5b83678da2efdfd6161f74997e` (0.6.0)
- Game version: 26.3
- Native bundle ID: `horizon_optimizer`

Native mods are source bundles. The Horizon launcher compiles them into a custom Horizon executable for the pinned revision. This is not an ordinary `.hmod` and cannot be dropped into the normal content-mod folder.

## Build and package

The repository includes a deterministic packager:

```sh
python3 tools/package.py
```

It writes `target/horizon_optimizer-0.1.0.hnmod`. Full native staging/build requires Linux, Rust 1.95, Python 3.12+, Git, Cargo, a Horizon checkout containing the pinned commit, and a clean Horizon Mixins checkout at the pinned revision. See `VALIDATION.md` and the upstream Horizon Mixins documentation.

## Scope and limitations

This is an initial targeted optimization, not a claim of broad FPS gains. The sweep runs less often, so stale out-of-range chunk/proto entries may remain until the next sweep. Moving the player or changing render distance still triggers an immediate sweep. Benchmarking is required to determine whether this helps a particular world, CPU, and render distance.

License: MIT.
