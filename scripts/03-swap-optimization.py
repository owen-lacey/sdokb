#!/usr/bin/env python3
"""
Step 3: Swap Optimization (2-Opt)

Iteratively swaps pairs of nodes to reduce total edge distance.
Stops when no improvement is found for a specified number of consecutive attempts.

Uses efficient delta calculation - only recalculates distances for edges
affected by the swap, not the entire graph.

Usage:
    python scripts/03-swap-optimization.py
"""

import random
import time
from datetime import datetime
from collections import defaultdict

from optimization_utils import (
    calculate_vogel_position,
    calculate_metrics,
    save_step_output,
    load_step_output,
    append_to_progress,
    print_header,
    print_metrics,
    generate_position_sql,
    euclidean_distance,
    Metrics,
)

# Configuration
STAGNATION_THRESHOLD = 1000  # Stop after this many consecutive non-improving swaps
MAX_ITERATIONS = 50000  # Safety limit
RANDOM_SEED = 42  # For reproducibility


def build_adjacency(edges: list[tuple[int, int]]) -> dict[int, set[int]]:
    """
    Build adjacency list from edges.

    Returns dict mapping actor_id to set of connected actor_ids.
    """
    adj = defaultdict(set)
    for source, target in edges:
        adj[source].add(target)
        adj[target].add(source)
    return dict(adj)


def calculate_actor_contribution(
    actor_id: int,
    positions: dict[int, tuple[float, float]],
    adjacency: dict[int, set[int]]
) -> float:
    """
    Calculate total edge distance contribution for a single actor.

    This is the sum of distances to all connected actors.
    """
    if actor_id not in adjacency:
        return 0.0

    x1, y1 = positions[actor_id]
    total = 0.0

    for neighbor_id in adjacency[actor_id]:
        x2, y2 = positions[neighbor_id]
        total += euclidean_distance(x1, y1, x2, y2)

    return total


def try_swap(
    actor_i: int,
    actor_j: int,
    positions: dict[int, tuple[float, float]],
    adjacency: dict[int, set[int]]
) -> float:
    """
    Calculate the change in total distance if we swap positions of actors i and j.

    Returns the delta (negative means improvement).
    """
    # Calculate current contributions
    old_contrib_i = calculate_actor_contribution(actor_i, positions, adjacency)
    old_contrib_j = calculate_actor_contribution(actor_j, positions, adjacency)

    # Handle shared edge (if i and j are connected, it's counted twice)
    shared_edge_adjustment = 0.0
    if actor_j in adjacency.get(actor_i, set()):
        x_i, y_i = positions[actor_i]
        x_j, y_j = positions[actor_j]
        shared_edge_adjustment = euclidean_distance(x_i, y_i, x_j, y_j)

    old_total = old_contrib_i + old_contrib_j - shared_edge_adjustment

    # Temporarily swap positions
    positions[actor_i], positions[actor_j] = positions[actor_j], positions[actor_i]

    # Calculate new contributions
    new_contrib_i = calculate_actor_contribution(actor_i, positions, adjacency)
    new_contrib_j = calculate_actor_contribution(actor_j, positions, adjacency)

    # Handle shared edge again
    if actor_j in adjacency.get(actor_i, set()):
        x_i, y_i = positions[actor_i]
        x_j, y_j = positions[actor_j]
        shared_edge_adjustment = euclidean_distance(x_i, y_i, x_j, y_j)

    new_total = new_contrib_i + new_contrib_j - shared_edge_adjustment

    # Swap back
    positions[actor_i], positions[actor_j] = positions[actor_j], positions[actor_i]

    return new_total - old_total


def run_swap_optimization(
    actors: list[dict],
    edges: list[tuple[int, int]],
    initial_positions: dict[int, tuple[float, float]],
    initial_ordinals: dict[int, int]
) -> tuple[dict[int, tuple[float, float]], dict[int, int], dict]:
    """
    Run the swap optimization algorithm.

    Returns:
        - Final positions dict
        - Final ordinals dict
        - Stats dict with convergence information
    """
    random.seed(RANDOM_SEED)

    # Copy initial state
    positions = dict(initial_positions)
    ordinals = dict(initial_ordinals)

    # Build adjacency list for efficient neighbor lookups
    adjacency = build_adjacency(edges)

    actor_ids = [a['person_id'] for a in actors]

    # Calculate initial total distance
    total_distance = sum(
        euclidean_distance(*positions[e[0]], *positions[e[1]])
        for e in edges
    )

    print(f'Initial total distance: {total_distance:,.2f}')

    # Optimization loop
    stagnation_counter = 0
    iteration = 0
    swaps_accepted = 0
    start_time = time.time()

    while stagnation_counter < STAGNATION_THRESHOLD and iteration < MAX_ITERATIONS:
        iteration += 1

        # Pick two random actors to swap
        actor_i, actor_j = random.sample(actor_ids, 2)

        # Calculate delta
        delta = try_swap(actor_i, actor_j, positions, adjacency)

        if delta < -0.001:  # Improvement (with small epsilon for floating point)
            # Accept swap
            positions[actor_i], positions[actor_j] = positions[actor_j], positions[actor_i]
            ordinals[actor_i], ordinals[actor_j] = ordinals[actor_j], ordinals[actor_i]

            total_distance += delta
            swaps_accepted += 1
            stagnation_counter = 0

            if swaps_accepted % 50 == 0:
                print(f'\rIteration {iteration}: {swaps_accepted} swaps, '
                      f'total distance: {total_distance:,.2f}', end='', flush=True)
        else:
            stagnation_counter += 1

    elapsed_time = time.time() - start_time
    print()  # New line after progress

    stats = {
        'iterations': iteration,
        'swaps_accepted': swaps_accepted,
        'stagnation_threshold': STAGNATION_THRESHOLD,
        'elapsed_seconds': round(elapsed_time, 2),
        'stopped_reason': 'stagnation' if stagnation_counter >= STAGNATION_THRESHOLD else 'max_iterations',
    }

    return positions, ordinals, stats


