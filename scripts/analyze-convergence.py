#!/usr/bin/env python3
"""
Analyze optimization convergence to determine optimal iteration count.
Creates plots showing objective value vs iterations.
"""

import os
import json
import time
import math
import numpy as np
import matplotlib.pyplot as plt
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
GOLDEN_ANGLE = 137.5
SPACING = 80


def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    supabase_url = os.getenv('VITE_SUPABASE_URL')
    supabase_key = os.getenv('VITE_SUPABASE_ANON_KEY')
    if not supabase_url or not supabase_key:
        raise ValueError('VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must be set')
    return create_client(supabase_url, supabase_key)


def calculate_vogel_position(index, spacing=SPACING):
    """Calculate Vogel spiral position."""
    radius = spacing * math.sqrt(index + 1)
    theta_radians = math.radians(index * GOLDEN_ANGLE)
    return radius * math.cos(theta_radians), radius * math.sin(theta_radians)


def fetch_top_actors(supabase: Client, limit: int):
    """Fetch top N actors."""
    print(f'Fetching top {limit} actors...')
    response = supabase.table('actors') \
        .select('person_id, name, Recognizability') \
        .order('Recognizability', desc=True) \
        .limit(limit) \
        .execute()
    return response.data


def fetch_connections(supabase: Client, actor_ids: list):
    """Fetch connections between actors."""
    print(f'Fetching connections...')
    all_connections = []
    page_size = 1000
    actor_ids_str = ','.join(map(str, actor_ids))

    for start in range(0, 100000, page_size):  # Max 100k connections
        response = supabase.table('actor_connections') \
            .select('Source, Target') \
            .or_(f'Source.in.({actor_ids_str}),Target.in.({actor_ids_str})') \
            .range(start, start + page_size - 1) \
            .execute()

        if response.data:
            all_connections.extend(response.data)
            if len(response.data) < page_size:
                break
        else:
            break

    print(f'Fetched {len(all_connections)} connections')
    return all_connections


def build_graph(actors, connections):
    """Build graph structures."""
    person_id_to_index = {actor['person_id']: idx for idx, actor in enumerate(actors)}
    actor_id_set = set(actor['person_id'] for actor in actors)

    edge_set = set()
    adjacency = defaultdict(set)

    for conn in connections:
        if conn['Source'] in actor_id_set and conn['Target'] in actor_id_set:
            source_idx = person_id_to_index[conn['Source']]
            target_idx = person_id_to_index[conn['Target']]
            edge = tuple(sorted([source_idx, target_idx]))
            edge_set.add(edge)
            adjacency[source_idx].add(target_idx)
            adjacency[target_idx].add(source_idx)

    edges = [list(edge) for edge in edge_set]
    degree = {idx: len(adjacency[idx]) for idx in range(len(actors))}

    return edges, adjacency, degree


def precompute_distances(num_positions):
    """Precompute distance matrix."""
    positions = np.array([calculate_vogel_position(i) for i in range(num_positions)])
    diff = positions[:, np.newaxis, :] - positions[np.newaxis, :, :]
    return np.sqrt(np.sum(diff**2, axis=2))


def calculate_objective(permutation, edges, distances):
    """Calculate total distance."""
    return sum(distances[permutation[i], permutation[j]] for i, j in edges)


def greedy_solution(num_actors, degree, distances):
    """Generate greedy initial solution."""
    actors_by_degree = sorted(range(num_actors), key=lambda i: degree[i], reverse=True)
    position_centrality = [distances[i, 0] for i in range(num_actors)]
    positions_by_centrality = sorted(range(num_actors), key=lambda i: position_centrality[i])

    permutation = [0] * num_actors
    for actor_rank, actor_idx in enumerate(actors_by_degree):
        permutation[actor_idx] = positions_by_centrality[actor_rank]

    return permutation


