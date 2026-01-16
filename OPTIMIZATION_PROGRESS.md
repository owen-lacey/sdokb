# Graph Layout Optimization Progress

## Run: 2026-01-16 16:16:46

### Step 1: Random Baseline
*Timestamp: 2026-01-16 16:16:46*

- Edge count: 324
- Total distance: 235,828.99
- Avg distance: 727.87
- Min distance: 134.85
- Max distance: 1545.23

- Random seed: 42
- Description: Baseline with randomly shuffled ordinal positions

### Step 2: Centrality Ordering
*Timestamp: 2026-01-16 16:19:40*

- Edge count: 324
- Total distance: 171,930.00
- Avg distance: 530.65
- Min distance: 128.16
- Max distance: 1323.83
- **vs baseline: ↓27.1%**

- Ordering: By degree (connection count), descending
- Top actor: Tilda Swinton (28 connections)

### Step 3: Swap Optimization
*Timestamp: 2026-01-16 16:27:04*

- Edge count: 324
- Total distance: 120,943.15
- Avg distance: 373.28
- Min distance: 128.16
- Max distance: 1049.88
- **vs previous step: ↓29.7%**
- **vs baseline: ↓48.7%**

- Iterations: 9,762
- Swaps accepted: 156
- Time: 0.06s
- Stopped: stagnation

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-16 16:32:11*

- Edge count: 324
- Total distance: 119,110.13
- Avg distance: 367.62
- Min distance: 121.11
- Max distance: 1037.75
- **vs previous step: ↓1.5%**
- **vs baseline: ↓49.5%**

- Iterations: 15
- Improvement from Step 3: 1.5%
- Converged: True
- Time: 0.01s
