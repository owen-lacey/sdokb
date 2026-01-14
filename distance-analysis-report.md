# Actor Distance Analysis Report

**Date**: January 13, 2026
**Dataset**: Top 100 actors by recognizability
**Distance Matrix**: 100x100 Euclidean distances between actor positions

## Executive Summary

This analysis examines the average distance between actors and their costars (actors they've appeared in movies with) across different position arrangements.

### Key Findings

- **Mean average distance across 10 shuffled iterations**: 740.73 pixels
- **Range**: 710.59 - 775.62 pixels (variation of ~65 pixels)
- **Original layout average distance**: 739.37 pixels

The original layout produces an average distance very close to the mean across shuffled iterations, suggesting it's reasonably well-optimized for minimizing costar distances.

## Methodology

1. **Data Sources**:
   - Actor positions from `actors_with_positions.csv` (first 100 actors)
   - Pre-computed distance matrix from `distance-matrix-100.json`
   - Actor connections (movie collaborations) from Supabase database

2. **Analysis Process**:
   - Load 100 actors with their positions
   - Fetch all movie connections between these actors (21,670 connections total)
   - Calculate average Euclidean distance for each actor to their costars only
   - Compute overall average across all actors with connections

3. **Shuffled Position Test**:
   - Randomly reassign positions to actors 10 times
   - Recalculate average distances for each shuffle
   - Compare variance to understand layout sensitivity

## Detailed Results

### Shuffled Position Iterations

| Iteration | Average Distance (px) |
|-----------|----------------------|
| 1         | 727.61              |
| 2         | 723.26              |
| 3         | 746.55              |
| 4         | 775.62              |
| 5         | 739.70              |
| 6         | 720.33              |
| 7         | 770.03              |
| 8         | 710.59              |
| 9         | 756.22              |
| 10        | 737.41              |

### Statistical Summary

- **Mean**: 740.73 px
- **Minimum**: 710.59 px
- **Maximum**: 775.62 px
- **Range**: 65.03 px
- **Standard Deviation**: ~20.5 px (approximate)

## Original Layout Analysis

### Actors with Extreme Average Distances

**Closest to Costars:**
- Cardi B: 171.00 px (1 connection)
- Laurence Olivier: 211.00 px (1 connection)
- Sidney Poitier: 266.00 px (1 connection)

**Furthest from Costars:**
- Meghan: 1,509.00 px (1 connection)
- Diane Keaton: 1,354.00 px (1 connection)
- John Boyega: 1,233.50 px (4 connections)

### Most Connected Actors

- **Tilda Swinton**: 23 connections, avg distance 1,019.74 px
- **Scarlett Johansson**: 21 connections, avg distance 750.90 px
- **Steve Carell**: 20 connections, avg distance 856.75 px
- **Robert Downey Jr.**: 18 connections, avg distance 753.67 px
- **Benedict Cumberbatch**: 17 connections, avg distance 534.41 px

### Actors with No Connections

The following actors in the top 100 had no movie connections with other actors in this dataset:
- John Legend
- Harry Styles
- Hugh Hefner
- Ruth Bader Ginsburg
- Paul McCartney
- Pitbull
- Chris Brown
- Millie Bobby Brown
- Aishwarya Rai Bachchan

## Interpretation

1. **Layout Quality**: The original layout (739.37 px average) is very close to the mean of shuffled layouts (740.73 px), indicating it performs near the average for random arrangements.

2. **Variance**: The 65-pixel range across shuffled iterations suggests that position arrangement has a moderate impact on average costar distances.

3. **Connection Density**: With 21,670 connections among 100 actors, the network is highly connected (out of ~88 actors with connections), averaging multiple collaborations per actor.

4. **Outliers**: Actors with only 1 connection show the highest variance in average distance, ranging from 171 px (Cardi B) to 1,509 px (Meghan), depending on where their single costar is positioned.

## Scripts Used

- `scripts/analyze-connected-distances.js`: Single analysis of current layout
- `scripts/analyze-shuffled-distances.js`: Multiple iterations with shuffled positions

### Running the Analysis

```bash
# Single analysis
export $(cat .env | grep VITE_SUPABASE | xargs) && \
  node scripts/analyze-connected-distances.js

# Shuffled analysis (default 10 iterations)
export $(cat .env | grep VITE_SUPABASE | xargs) && \
  node scripts/analyze-shuffled-distances.js 10
```

## Recommendations

1. **Layout Optimization**: Consider implementing a force-directed layout algorithm that minimizes the distance between connected actors.

2. **Connection Weighting**: Weight distances by number of shared movies to prioritize frequent collaborators.

3. **Clustering**: Implement community detection to group actors who frequently work together in the same region.

4. **Further Analysis**: Test with larger sample sizes (e.g., 50-100 shuffled iterations) to get more robust statistical measures.
