# Graph Layout Optimization Progress

## Run: 2026-01-16

### Step 1: Random Baseline
- Edge count: 324
- Total distance: 235,828.99
- Avg distance: 727.87
- Min distance: 134.85
- Max distance: 1545.23

### Step 2: Centrality Ordering
- Edge count: 324
- Total distance: 171,930.00
- Avg distance: 530.65
- Min distance: 128.16
- Max distance: 1323.83
- **vs baseline: ↓27.1%**

Top actor: Tilda Swinton (28 connections)

### Step 3: Swap Optimization
- Edge count: 324
- Total distance: 120,943.15
- Avg distance: 373.28
- Min distance: 128.16
- Max distance: 1049.88
- **vs previous step: ↓29.7%**
- **vs baseline: ↓48.7%**

Iterations: 9,762 | Swaps accepted: 156 | Time: 0.06s

### Step 4: Force-Directed Relaxation
- Edge count: 324
- Total distance: 66,218.37
- Avg distance: 204.38
- Min distance: 52.43
- Max distance: 595.33
- **vs previous step: ↓45.2%**
- **vs baseline: ↓71.9%**

Iterations: 477 | Time: 0.39s | MIN_DISTANCE: 160

---

## Summary

| Step | Avg Distance | vs Baseline |
|------|--------------|-------------|
| 1. Random Baseline | 727.87 | — |
| 2. Centrality Ordering | 530.65 | ↓27.1% |
| 3. Swap Optimization | 373.28 | ↓48.7% |
| 4. Force Relaxation | **204.38** | **↓71.9%** |
