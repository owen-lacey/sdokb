# Actor Layout Optimization Scripts

A 3-step pipeline to optimize actor positions in a graph visualization by minimizing edge distances.

## Prerequisites

Install dependencies:
```bash
uv pip install python-dotenv supabase
```

Set environment variables in `.env`:
```
VITE_SUPABASE_URL=<your-supabase-url>
VITE_SUPABASE_ANON_KEY=<your-supabase-key>
VITE_GRAPH_LIMIT=100  # Number of actors to optimize
```

## Pipeline Overview

Run the scripts in order. Each step builds on the previous:

| Step | Script | Description |
|------|--------|-------------|
| 1 | `01-random-baseline.py` | Establish baseline with random positions |
| 2 | `02-centrality-ordering.py` | Place highly-connected actors in center |
| 3 | `03-swap-optimization.py` | 2-opt swaps to reduce edge distances |

## Usage

```bash
# Run the full pipeline
python scripts/01-random-baseline.py
python scripts/02-centrality-ordering.py
python scripts/03-swap-optimization.py
```

Each step:
- Reads from the previous step's output in `optimization_outputs/`
- Saves results to `optimization_outputs/{step-name}.json`
- Appends metrics to `OPTIMIZATION_PROGRESS.md`

## Script Details

### Step 1: Random Baseline
Fetches actors from Supabase, assigns random ordinal positions on a Vogel spiral, and calculates baseline edge distance metrics.

**Output:** `optimization_outputs/01-random-baseline.json`

### Step 2: Centrality Ordering
Sorts actors by degree (connection count) and assigns center positions to highly-connected actors.

**Output:** `optimization_outputs/02-centrality-ordering.json`

### Step 3: Swap Optimization
Iteratively swaps pairs of actors if it reduces total edge distance. Stops after 1000 consecutive non-improving attempts.

**Outputs:**
- `optimization_outputs/03-swap-optimization.json`
- `optimization_outputs/graph-data-{N}.json` (frontend-ready)

## Shared Utilities

`optimization_utils.py` provides:
- Supabase client initialization
- Vogel spiral position calculation
- Distance and metrics calculation
- File I/O for step outputs
- Progress tracking

## Output Files

After running the full pipeline:

```
optimization_outputs/
├── 01-random-baseline.json      # Step 1 results
├── 02-centrality-ordering.json  # Step 2 results
├── 03-swap-optimization.json    # Step 3 results
└── graph-data-{N}.json          # Frontend-ready graph data
```

The `graph-data-{N}.json` file can be uploaded to Supabase Storage for the frontend to consume.
