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

### Step 1: Random Baseline
*Timestamp: 2026-01-22 15:28:25*

- Edge count: 324
- Total distance: 235,828.99
- Avg distance: 727.87
- Min distance: 134.85
- Max distance: 1545.23

- Random seed: 42
- Description: Baseline with randomly shuffled ordinal positions

### Step 2: Centrality Ordering
*Timestamp: 2026-01-22 15:28:46*

- Edge count: 324
- Total distance: 171,930.00
- Avg distance: 530.65
- Min distance: 128.16
- Max distance: 1323.83
- **vs baseline: ↓27.1%**

- Ordering: By degree (connection count), descending
- Top actor: Tilda Swinton (28 connections)

### Step 3: Swap Optimization
*Timestamp: 2026-01-22 15:28:53*

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
*Timestamp: 2026-01-22 15:29:02*

- Edge count: 324
- Total distance: 66,218.37
- Avg distance: 204.38
- Min distance: 52.43
- Max distance: 595.33
- **vs previous step: ↓45.2%**
- **vs baseline: ↓71.9%**

- Iterations: 477
- Improvement from Step 3: 45.2%
- Converged: True
- Time: 0.39s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 15:57:34*

- Edge count: 324
- Total distance: 66,218.37
- Avg distance: 204.38
- Min distance: 52.43
- Max distance: 595.33
- **vs previous step: ↓45.2%**
- **vs baseline: ↓71.9%**

- Iterations: 477
- Improvement from Step 3: 45.2%
- Converged: True
- Time: 0.39s

### Step 1: Random Baseline
*Timestamp: 2026-01-22 16:04:29*

- Edge count: 1362
- Total distance: 1,397,724.46
- Avg distance: 1026.23
- Min distance: 133.99
- Max distance: 2237.08

- Random seed: 42
- Description: Baseline with randomly shuffled ordinal positions

### Step 2: Centrality Ordering
*Timestamp: 2026-01-22 16:10:25*

- Edge count: 1413
- Total distance: 1,091,837.08
- Avg distance: 772.71
- Min distance: 128.16
- Max distance: 1952.02
- **vs baseline: ↓24.7%**

- Ordering: By degree (connection count), descending
- Top actor: Steve Carell (44 connections)

### Step 3: Swap Optimization
*Timestamp: 2026-01-22 16:10:59*

- Edge count: 1413
- Total distance: 815,721.48
- Avg distance: 577.30
- Min distance: 128.16
- Max distance: 1952.05
- **vs previous step: ↓25.3%**
- **vs baseline: ↓43.7%**

- Iterations: 42,549
- Swaps accepted: 549
- Time: 0.50s
- Stopped: stagnation

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 16:11:23*

- Edge count: 1413
- Total distance: 310,126.15
- Avg distance: 219.48
- Min distance: 33.07
- Max distance: 695.59
- **vs previous step: ↓62.0%**
- **vs baseline: ↓78.6%**

- Iterations: 445
- Improvement from Step 3: 62.0%
- Converged: True
- Time: 1.43s

### Step 1: Random Baseline
*Timestamp: 2026-01-22 16:26:33*

- Edge count: 1362
- Total distance: 1,397,724.46
- Avg distance: 1026.23
- Min distance: 133.99
- Max distance: 2237.08

- Random seed: 42
- Description: Baseline with randomly shuffled ordinal positions

### Step 2: Centrality Ordering
*Timestamp: 2026-01-22 16:27:01*

- Edge count: 1413
- Total distance: 1,091,837.08
- Avg distance: 772.71
- Min distance: 128.16
- Max distance: 1952.02
- **vs baseline: ↓24.7%**

- Ordering: By degree (connection count), descending
- Top actor: Steve Carell (44 connections)

### Step 3: Swap Optimization
*Timestamp: 2026-01-22 16:27:07*

- Edge count: 1413
- Total distance: 815,721.48
- Avg distance: 577.30
- Min distance: 128.16
- Max distance: 1952.05
- **vs previous step: ↓25.3%**
- **vs baseline: ↓43.7%**

- Iterations: 42,549
- Swaps accepted: 549
- Time: 0.33s
- Stopped: stagnation

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 16:27:12*

- Edge count: 1413
- Total distance: 310,126.15
- Avg distance: 219.48
- Min distance: 33.07
- Max distance: 695.59
- **vs previous step: ↓62.0%**
- **vs baseline: ↓78.6%**

- Iterations: 445
- Improvement from Step 3: 62.0%
- Converged: True
- Time: 1.02s

### Step 1: Random Baseline
*Timestamp: 2026-01-22 16:31:55*

