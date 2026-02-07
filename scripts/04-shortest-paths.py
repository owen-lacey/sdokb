"""
BFS shortest-path distances from center actors to all other actors.

Processes centers sequentially in the order listed so you can stop at any
time and still have results for the most important actors.  Append new
person_ids to CENTER_ACTOR_IDS to analyze more centers over time.

Usage:
    python scripts/04-shortest-paths.py
"""

import json
import sys
import time
from collections import deque
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GRAPH_PATH = Path("optimization_outputs/graph-data-20000.json")
OUTPUT_PATH = Path("optimization_outputs/shortest-paths.json")

# Centers to analyze, ordered by recognizability / importance.
# Add more person_ids here over time — each run processes them all.
CENTER_ACTOR_IDS: list[int] = [
    4724,       # Kevin Bacon
    112,        # Cate Blanchett
    4491,       # Jennifer Aniston
    4690,       # Christopher Walken
    1327,       # Ian McKellen
    5469,       # Ralph Fiennes
    5472,       # Colin Firth
    7499,       # Jared Leto
    5530,       # James McAvoy
    90633,      # Gal Gadot
    4430,       # Sharon Stone
    1283,       # Helena Bonham Carter
    1920,       # Winona Ryder
    172069,     # Chadwick Boseman
    1190668,    # Timothée Chalamet
]

# ---------------------------------------------------------------------------
# Graph building
# ---------------------------------------------------------------------------

def load_graph(path: Path) -> tuple[dict[int, list[int]], dict[int, str]]:
    """Return (adjacency list, id->name map) from the graph JSON."""
    with open(path) as f:
        data = json.load(f)

    id_to_name: dict[int, str] = {}
    for actor in data["actors"]:
        pid = actor["person_id"]
        id_to_name[pid] = actor["name"]

    adj: dict[int, list[int]] = {pid: [] for pid in id_to_name}
    for edge in data["edges"]:
        s, t = edge["source"], edge["target"]
        if s in adj and t in adj:
            adj[s].append(t)
            adj[t].append(s)

    return adj, id_to_name

# ---------------------------------------------------------------------------
# BFS
# ---------------------------------------------------------------------------

def bfs_distances(adj: dict[int, list[int]], source: int) -> dict[int, int]:
    """BFS from *source*. Returns {node: distance} for all reachable nodes."""
    dist: dict[int, int] = {source: 0}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        d = dist[node]
        for neighbor in adj[node]:
            if neighbor not in dist:
                dist[neighbor] = d + 1
                queue.append(neighbor)
    return dist

# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(name: str, distances: dict[int, int], total_nodes: int) -> None:
    reachable = len(distances) - 1  # exclude the source itself
    unreachable = total_nodes - len(distances)

    # distance distribution
    dist_counts: dict[int, int] = {}
    for d in distances.values():
        if d == 0:
            continue
        dist_counts[d] = dist_counts.get(d, 0) + 1

    max_dist = max(dist_counts) if dist_counts else 0
    total_distance = sum(d * c for d, c in dist_counts.items())
    avg_dist = total_distance / reachable if reachable else 0

    print(f"\n{'=' * 60}")
    print(f"  Center: {name}")
    print(f"  Reachable: {reachable:,}   Unreachable: {unreachable:,}")
    print(f"  Avg distance: {avg_dist:.3f}   Max distance: {max_dist}")
    print(f"  Distance distribution:")
    for d in range(1, max_dist + 1):
        count = dist_counts.get(d, 0)
        bar = "#" * min(count // 40, 60)
        print(f"    {d:3d}: {count:>6,}  {bar}")
    print(f"{'=' * 60}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print(f"Loading graph from {GRAPH_PATH} …")
    adj, id_to_name = load_graph(GRAPH_PATH)
    total_nodes = len(adj)
    print(f"  {total_nodes:,} actors, {sum(len(v) for v in adj.values()) // 2:,} edges\n")

    results: list[dict] = []

    for pid in CENTER_ACTOR_IDS:
        name = id_to_name.get(pid)
        if name is None:
            print(f"⚠ person_id {pid} not found in graph, skipping")
            continue

        t0 = time.perf_counter()
        distances = bfs_distances(adj, pid)
        elapsed = time.perf_counter() - t0

        # Build per-node distance list (None for unreachable)
        full_distances: dict[str, int | None] = {}
        for other_pid in adj:
            if other_pid == pid:
                continue
            d = distances.get(other_pid)
            full_distances[str(other_pid)] = d  # None if unreachable

        reachable = len(distances) - 1
        unreachable = total_nodes - len(distances)

        # Compute stats
        dist_counts: dict[int, int] = {}
        for d in distances.values():
            if d == 0:
                continue
            dist_counts[d] = dist_counts.get(d, 0) + 1

        max_dist = max(dist_counts) if dist_counts else 0
        total_distance = sum(d * c for d, c in dist_counts.items())
        avg_dist = total_distance / reachable if reachable else 0

        results.append({
            "person_id": pid,
            "name": name,
            "reachable": reachable,
            "unreachable": unreachable,
            "avg_distance": round(avg_dist, 4),
            "max_distance": max_dist,
            "distribution": {str(d): dist_counts.get(d, 0) for d in range(1, max_dist + 1)},
            "distances": full_distances,
        })

        print_report(name, distances, total_nodes)
        print(f"  BFS completed in {elapsed:.3f}s")

    # Summary table
    print(f"\n\n{'=' * 72}")
    print(f"  SUMMARY — sorted by max distance (ascending)")
    print(f"{'=' * 72}")
    print(f"  {'Name':<28} {'Avg':>8} {'Max':>5} {'Reachable':>10} {'Unreachable':>12}")
    print(f"  {'-'*28} {'-'*8} {'-'*5} {'-'*10} {'-'*12}")
    for r in sorted(results, key=lambda r: (r["max_distance"], r["avg_distance"])):
        print(f"  {r['name']:<28} {r['avg_distance']:>8.3f} {r['max_distance']:>5} "
              f"{r['reachable']:>10,} {r['unreachable']:>12,}")
    print(f"{'=' * 72}")

    # Write output
    with open(OUTPUT_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nFull results written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
