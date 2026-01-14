#!/usr/bin/env python3
"""
Fair comparison of Simulated Annealing vs Greedy + 2-Opt.

Uses IDENTICAL input data for both algorithms.
"""

import json
import time
import numpy as np
from pathlib import Path
from scipy.optimize import dual_annealing

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / 'optimization-input.json'
OUTPUT_FILE = PROJECT_ROOT / 'algorithm_comparison.json'


def load_data():
    """Load the prepared optimization input."""
    print('Loading optimization input...')
    with open(INPUT_FILE, 'r') as f:
        data = json.load(f)

    actors = data['actors']
    edges = data['edges']
    distance_matrix = np.array(data['distance_matrix'])

    print(f"Loaded: {len(actors)} actors, {len(edges)} edges")
    return actors, edges, distance_matrix


def calculate_objective(permutation, edges, distance_matrix):
    """Calculate total distance for a permutation."""
    total = 0.0
    for i, j in edges:
        pos_i = permutation[i]
        pos_j = permutation[j]
        total += distance_matrix[pos_i, pos_j]
    return total


def simulated_annealing(actors, edges, distance_matrix, max_iterations=5000):
    """Run simulated annealing optimization."""
    print('\n' + '='*70)
    print('ALGORITHM 1: SIMULATED ANNEALING')
    print('='*70)

    num_actors = len(actors)
    edges_array = np.array(edges, dtype=np.int32)

    def objective(permutation_continuous):
        perm = np.argsort(permutation_continuous).astype(np.int32)
        total = 0.0
        for edge in edges_array:
            actor_i, actor_k = edge
            pos_i = perm[actor_i]
            pos_k = perm[actor_k]
            total += distance_matrix[pos_i, pos_k]
        return total

    bounds = [(0, 100)] * num_actors

    print(f'Running simulated annealing (max {max_iterations} iterations)...')
    start_time = time.time()

    result = dual_annealing(
        objective,
        bounds=bounds,
        maxiter=max_iterations,
        initial_temp=5230.0,
        visit=2.62,
        seed=42
    )

    elapsed = time.time() - start_time
    optimal_perm = np.argsort(result.x).astype(int).tolist()

    print(f'Completed in {elapsed:.2f} seconds')
    print(f'Final objective: {result.fun:,.2f}')
    print(f'Iterations: {result.nit}')

    return optimal_perm, result.fun, elapsed


def greedy_solution(actors, edges, distance_matrix):
    """Generate greedy initial solution."""
    num_actors = len(actors)

    # Calculate degree (connection count) for each actor
    degree = {i: 0 for i in range(num_actors)}
    for i, j in edges:
        degree[i] += 1
        degree[j] += 1

    # Sort actors by degree (descending)
    actors_by_degree = sorted(range(num_actors), key=lambda i: degree[i], reverse=True)

    # Sort positions by centrality (distance from origin)
    position_centrality = [distance_matrix[i, 0] for i in range(num_actors)]
    positions_by_centrality = sorted(range(num_actors), key=lambda i: position_centrality[i])

    # Assign: highest degree -> most central position
    permutation = [0] * num_actors
    for actor_rank, actor_idx in enumerate(actors_by_degree):
        permutation[actor_idx] = positions_by_centrality[actor_rank]

    return permutation


def two_opt_local_search(permutation, edges, distance_matrix, max_iterations=10000):
    """Run 2-opt local search."""
    current_perm = permutation.copy()
    num_actors = len(permutation)

    current_obj = calculate_objective(current_perm, edges, distance_matrix)
    iterations = 0
    no_improve_count = 0
    no_improve_limit = 500

    print(f'Running 2-opt refinement (max {max_iterations} iterations)...')
    start_time = time.time()

    while iterations < max_iterations and no_improve_count < no_improve_limit:
        iterations += 1

        # Random swap
        i, j = np.random.choice(num_actors, size=2, replace=False)

        # Calculate delta
        old_contribution = 0.0
        new_contribution = 0.0

        for edge in edges:
            a, b = edge
            pos_a = current_perm[a]
            pos_b = current_perm[b]

            if a == i or a == j or b == i or b == j:
                old_contribution += distance_matrix[pos_a, pos_b]

                new_pos_a = current_perm[j] if a == i else (current_perm[i] if a == j else pos_a)
                new_pos_b = current_perm[j] if b == i else (current_perm[i] if b == j else pos_b)

                new_contribution += distance_matrix[new_pos_a, new_pos_b]

        delta = new_contribution - old_contribution

        if delta < -0.01:
            current_perm[i], current_perm[j] = current_perm[j], current_perm[i]
            current_obj += delta
            no_improve_count = 0
        else:
            no_improve_count += 1

        if iterations % 1000 == 0:
            print(f'\r  Iteration {iterations}: {current_obj:,.2f}', end='', flush=True)

    elapsed = time.time() - start_time
    print(f'\n  Completed in {elapsed:.2f}s')

    return current_perm, current_obj, elapsed, iterations