def two_opt_with_tracking(permutation, edges, distances, max_iterations=50000):
    """
    2-opt with detailed tracking of convergence.

    Returns history of objective values at each iteration.
    """
    print(f'Running 2-opt with convergence tracking...')

    current_perm = permutation.copy()
    num_actors = len(permutation)

    # Track objective value history
    history = []

    # Calculate initial objective
    current_obj = calculate_objective(current_perm, edges, distances)
    history.append(current_obj)

    print(f'Initial objective: {current_obj:,.2f}')

    start_time = time.time()

    for iteration in range(max_iterations):
        # Random swap
        i, j = np.random.choice(num_actors, size=2, replace=False)

        # Calculate delta (change in objective)
        old_contribution = 0.0
        new_contribution = 0.0

        for edge in edges:
            a, b = edge
            pos_a = current_perm[a]
            pos_b = current_perm[b]

            # Only recalculate edges involving swapped actors
            if a == i or a == j or b == i or b == j:
                old_contribution += distances[pos_a, pos_b]

                new_pos_a = current_perm[j] if a == i else (current_perm[i] if a == j else pos_a)
                new_pos_b = current_perm[j] if b == i else (current_perm[i] if b == j else pos_b)

                new_contribution += distances[new_pos_a, new_pos_b]

        delta = new_contribution - old_contribution

        if delta < -0.01:  # Accept improvement
            current_perm[i], current_perm[j] = current_perm[j], current_perm[i]
            current_obj += delta

        # Record every 10 iterations
        if iteration % 10 == 0:
            history.append(current_obj)

        if (iteration + 1) % 1000 == 0:
            elapsed = time.time() - start_time
            print(f'\rIteration {iteration+1}: {current_obj:,.2f} ({elapsed:.1f}s)', end='', flush=True)

    elapsed = time.time() - start_time
    print(f'\nCompleted {max_iterations} iterations in {elapsed:.2f}s')

    return current_perm, history


def plot_convergence(history, num_actors, num_edges, output_file):
    """Create convergence plot."""
    iterations = [i * 10 for i in range(len(history))]  # Recorded every 10 iterations

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    # Plot 1: Full convergence
    ax1.plot(iterations, history, linewidth=2, color='blue', alpha=0.7)
    ax1.set_xlabel('Iteration', fontsize=12)
    ax1.set_ylabel('Objective Value (Total Distance)', fontsize=12)
    ax1.set_title(f'Convergence Curve - {num_actors} Actors, {num_edges} Edges', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # Add improvement annotation
    initial = history[0]
    final = history[-1]
    improvement = ((initial - final) / initial) * 100
    ax1.axhline(y=final, color='green', linestyle='--', alpha=0.5, label=f'Final: {final:,.0f}')
    ax1.axhline(y=initial, color='red', linestyle='--', alpha=0.5, label=f'Initial: {initial:,.0f}')
    ax1.legend()

    # Plot 2: Improvement rate (derivative)
    improvements = [history[i-1] - history[i] for i in range(1, len(history))]
    ax2.plot(iterations[1:], improvements, linewidth=1, color='green', alpha=0.7)
    ax2.set_xlabel('Iteration', fontsize=12)
    ax2.set_ylabel('Improvement per 10 Iterations', fontsize=12)
    ax2.set_title('Rate of Improvement', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)

    plt.tight_layout()
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f'Convergence plot saved to: {output_file}')

    # Print statistics
    print(f'\nConvergence Statistics:')
    print(f'Initial objective: {initial:,.2f}')
    print(f'Final objective: {final:,.2f}')
    print(f'Total improvement: {initial - final:,.2f} ({improvement:.2f}%)')

    # Find when 90%, 95%, 99% of improvement was achieved
    improvement_achieved = [(initial - h) / (initial - final) for h in history]
    for threshold in [0.90, 0.95, 0.99]:
        for idx, achieved in enumerate(improvement_achieved):
            if achieved >= threshold:
                print(f'{threshold*100:.0f}% of improvement achieved at iteration: {idx * 10}')
                break


def main():
    """Main execution."""
    import sys

    num_actors = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    max_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 50000

    print('='*80)
    print(f'CONVERGENCE ANALYSIS: {num_actors} ACTORS')
    print('='*80)
    print()

    # Fetch data
    supabase = get_supabase_client()
    actors = fetch_top_actors(supabase, num_actors)
    connections = fetch_connections(supabase, [a['person_id'] for a in actors])

    # Build graph
    edges, adjacency, degree = build_graph(actors, connections)
    print(f'Graph: {len(edges)} edges, avg degree: {sum(degree.values())/len(actors):.2f}')

    # Precompute distances
    distances = precompute_distances(num_actors)

    # Baseline
    identity_perm = list(range(num_actors))
    baseline_obj = calculate_objective(identity_perm, edges, distances)
    print(f'Baseline: {baseline_obj:,.2f}')

    # Greedy solution
    greedy_perm = greedy_solution(num_actors, degree, distances)
    greedy_obj = calculate_objective(greedy_perm, edges, distances)
    print(f'Greedy: {greedy_obj:,.2f} ({((baseline_obj-greedy_obj)/baseline_obj*100):.2f}% improvement)')
    print()

    # Run 2-opt with tracking
    optimized_perm, history = two_opt_with_tracking(greedy_perm, edges, distances, max_iterations)

    # Plot results
    output_file = OUTPUT_DIR / f'convergence_{num_actors}_actors.png'
    plot_convergence(history, num_actors, len(edges), output_file)


if __name__ == '__main__':
    main()
