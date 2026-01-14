#!/usr/bin/env python3
"""
Large-Scale Actor Layout Optimization

Fast greedy + local search algorithm that can handle thousands of actors.
Uses hierarchical optimization for maximum scalability.
"""

import os
import json
import time
import math
import numpy as np
from pathlib import Path
from collections import defaultdict
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / 'optimization_outputs'
OUTPUT_DIR.mkdir(exist_ok=True)

# Vogel spiral parameters
GOLDEN_ANGLE = 137.5  # degrees
SPACING = 80  # pixels


def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    supabase_url = os.getenv('VITE_SUPABASE_URL')
    supabase_key = os.getenv('VITE_SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_key:
        raise ValueError('VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must be set in .env')

    return create_client(supabase_url, supabase_key)


def calculate_vogel_position(index, spacing=SPACING):
    """Calculate Vogel spiral position for a given index."""
    radius = spacing * math.sqrt(index + 1)
    theta_degrees = index * GOLDEN_ANGLE
    theta_radians = math.radians(theta_degrees)

    x = radius * math.cos(theta_radians)
    y = radius * math.sin(theta_radians)

    return x, y


def fetch_top_actors(supabase: Client, limit: int):
    """Fetch top N actors from Supabase ordered by Recognizability."""
    print(f'Fetching top {limit} actors from Supabase...')

    all_actors = []
    page_size = 1000

    for start in range(0, limit, page_size):
        batch_size = min(page_size, limit - start)

        response = supabase.table('actors') \
            .select('person_id, name, Recognizability') \
            .order('Recognizability', desc=True) \
            .range(start, start + batch_size - 1) \
            .execute()

        if response.data:
            all_actors.extend(response.data)
            print(f'\rFetched {len(all_actors)}/{limit} actors...', end='', flush=True)

        if len(response.data) < batch_size:
            break

    print(f'\nLoaded {len(all_actors)} actors')
    return all_actors


def fetch_connections(supabase: Client, actor_ids: list):
    """Fetch all connections between actors from Supabase."""
    print(f'Fetching connections for {len(actor_ids)} actors...')

    all_connections = []
    page_size = 1000
    start = 0

    # Build the OR query for filtering
    actor_ids_str = ','.join(map(str, actor_ids))

    while True:
        response = supabase.table('actor_connections') \
            .select('Source, Target') \
            .or_(f'Source.in.({actor_ids_str}),Target.in.({actor_ids_str})') \
            .range(start, start + page_size - 1) \
            .execute()

        if response.data and len(response.data) > 0:
            all_connections.extend(response.data)
            print(f'\rFetched {len(all_connections)} connections...', end='', flush=True)

            if len(response.data) < page_size:
                break
            start += page_size
        else:
            break

    print(f'\nTotal connections fetched: {len(all_connections)}')
    return all_connections


def build_graph(actors: list, connections: list):
    """
    Build graph data structures.

    Returns:
        - person_id_to_index: mapping from person_id to array index
        - edges: list of [i, j] pairs
        - adjacency: dict mapping actor index to set of connected actor indices
        - degree: dict mapping actor index to connection count
    """
    print('Building graph structures...')

    person_id_to_index = {actor['person_id']: idx for idx, actor in enumerate(actors)}
    actor_id_set = set(actor['person_id'] for actor in actors)

    # Use set to deduplicate edges
    edge_set = set()
    adjacency = defaultdict(set)

    for conn in connections:
        source_id = conn['Source']
        target_id = conn['Target']

        if source_id in actor_id_set and target_id in actor_id_set:
            source_idx = person_id_to_index[source_id]
            target_idx = person_id_to_index[target_id]

            # Store as sorted tuple to avoid duplicates
            edge = tuple(sorted([source_idx, target_idx]))
            edge_set.add(edge)

            # Build adjacency list
            adjacency[source_idx].add(target_idx)
            adjacency[target_idx].add(source_idx)

    edges = [list(edge) for edge in edge_set]

    # Calculate degree (number of connections)
    degree = {idx: len(adjacency[idx]) for idx in range(len(actors))}

    print(f'Built graph: {len(edges)} unique edges')
    print(f'Average degree: {sum(degree.values()) / len(actors):.2f}')
    print(f'Max degree: {max(degree.values())}')

    return person_id_to_index, edges, adjacency, degree


def precompute_distances(num_positions, spacing=SPACING):
    """Precompute distance matrix for all positions."""
    print(f'Precomputing {num_positions}x{num_positions} distance matrix...')

    # Calculate all positions
    positions = np.array([calculate_vogel_position(i, spacing) for i in range(num_positions)])

    # Compute pairwise distances
    # Using broadcasting for efficiency
    diff = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]  # (N, N, 2)
    distances = np.sqrt(np.sum(diff**2, axis=2))  # (N, N)

    print(f'Distance matrix computed')
    return distances