- Edge count: 5674
- Total distance: 9,414,341.24
- Avg distance: 1659.21
- Min distance: 134.06
- Max distance: 3520.97

- Random seed: 42
- Description: Baseline with randomly shuffled ordinal positions

### Step 2: Centrality Ordering
*Timestamp: 2026-01-22 16:32:37*

- Edge count: 5878
- Total distance: 6,837,891.44
- Avg distance: 1163.30
- Min distance: 131.11
- Max distance: 3140.04
- **vs baseline: ↓29.9%**

- Ordering: By degree (connection count), descending
- Top actor: Samuel L. Jackson (106 connections)

### Step 3: Swap Optimization
*Timestamp: 2026-01-22 16:32:46*

- Edge count: 5878
- Total distance: 5,508,970.07
- Avg distance: 937.22
- Min distance: 128.16
- Max distance: 3006.09
- **vs previous step: ↓19.4%**
- **vs baseline: ↓43.5%**

- Iterations: 50,000
- Swaps accepted: 1,145
- Time: 0.63s
- Stopped: max_iterations

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 16:33:01*

- Edge count: 5878
- Total distance: 1,425,507.52
- Avg distance: 242.52
- Min distance: 18.85
- Max distance: 1065.91
- **vs previous step: ↓74.1%**
- **vs baseline: ↓85.4%**

- Iterations: 487
- Improvement from Step 3: 74.1%
- Converged: True
- Time: 6.78s

### Step 1: Random Baseline
*Timestamp: 2026-01-22 16:44:44*

- Edge count: 1362
- Total distance: 1,397,724.46
- Avg distance: 1026.23
- Min distance: 133.99
- Max distance: 2237.08

- Random seed: 42
- Description: Baseline with randomly shuffled ordinal positions

### Step 1: Random Baseline
*Timestamp: 2026-01-22 16:45:59*

- Edge count: 18340
- Total distance: 42,433,326.81
- Avg distance: 2313.70
- Min distance: 133.88
- Max distance: 5025.12

- Random seed: 42
- Description: Baseline with randomly shuffled ordinal positions

### Step 2: Centrality Ordering
*Timestamp: 2026-01-22 16:46:46*

- Edge count: 18340
- Total distance: 29,967,039.28
- Avg distance: 1633.97
- Min distance: 128.16
- Max distance: 4730.24
- **vs baseline: ↓29.4%**

- Ordering: By degree (connection count), descending
- Top actor: Samuel L. Jackson (197 connections)

### Step 3: Swap Optimization
*Timestamp: 2026-01-22 16:46:54*

- Edge count: 18340
- Total distance: 25,139,911.15
- Avg distance: 1370.77
- Min distance: 128.16
- Max distance: 4514.36
- **vs previous step: ↓16.1%**
- **vs baseline: ↓40.8%**

- Iterations: 50,000
- Swaps accepted: 1,733
- Time: 1.01s
- Stopped: max_iterations

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 16:47:29*

- Edge count: 18340
- Total distance: 4,723,549.07
- Avg distance: 257.55
- Min distance: 13.80
- Max distance: 1536.43
- **vs previous step: ↓81.2%**
- **vs baseline: ↓88.9%**

- Iterations: 499
- Improvement from Step 3: 81.2%
- Converged: True
- Time: 26.87s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 17:00:38*

- Edge count: 18340
- Total distance: 6,049,189.19
- Avg distance: 329.84
- Min distance: 22.67
- Max distance: 1595.83
- **vs previous step: ↓75.9%**
- **vs baseline: ↓85.7%**

- Iterations: 435
- Improvement from Step 3: 75.9%
- Converged: True
- Time: 23.09s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 17:10:47*

- Edge count: 18340
- Total distance: 21,436,684.69
- Avg distance: 1168.85
- Min distance: 14.49
- Max distance: 3937.16
- **vs previous step: ↓14.7%**
- **vs baseline: ↓49.5%**

- Iterations: 2000
- Improvement from Step 3: 14.7%
- Converged: False
- Time: 87.10s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 17:11:49*

- Edge count: 18340
- Total distance: 24,677,359.45
- Avg distance: 1345.55
- Min distance: 98.56
- Max distance: 4574.60
- **vs previous step: ↓1.8%**
- **vs baseline: ↓41.8%**

- Iterations: 119
- Improvement from Step 3: 1.8%
- Converged: True
- Time: 15.02s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 17:12:43*

- Edge count: 18340
- Total distance: 24,689,182.84
- Avg distance: 1346.19
- Min distance: 95.52
- Max distance: 4562.71
- **vs previous step: ↓1.8%**
- **vs baseline: ↓41.8%**