def main():
    print_header('STEP 3: SWAP OPTIMIZATION')

    # Load Step 2 output
    try:
        step2_data = load_step_output('02-centrality-ordering')
        print(f"Loaded Step 2 output ({len(step2_data['actors'])} actors)")
    except FileNotFoundError:
        print('Error: Step 2 output not found. Run Step 2 first.')
        return

    # Load baseline metrics for comparison
    try:
        baseline_data = load_step_output('01-random-baseline')
        baseline_metrics = Metrics(**baseline_data['metrics'])
    except FileNotFoundError:
        baseline_metrics = None

    # Get previous step metrics
    previous_metrics = Metrics(**step2_data['metrics'])
    print(f'Previous avg distance (Step 2): {previous_metrics.avg_distance:.2f}')

    # Reconstruct actors, edges, positions, and ordinals from Step 2
    actors = step2_data['actors']
    edges = [(e['source'], e['target']) for e in step2_data['edges']]

    initial_positions = {
        a['person_id']: (a['x'], a['y'])
        for a in actors
    }
    initial_ordinals = {
        a['person_id']: a['ordinal']
        for a in actors
    }

    # Run optimization
    print(f'\nRunning swap optimization (stagnation threshold: {STAGNATION_THRESHOLD})...\n')
    final_positions, final_ordinals, stats = run_swap_optimization(
        actors, edges, initial_positions, initial_ordinals
    )

    # Calculate final metrics
    metrics = calculate_metrics(final_positions, edges)

    # Print results
    print_metrics(metrics, 'Swap Optimization Metrics')

    improvement_vs_previous = ((previous_metrics.avg_distance - metrics.avg_distance)
                               / previous_metrics.avg_distance * 100)
    print(f'\nImprovement vs Step 2: {improvement_vs_previous:.1f}%')

    if baseline_metrics:
        improvement_vs_baseline = ((baseline_metrics.avg_distance - metrics.avg_distance)
                                   / baseline_metrics.avg_distance * 100)
        print(f'Improvement vs baseline: {improvement_vs_baseline:.1f}%')

    print(f'\nConvergence stats:')
    print(f'  Iterations: {stats["iterations"]:,}')
    print(f'  Swaps accepted: {stats["swaps_accepted"]:,}')
    print(f'  Time: {stats["elapsed_seconds"]:.2f}s')
    print(f'  Stopped: {stats["stopped_reason"]}')

    # Save output
    output_data = {
        'step': 'Step 3: Swap Optimization',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'num_actors': len(actors),
            'stagnation_threshold': STAGNATION_THRESHOLD,
            'max_iterations': MAX_ITERATIONS,
            'random_seed': RANDOM_SEED,
        },
        'stats': stats,
        'metrics': metrics.to_dict(),
        'actors': [
            {
                'person_id': a['person_id'],
                'name': a['name'],
                'recognizability': a['recognizability'],
                'degree': a['degree'],
                'ordinal': final_ordinals[a['person_id']],
                'x': final_positions[a['person_id']][0],
                'y': final_positions[a['person_id']][1],
            }
            for a in actors
        ],
        'edges': [
            {'source': e[0], 'target': e[1]}
            for e in edges
        ],
    }

    save_step_output('03-swap-optimization', output_data)

    # Generate SQL for Supabase update
    generate_position_sql(
        '03-swap-optimization',
        actors,
        final_positions,
        final_ordinals
    )

    # Append to progress file
    append_to_progress(
        'Step 3: Swap Optimization',
        metrics,
        extra_info={
            'Iterations': f'{stats["iterations"]:,}',
            'Swaps accepted': f'{stats["swaps_accepted"]:,}',
            'Time': f'{stats["elapsed_seconds"]:.2f}s',
            'Stopped': stats['stopped_reason'],
        },
        baseline_metrics=baseline_metrics,
        previous_metrics=previous_metrics,
    )

    print_header('STEP 3 COMPLETE')
    print(f'Actors: {len(actors)}')
    print(f'Edges: {len(edges)}')
    print(f'Avg edge distance: {metrics.avg_distance:.2f}')
    print(f'Improvement vs Step 2: {improvement_vs_previous:.1f}%')
    if baseline_metrics:
        print(f'Improvement vs baseline: {improvement_vs_baseline:.1f}%')
    print()
    print('Run Step 4 next: python scripts/04-force-relaxation.py')


if __name__ == '__main__':
    main()