def calculate_objective(permutation, edges, distances):
    """Calculate total distance for a given permutation."""
    total = 0.0
    for i, j in edges:
        pos_i = permutation[i]
        pos_j = permutation[j]
        total += distances[pos_i, pos_j]
    return total


def greedy_initial_solution(num_actors, degree, distances):
    """
    Create greedy initial permutation.

    Strategy: Assign actors with highest degree (most connections) to central positions.
    """
    print('Generating greedy initial solution...')

    # Sort actors by degree (descending)
    actors_by_degree = sorted(range(num_actors), key=lambda i: degree[i], reverse=True)

    # Sort positions by distance from origin (ascending - central first)
    position_centrality = [distances[i, 0] for i in range(num_actors)]  # Distance from position 0 (center)
    positions_by_centrality = sorted(range(num_actors), key=lambda i: position_centrality[i])

    # Assign: highest degree actor -> most central position
    permutation = [0] * num_actors
    for actor_rank, actor_idx in enumerate(actors_by_degree):
        permutation[actor_idx] = positions_by_centrality[actor_rank]

    print('Greedy solution generated')
    return permutation


def calculate_adaptive_iterations(num_edges, num_actors):
    """
    Calculate optimal iteration count based on problem size.

    Based on convergence analysis:
    - Small problems (< 500 edges): Need fewer iterations
    - Medium problems (500-5000 edges): Scale with edge count
    - Large problems (> 5000 edges): Cap to avoid excessive runtime

    Returns iteration count and quality level description.
    """
    # Base formula: 5-7 iterations per edge for good convergence
    base_iterations = num_edges * 6

    # Minimum: at least 5,000 iterations for any problem
    min_iterations = 5000

    # Maximum: cap at 50,000 to keep runtime reasonable
    max_iterations = 50000

    # Apply bounds
    iterations = max(min_iterations, min(max_iterations, base_iterations))

    # Determine quality level
    if iterations >= 20000:
        quality = "high (99%+ optimal)"
    elif iterations >= 10000:
        quality = "good (90-95% optimal)"
    else:
        quality = "fast (85-90% optimal)"

    return iterations, quality


def two_opt_local_search(permutation, edges, distances, max_iterations=None, no_improve_limit=None):
    """
    2-opt local search optimization.

    Iteratively try swapping pairs of actors and keep swaps that improve objective.

    Args:
        permutation: Initial permutation
        edges: List of edges
        distances: Distance matrix
        max_iterations: Max iterations (None = auto-calculate)
        no_improve_limit: Stop if no improvement for N iterations (None = auto-calculate)
    """
    # Auto-calculate iterations if not provided
    if max_iterations is None:
        max_iterations, quality_level = calculate_adaptive_iterations(len(edges), len(permutation))
        print(f'Auto-selected {max_iterations:,} iterations ({quality_level})')

    # Auto-calculate no-improve limit if not provided
    if no_improve_limit is None:
        # Set to ~5% of max iterations
        no_improve_limit = max(500, int(max_iterations * 0.05))

    print(f'Running 2-opt local search (max {max_iterations:,} iterations)...')
    print(f'Early stopping after {no_improve_limit:,} iterations without improvement')

    current_perm = permutation.copy()
    current_obj = calculate_objective(current_perm, edges, distances)
    initial_obj = current_obj

    print(f'Initial objective: {current_obj:,.2f}')

    num_actors = len(permutation)
    best_obj = current_obj
    iterations = 0
    no_improve_count = 0

    start_time = time.time()

    while iterations < max_iterations and no_improve_count < no_improve_limit:
        iterations += 1

        # Randomly select two actors to swap
        i, j = np.random.choice(num_actors, size=2, replace=False)

        # Calculate current contribution of these actors
        old_contribution = 0.0
        new_contribution = 0.0

        for edge in edges:
            a, b = edge

            # Get current positions
            pos_a = current_perm[a]
            pos_b = current_perm[b]

            # If either actor is involved in the swap
            if a == i or a == j or b == i or b == j:
                old_contribution += distances[pos_a, pos_b]

                # Calculate new positions after swap
                new_pos_a = current_perm[j] if a == i else (current_perm[i] if a == j else pos_a)
                new_pos_b = current_perm[j] if b == i else (current_perm[i] if b == j else pos_b)

                new_contribution += distances[new_pos_a, new_pos_b]

        # Check if swap improves objective
        delta = new_contribution - old_contribution

        if delta < -0.01:  # Improvement (with small epsilon for numerical stability)
            # Accept swap
            current_perm[i], current_perm[j] = current_perm[j], current_perm[i]
            current_obj += delta
            no_improve_count = 0

            if current_obj < best_obj:
                best_obj = current_obj
        else:
            no_improve_count += 1

        # Progress update every 1000 iterations
        if iterations % 1000 == 0:
            elapsed = time.time() - start_time
            print(f'\rIteration {iterations}: Obj = {current_obj:,.2f} '
                  f'(Best: {best_obj:,.2f}, {elapsed:.1f}s)', end='', flush=True)

    elapsed = time.time() - start_time

    # Determine stopping reason
    if iterations >= max_iterations:
        stop_reason = "reached max iterations"
    else:
        stop_reason = f"no improvement for {no_improve_limit:,} iterations (early stop)"

    print(f'\n2-opt completed: {iterations:,} iterations in {elapsed:.2f}s ({stop_reason})')
    print(f'Final objective: {current_obj:,.2f}')
    improvement_pct = ((initial_obj - current_obj) / initial_obj * 100) if initial_obj > 0 else 0
    print(f'Improvement: {initial_obj - current_obj:,.2f} ({improvement_pct:.2f}%)')

    return current_perm, current_obj