- Iterations: 91
- Improvement from Step 3: 1.8%
- Converged: True
- Time: 14.16s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:23:57*

- Edge count: 18340
- Total distance: 1,902,909.13
- Avg distance: 103.76
- Min distance: 7.55
- Max distance: 1227.27
- **vs previous step: ↓92.4%**
- **vs baseline: ↓95.5%**

- Iterations: 762
- Improvement from Step 3: 92.4%
- Converged: True
- Time: 63.70s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:27:56*

- Edge count: 18340
- Total distance: 37,317,505.56
- Avg distance: 2034.76
- Min distance: 50.75
- Max distance: 4667.37
- **vs previous step: ↑48.4%**
- **vs baseline: ↓12.1%**

- Iterations: 762
- Improvement from Step 3: -48.4%
- Converged: True
- Time: 67.69s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:28:44*

- Edge count: 18340
- Total distance: 25,024,331.05
- Avg distance: 1364.47
- Min distance: 100.26
- Max distance: 4567.15
- **vs previous step: ↓0.5%**
- **vs baseline: ↓41.0%**

- Iterations: 37
- Improvement from Step 3: 0.5%
- Converged: True
- Time: 5.50s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:33:26*

- Edge count: 18340
- Total distance: 12,623,763.44
- Avg distance: 688.32
- Min distance: 6.89
- Max distance: 1912.38
- **vs previous step: ↓49.8%**
- **vs baseline: ↓70.3%**

- Iterations: 2000
- Improvement from Step 3: 49.8%
- Converged: False
- Time: 251.04s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:35:29*

- Edge count: 18340
- Total distance: 35,402,559.57
- Avg distance: 1930.35
- Min distance: 100.87
- Max distance: 4749.32
- **vs previous step: ↑40.8%**
- **vs baseline: ↓16.6%**

- Iterations: 753
- Improvement from Step 3: -40.8%
- Converged: True
- Time: 68.84s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:38:04*

- Edge count: 18340
- Total distance: 43,936,230.94
- Avg distance: 2395.65
- Min distance: 160.00
- Max distance: 5335.84
- **vs previous step: ↑74.8%**
- **vs baseline: ↑3.5%**

- Iterations: 753
- Improvement from Step 3: -74.8%
- Converged: True
- Time: 73.98s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:43:41*

- Edge count: 18340
- Total distance: 1,905,677.76
- Avg distance: 103.91
- Min distance: 7.19
- Max distance: 1237.61
- **vs previous step: ↓92.4%**
- **vs baseline: ↓95.5%**

- Iterations: 753
- Improvement from Step 3: 92.4%
- Converged: True
- Time: 39.66s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:49:26*

- Edge count: 18340
- Total distance: 2,841,871.70
- Avg distance: 154.95
- Min distance: 9.17
- Max distance: 1268.71
- **vs previous step: ↓88.7%**
- **vs baseline: ↓93.3%**

- Iterations: 704
- Improvement from Step 3: 88.7%
- Converged: True
- Time: 32.77s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:52:16*

- Edge count: 18340
- Total distance: 3,979,949.95
- Avg distance: 217.01
- Min distance: 13.70
- Max distance: 1312.35
- **vs previous step: ↓84.2%**
- **vs baseline: ↓90.6%**

- Iterations: 662
- Improvement from Step 3: 84.2%
- Converged: True
- Time: 28.13s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:53:34*

- Edge count: 18340
- Total distance: 10,206,193.60
- Avg distance: 556.50
- Min distance: 41.42
- Max distance: 2211.26
- **vs previous step: ↓59.4%**
- **vs baseline: ↓75.9%**

- Iterations: 435
- Improvement from Step 3: 59.4%
- Converged: True
- Time: 16.87s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:54:37*

- Edge count: 18340
- Total distance: 2,841,871.70
- Avg distance: 154.95
- Min distance: 9.17
- Max distance: 1268.71
- **vs previous step: ↓88.7%**
- **vs baseline: ↓93.3%**

- Iterations: 704
- Improvement from Step 3: 88.7%
- Converged: True
- Time: 32.38s

### Step 4: Force-Directed Relaxation
*Timestamp: 2026-01-22 21:56:03*

- Edge count: 18340
- Total distance: 1,905,677.76
- Avg distance: 103.91
- Min distance: 7.19
- Max distance: 1237.61
- **vs previous step: ↓92.4%**
- **vs baseline: ↓95.5%**

- Iterations: 753
- Improvement from Step 3: 92.4%
- Converged: True
- Time: 39.64s