def greedy_plus_2opt(actors, edges, distance_matrix, max_iterations=10000):
    """Run greedy + 2-opt optimization."""
    print('\n' + '='*70)
    print('ALGORITHM 2: GREEDY + 2-OPT')
    print('='*70)

    # Greedy initial solution
    print('Generating greedy initial solution...')
    greedy_start = time.time()
    greedy_perm = greedy_solution(actors, edges, distance_matrix)
    greedy_obj = calculate_objective(greedy_perm, edges, distance_matrix)
    greedy_time = time.time() - greedy_start

    print(f'Greedy completed in {greedy_time:.3f} seconds')
    print(f'Greedy objective: {greedy_obj:,.2f}')

    # 2-opt refinement
    final_perm, final_obj, twoopt_time, iterations = two_opt_local_search(
        greedy_perm, edges, distance_matrix, max_iterations
    )

    total_time = greedy_time + twoopt_time

    print(f'Final objective: {final_obj:,.2f}')
    print(f'Total time: {total_time:.2f} seconds')

    return final_perm, final_obj, total_time, greedy_obj


def main():
    """Run fair comparison."""
    print('='*70)
    print('FAIR ALGORITHM COMPARISON')
    print('='*70)
    print()

    # Load identical input data
    actors, edges, distance_matrix = load_data()

    # Calculate baseline
    identity_perm = list(range(len(actors)))
    baseline_obj = calculate_objective(identity_perm, edges, distance_matrix)
    baseline_avg = baseline_obj / len(edges)

    print(f'\nBaseline (identity permutation):')
    print(f'  Total distance: {baseline_obj:,.2f}')
    print(f'  Avg per edge: {baseline_avg:.2f}')

    # Run Simulated Annealing
    sa_perm, sa_obj, sa_time = simulated_annealing(actors, edges, distance_matrix)
    sa_improvement = ((baseline_obj - sa_obj) / baseline_obj) * 100
    sa_avg = sa_obj / len(edges)

    # Run Greedy + 2-Opt
    g2_perm, g2_obj, g2_time, greedy_obj = greedy_plus_2opt(actors, edges, distance_matrix)
    g2_improvement = ((baseline_obj - g2_obj) / baseline_obj) * 100
    g2_avg = g2_obj / len(edges)
    greedy_improvement = ((baseline_obj - greedy_obj) / baseline_obj) * 100

    # Print comparison
    print('\n' + '='*70)
    print('COMPARISON RESULTS')
    print('='*70)
    print()
    print(f"{'Metric':<35} | {'SA':<15} | {'Greedy+2Opt':<15}")
    print('-'*70)
    print(f"{'Total Distance':<35} | {sa_obj:>15,.2f} | {g2_obj:>15,.2f}")
    print(f"{'Avg Distance per Edge':<35} | {sa_avg:>15.2f} | {g2_avg:>15.2f}")
    print(f"{'Improvement over Baseline':<35} | {sa_improvement:>14.2f}% | {g2_improvement:>14.2f}%")
    print(f"{'Runtime (seconds)':<35} | {sa_time:>15.2f} | {g2_time:>15.2f}")
    print(f"{'Runtime (minutes)':<35} | {sa_time/60:>15.2f} | {g2_time/60:>15.2f}")
    print()

    # Winner determination
    print('WINNER ANALYSIS:')
    if g2_obj < sa_obj:
        diff = sa_obj - g2_obj
        diff_pct = (diff / sa_obj) * 100
        speedup = sa_time / g2_time
        print(f'  ✓ Greedy+2Opt is BETTER by {diff:,.2f} ({diff_pct:.2f}%)')
        print(f'  ✓ Greedy+2Opt is FASTER by {speedup:.1f}x')
    else:
        diff = g2_obj - sa_obj
        diff_pct = (diff / g2_obj) * 100
        speedup = sa_time / g2_time
        print(f'  ✓ Simulated Annealing is BETTER by {diff:,.2f} ({diff_pct:.2f}%)')
        if speedup > 1:
            print(f'  ✗ But SLOWER by {speedup:.1f}x')

    print()
    print(f'Greedy alone improvement: {greedy_improvement:.2f}%')
    print(f'2-opt refinement added: {g2_improvement - greedy_improvement:.2f}%')

    # Save results
    results = {
        'metadata': {
            'num_actors': len(actors),
            'num_edges': len(edges),
            'baseline_objective': baseline_obj,
            'baseline_avg_per_edge': baseline_avg
        },
        'simulated_annealing': {
            'objective': sa_obj,
            'avg_per_edge': sa_avg,
            'improvement_percent': sa_improvement,
            'runtime_seconds': sa_time,
            'permutation': sa_perm
        },
        'greedy_plus_2opt': {
            'greedy_objective': greedy_obj,
            'greedy_improvement_percent': greedy_improvement,
            'final_objective': g2_obj,
            'avg_per_edge': g2_avg,
            'improvement_percent': g2_improvement,
            'runtime_seconds': g2_time,
            'permutation': g2_perm
        }
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f'\nResults saved to: {OUTPUT_FILE}')
    print('='*70)


if __name__ == '__main__':
    main()