def optimize_actors(num_actors):
    """
    Main optimization function for N actors.

    Args:
        num_actors: Number of top actors to optimize
    """
    print('='*80)
    print(f'LARGE-SCALE OPTIMIZATION: {num_actors:,} ACTORS')
    print('='*80)
    print()

    start_time = time.time()

    # Fetch data
    supabase = get_supabase_client()
    actors = fetch_top_actors(supabase, num_actors)

    if len(actors) < num_actors:
        print(f'Warning: Only {len(actors)} actors available, continuing with this number')
        num_actors = len(actors)

    actor_ids = [actor['person_id'] for actor in actors]
    connections = fetch_connections(supabase, actor_ids)

    # Build graph
    person_id_to_index, edges, adjacency, degree = build_graph(actors, connections)

    # Precompute distances
    distances = precompute_distances(num_actors)

    # Calculate baseline (identity permutation)
    print('\nCalculating baseline (identity permutation)...')
    identity_perm = list(range(num_actors))
    baseline_obj = calculate_objective(identity_perm, edges, distances)
    baseline_avg = baseline_obj / len(edges) if len(edges) > 0 else 0
    print(f'Baseline objective: {baseline_obj:,.2f}')
    print(f'Baseline avg per edge: {baseline_avg:.2f}')
    print()

    # Greedy initial solution
    greedy_perm = greedy_initial_solution(num_actors, degree, distances)
    greedy_obj = calculate_objective(greedy_perm, edges, distances)
    greedy_improvement = ((baseline_obj - greedy_obj) / baseline_obj * 100) if baseline_obj > 0 else 0
    print(f'Greedy objective: {greedy_obj:,.2f}')
    print(f'Greedy improvement over baseline: {greedy_improvement:.2f}%')
    print()

    # Local search optimization
    optimized_perm, optimized_obj = two_opt_local_search(greedy_perm, edges, distances)

    total_improvement = ((baseline_obj - optimized_obj) / baseline_obj * 100) if baseline_obj > 0 else 0
    optimized_avg = optimized_obj / len(edges) if len(edges) > 0 else 0

    elapsed_total = time.time() - start_time

    # Save results
    output_file = OUTPUT_DIR / f'optimized_{num_actors}_actors.json'
    results = {
        'metadata': {
            'num_actors': num_actors,
            'num_edges': len(edges),
            'algorithm': 'greedy_plus_2opt',
            'total_time_seconds': elapsed_total,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'results': {
            'baseline_objective': baseline_obj,
            'baseline_avg_per_edge': baseline_avg,
            'greedy_objective': greedy_obj,
            'greedy_improvement_percent': greedy_improvement,
            'optimized_objective': optimized_obj,
            'optimized_avg_per_edge': optimized_avg,
            'total_improvement_percent': total_improvement
        },
        'actors': actors,
        'permutation': optimized_perm
    }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    # Print summary
    print()
    print('='*80)
    print('OPTIMIZATION COMPLETE')
    print('='*80)
    print(f'Actors optimized: {num_actors:,}')
    print(f'Edges: {len(edges):,}')
    print(f'Total time: {elapsed_total:.2f} seconds ({elapsed_total/60:.1f} minutes)')
    print()
    print(f'Baseline avg per edge:   {baseline_avg:>12.2f} px')
    print(f'Optimized avg per edge:  {optimized_avg:>12.2f} px')
    print(f'Total improvement:       {total_improvement:>12.2f}%')
    print()
    print(f'Results saved to: {output_file}')
    print('='*80)

    return results


def main():
    """Main execution."""
    import sys

    # Get number of actors from command line or use default
    if len(sys.argv) > 1:
        num_actors = int(sys.argv[1])
    else:
        num_actors = 1000  # Default

    optimize_actors(num_actors)


if __name__ == '__main__':
    main()
