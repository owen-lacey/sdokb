# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SDOKB is an exploration into Hollywood data — an infinite-scrolling graph visualization of actor relationships. Actors are positioned on a Vogel spiral layout, optimized by a Python pipeline, and rendered as an interactive SVG with pan/zoom.

No users, no backwards compatibility concerns.

## Commands

### Frontend (Svelte 5 + Vite)

```bash
npm run dev       # Start dev server (default port 5173)
npm run build     # Production build → dist/
npm run preview   # Preview production build
npm run check     # TypeScript + Svelte type checking
```

### Python Optimization Pipeline

Requires: `uv pip install python-dotenv supabase`

Run sequentially — each step reads the previous step's output from `optimization_outputs/`:

```bash
python scripts/01-random-baseline.py
python scripts/02-centrality-ordering.py
python scripts/03-swap-optimization.py
```

## Architecture

### Data Flow

```
Supabase DB (actors, actor_connections, movies)
    ↓ Python pipeline
optimization_outputs/graph-data-{N}.json  → uploaded to Supabase Storage
    ↓ Frontend fetch
Quadtree spatial index → viewport culling → SVG render
```

### Frontend (`src/`)

- **Stores** (`lib/stores/`) — `graph.ts` loads actor/edge data and builds a quadtree; `viewport.ts` tracks pan/zoom state. A derived `visibleCircles` store filters nodes by viewport bounds.
- **Components** — `Graph.svelte` handles mouse/wheel events and renders visible `Circle.svelte` (actor nodes) and `Edge.svelte` (connections on hover).
- **Quadtree** (`lib/utils/quadtree.ts`) — custom spatial index (capacity 4) for O(log n) viewport culling with a 200px buffer.
- **Layout** (`lib/utils/layout.ts`) — Vogel spiral (golden angle ~137.5°) positions actors by ordinal index.

### Python Pipeline (`scripts/`)

3-step optimization minimizing total edge distance on the Vogel spiral:

1. **Random baseline** — fetch actors from Supabase, assign random ordinals
2. **Centrality ordering** — sort by degree, place high-degree actors at center
3. **Swap optimization** — 2-opt swaps with delta recalculation (1000 non-improving attempts → stop)

Shared utilities in `optimization_utils.py`. Each step appends metrics to `OPTIMIZATION_PROGRESS.md`.

### Environment Variables

`VITE_GRAPH_LIMIT` controls actor count. Frontend reads `VITE_DATA_BASE_URL` for pre-generated JSON. Python scripts use `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY`.

## Key Patterns

- **Svelte 5 runes** — uses `$state`, `$derived`, `$effect` (not legacy `$:` reactivity)
- **No CSS framework** — styles are component-scoped in Svelte `<style>` blocks
- **No linter configured** — no ESLint/Prettier setup
- **No test framework** — no tests exist
- **seedrandom** — only runtime dependency, used for reproducible random layouts
