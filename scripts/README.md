# Actor Layout Optimization Scripts

## Main Optimizer (Single Source of Truth)

**`optimize-layout.py`** - Production optimizer using Greedy + 2-Opt algorithm

```bash
# Optimize 100 actors (~9 seconds)
python3 scripts/optimize-layout.py 100

# Optimize 500 actors (~60 seconds)
python3 scripts/optimize-layout.py 500

# Optimize 1,000 actors (~5 minutes)
python3 scripts/optimize-layout.py 1000
```

**Output**: `optimization_outputs/optimized_{N}_actors.json`

## Supporting Scripts

### Data Preparation
**`prepare-optimization-data.py`** - Fetch actors and connections from Supabase

```bash
python3 scripts/prepare-optimization-data.py
```

Creates `optimization-input.json` with 100 actors (used by comparison script).

### Analysis Scripts

**`analyze-convergence.py`** - Plot convergence curves to tune iteration counts

```bash
python3 scripts/analyze-convergence.py 200 20000
```

Creates convergence plot showing when diminishing returns kick in.

### Gentle Layout Relaxation

**`relax-layout.py`** - Small-step force layout with min distance + recognizability weighting

```bash
python3 scripts/relax-layout.py
```

Outputs `actors_relaxed_positions.csv` with original + relaxed coordinates.
Use `--upsert` to write relaxed positions to Supabase (defaults to `x_100`/`y_100`).

**`compare-algorithms.py`** - Fair comparison of optimization algorithms

```bash
python3 scripts/compare-algorithms.py
```

Compares Greedy+2Opt vs Simulated Annealing on identical data.

### Legacy Analysis (JavaScript)

- `analyze-connected-distances.js` - Original distance analysis
- `analyze-shuffled-distances.js` - Random shuffle baseline testing

These were used to establish the baseline metrics in `distance-analysis-report.md`.

## Quick Start

```bash
# 1. Optimize 200 actors
python3 scripts/optimize-layout.py 200

# 2. Results saved to:
cat optimization_outputs/optimized_200_actors.json
```

## Algorithm Performance

| Actors | Edges | Time | Improvement |
|--------|-------|------|-------------|
| 100 | 309 | 9s | 51% |
| 200 | 1,375 | 13s | 42% |
| 500 | 5,862 | 59s | 39% |

See `../OPTIMIZATION_GUIDE.md` for detailed documentation.
