# Layout Optimization Performance (100 Actors)

This report replaces `OPTIMIZATION_GUIDE.md` with the latest metrics from a
fresh run of the current scripts.

## Run Setup

- `scripts/prepare-optimization-data.py` (ordinal_100 ordering) → 100 actors, 309 edges
- `scripts/optimize-layout.py 100` (Recognizability ordering) → 100 actors, 324 edges
- `scripts/relax-layout.py` (uses `optimization-input.json`)

Because the two pipelines currently order actors differently, the swap metrics
and the relaxation metrics are computed on different edge sets. See Notes.

## Metrics (Average Distance Per Edge)

### Initial (from `optimization-input.json`)
- Avg distance: **456.57 px** (309 edges, ordinal_100 ordering)

### Greedy + Swapping (from `optimization_outputs/optimized_100_actors.json`)
- Baseline avg: **728.23 px**
- Greedy avg: **499.96 px**
- Swapping (2-opt) avg: **379.71 px**
- Edges: **324** (Recognizability ordering)

### Relaxation (from `actors_relaxed_positions.csv`)
- Avg distance: **417.41 px** (309 edges, ordinal_100 ordering)

## Notes
- The greedy + swapping metrics are from `scripts/optimize-layout.py`, which
  uses Recognizability ordering and a different edge set (324 edges).
- Relaxation metrics are from the ordinal_100-ordered dataset (309 edges).
- If you want fully comparable numbers across all stages, we should align both
  scripts to the same ordering and edge set, then re-run.
