# Actor Layout Optimization - Quick Start

## Single Command to Run

```bash
python3 scripts/optimize-layout.py <number_of_actors>
```

## Examples

```bash
# 100 actors (~9 seconds)
python3 scripts/optimize-layout.py 100

# 500 actors (~1 minute)
python3 scripts/optimize-layout.py 500

# 1,000 actors (~5 minutes)
python3 scripts/optimize-layout.py 1000
```

## What It Does

1. **Fetches** top N actors from Supabase (by Recognizability)
2. **Fetches** all movie connections between these actors
3. **Optimizes** their positions to minimize distance between co-stars
4. **Saves** results to `optimization_outputs/optimized_{N}_actors.json`

## Expected Results

| Actors | Time | Improvement | Final Avg Distance |
|--------|------|-------------|--------------------|
| 100 | 9s | ~50% | ~370 px |
| 200 | 13s | ~42% | ~605 px |
| 500 | 60s | ~39% | ~950 px |
| 1,000 | 5min | ~35% | ~1,100 px |

## Output Format

```json
{
  "metadata": {
    "num_actors": 100,
    "num_edges": 314,
    "algorithm": "greedy_plus_2opt",
    "total_time_seconds": 7.94
  },
  "results": {
    "baseline_avg_per_edge": 745.04,
    "optimized_avg_per_edge": 384.13,
    "total_improvement_percent": 48.44
  },
  "actors": [...],  // Full actor data with metadata
  "permutation": [...] // Actor i → Position j mapping
}
```

## The Algorithm

**Two-stage optimization:**

1. **Greedy** (~25% improvement, instant)
   - Assign highly-connected actors to central positions

2. **2-Opt Local Search** (~25% more improvement, seconds)
   - Iteratively swap pairs of actors to reduce total distance
   - Adaptive iteration count based on problem size
   - Early stopping when convergence detected

## Why This Algorithm?

Tested head-to-head on identical data:

| Method | Result | Time |
|--------|--------|------|
| Simulated Annealing | 34% improvement | 152 seconds |
| **Greedy + 2-Opt** | **51% improvement** | **0.33 seconds** |

**Winner**: Greedy+2Opt is 26% better and 461× faster ✓

## Dependencies

```bash
pip3 install scipy numpy pandas python-dotenv supabase matplotlib
```

## Environment Setup

Requires `.env` file with Supabase credentials:
```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

## Full Documentation

See [`OPTIMIZATION_GUIDE.md`](./OPTIMIZATION_GUIDE.md) for detailed explanation of:
- How the algorithm works
- Convergence analysis
- Adaptive iteration logic
- Scaling to 10,000+ actors
- Troubleshooting

## Verify It Works

```bash
# Run comparison test
python3 scripts/compare-algorithms.py

# Analyze convergence
python3 scripts/analyze-convergence.py 200 20000
```
