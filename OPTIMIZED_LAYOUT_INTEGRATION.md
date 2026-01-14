# Optimized Layout Integration

## What Was Done

Integrated the optimized actor positions (48% improvement) into the Svelte web app with a toggle to switch between layouts.

## Changes Made

### 1. Extracted Optimized Permutation
**File**: `src/lib/data/optimized-permutation-100.json`

Contains the optimized permutation mapping for 100 actors:
```json
{
  "permutation": [15, 50, 46, 29, 24, ...]
}
```

This means actor at index 0 goes to position 15, actor at index 1 goes to position 50, etc.

### 2. Created Settings Store
**File**: `src/lib/stores/settings.ts`

Simple toggle for optimized layout:
```typescript
{
  useOptimizedLayout: boolean  // default: true
}
```

### 3. Updated Graph Store
**File**: `src/lib/stores/graph.ts`

Modified to apply permutation when loading 100 actors:
```typescript
// Before: actor[i] → position[i]
const position = getCirclePosition(index);

// After: actor[i] → position[permutation[i]]
const positionIndex = permutation ? permutation[index] : index;
const position = getCirclePosition(positionIndex);
```

### 4. Added UI Toggle
**File**: `src/App.svelte`

Added checkbox to toggle between layouts (only visible for 100 actors):
```
[ ] Optimized Layout (48% better)
```

## How It Works

### Default Layout (unchecked)
- Actors positioned by Recognizability order
- Actor with highest Recognizability → Center (position 0)
- Simple Vogel spiral based on fetch order

### Optimized Layout (checked)
- Actors repositioned to minimize distance between co-stars
- Highly-connected actors moved to central positions
- 48% reduction in average distance to costars

## Performance Metrics

| Layout | Avg Distance per Edge | Improvement |
|--------|----------------------|-------------|
| Default (Recognizability order) | 745 px | baseline |
| **Optimized (Greedy+2Opt)** | **384 px** | **48.4%** ✓ |

## User Experience

1. **App loads with optimized layout by default** (checked)
2. **Toggle to compare**: Uncheck to see original layout
3. **Only available for 100 actors**: Toggle hidden for other counts
4. **Instant switching**: Reloads graph on toggle

## Testing

```bash
# Build succeeds
npm run build

# Start dev server
npm run dev

# Then open http://localhost:5173
```

### What to Look For

**With Optimized Layout ON**:
- Actors who appeared in movies together should be closer
- Highly-connected actors (MCU, etc.) should cluster near center
- Average distance: ~384 px

**With Optimized Layout OFF**:
- Actors positioned purely by Recognizability
- Less clustering of co-stars
- Average distance: ~745 px

## Extending to Other Counts

To add optimized layouts for 200, 500, or 1000 actors:

1. **Run optimizer**:
   ```bash
   python3 scripts/optimize-layout.py 200
   ```

2. **Extract permutation**:
   ```bash
   cat optimization_outputs/optimized_200_actors.json | \
     python3 -c "import json, sys; data = json.load(sys.stdin); \
     print(json.dumps({'permutation': data['permutation']}, indent=2))" \
     > src/lib/data/optimized-permutation-200.json
   ```

3. **Update graph.ts**:
   ```typescript
   import optimizedPermutation200 from '../data/optimized-permutation-200.json';

   // In loadActors():
   const permutation =
     useOptimized && count === 100 ? optimizedPermutation.permutation :
     useOptimized && count === 200 ? optimizedPermutation200.permutation :
     null;
   ```

4. **Update toggle visibility in App.svelte**:
   ```svelte
   {#if numberOfNodes === 100 || numberOfNodes === 200}
     <div class="control-group">
       <!-- toggle -->
     </div>
   {/if}
   ```

## Files Added/Modified

**Added**:
- `src/lib/data/optimized-permutation-100.json` (optimized positions)
- `src/lib/stores/settings.ts` (toggle state)
- `OPTIMIZED_LAYOUT_INTEGRATION.md` (this file)

**Modified**:
- `src/lib/stores/graph.ts` (apply permutation)
- `src/App.svelte` (UI toggle)

## Verification

The optimized layout dramatically reduces distances:
- **Total distance**: 231,776 → 120,618 (48% improvement)
- **Avg per edge**: 745 px → 384 px
- **Baseline comparison**: Better than best random shuffle by 30%

See `algorithm_comparison.json` for full head-to-head results.
