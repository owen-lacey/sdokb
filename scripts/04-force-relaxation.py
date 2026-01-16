#!/usr/bin/env python3
"""
Step 4: Force-Directed Relaxation

Fine-tunes positions using physics simulation:
- Attraction: Connected nodes pull toward each other (edge springs)
- Repulsion: All nodes push apart to maintain minimum distance
- Damping: Gradually reduce movement to converge

Usage:
    python scripts/04-force-relaxation.py
"""

import csv
import time
from datetime import datetime
from collections import defaultdict

from optimization_utils import (
    calculate_metrics,
    save_step_output,
    load_step_output,
    append_to_progress,
    print_header,
    print_metrics,
    euclidean_distance,
    Metrics,
    OUTPUT_DIR,
)

# Configuration (tuned to match relax-layout.py)
MAX_ITERATIONS = 500
STEP_SIZE = 0.02  # Small step multiplier
MAX_STEP = 5.0  # Cap maximum movement per iteration
ATTRACTION_STRENGTH = 0.01  # Spring constant for edges
REPULSION_STRENGTH = 0.5  # Only applied when overlapping
ANCHOR_STRENGTH = 0.02  # Keeps nodes near original positions
MIN_DISTANCE = 60.0  # Minimum distance between nodes
IMPROVEMENT_THRESHOLD = 0.002  # Stop when improvement drops below this
PATIENCE = 15  # Stop after this many iterations without improvement


def build_adjacency(edges: list[tuple[int, int]]) -> dict[int, set[int]]:
    """Build adjacency list from edges."""
    adj = defaultdict(set)
    for source, target in edges:
        adj[source].add(target)
        adj[target].add(source)
    return dict(adj)


def calculate_objective(positions: dict[int, tuple[float, float]], edges: list[tuple[int, int]]) -> float:
    """Calculate total weighted edge distance (objective to minimize)."""
    total = 0.0
    for source, target in edges:
        x1, y1 = positions[source]
        x2, y2 = positions[target]
        total += euclidean_distance(x1, y1, x2, y2)
    return total


def run_force_relaxation(
    actors: list[dict],
    edges: list[tuple[int, int]],
    initial_positions: dict[int, tuple[float, float]]
) -> tuple[dict[int, tuple[float, float]], dict]:
    """
    Run the force-directed relaxation algorithm.

    Uses gentle forces with:
    - Attraction along edges
    - Repulsion only when nodes overlap (< MIN_DISTANCE)
    - Anchor force to keep nodes near original positions
    - Capped step sizes

    Returns:
        - Final positions dict
        - Stats dict with convergence information
    """
    import math

    # Copy initial positions as numpy-like lists
    actor_ids = [a['person_id'] for a in actors]
    positions = {aid: list(initial_positions[aid]) for aid in actor_ids}
    original_positions = {aid: list(initial_positions[aid]) for aid in actor_ids}

    # Build adjacency list
    adjacency = build_adjacency(edges)

    start_time = time.time()
    prev_obj = calculate_objective(positions, edges)
    no_improve = 0

    print(f'Running force relaxation (max {MAX_ITERATIONS} iterations)...')
    print(f'Initial objective: {prev_obj:,.2f}\n')

    for iteration in range(1, MAX_ITERATIONS + 1):
        # Initialize forces
        forces = {aid: [0.0, 0.0] for aid in actor_ids}

        # Attraction along edges
        for source, target in edges:
            x1, y1 = positions[source]
            x2, y2 = positions[target]
            dx = x2 - x1
            dy = y2 - y1
            dist = math.hypot(dx, dy)

            if dist == 0:
                continue

            direction_x = dx / dist
            direction_y = dy / dist
            magnitude = ATTRACTION_STRENGTH * dist

            fx = direction_x * magnitude
            fy = direction_y * magnitude

            forces[source][0] += fx
            forces[source][1] += fy
            forces[target][0] -= fx
            forces[target][1] -= fy

        # Repulsion only when nodes overlap (dist < MIN_DISTANCE)
        for i, actor_i in enumerate(actor_ids):
            x_i, y_i = positions[actor_i]

            for actor_j in actor_ids[i + 1:]:
                x_j, y_j = positions[actor_j]

                dx = x_j - x_i
                dy = y_j - y_i
                dist = math.hypot(dx, dy)

                if dist == 0:
                    direction_x, direction_y = 1.0, 0.0
                    dist = 1e-6
                else:
                    direction_x = dx / dist
                    direction_y = dy / dist

                # Only repel if overlapping
                if dist < MIN_DISTANCE:
                    overlap = MIN_DISTANCE - dist
                    magnitude = REPULSION_STRENGTH * overlap

                    fx = direction_x * magnitude
                    fy = direction_y * magnitude

                    forces[actor_i][0] -= fx
                    forces[actor_i][1] -= fy
                    forces[actor_j][0] += fx
                    forces[actor_j][1] += fy

        # Anchor force to keep near original positions
        for aid in actor_ids:
            forces[aid][0] += ANCHOR_STRENGTH * (original_positions[aid][0] - positions[aid][0])
            forces[aid][1] += ANCHOR_STRENGTH * (original_positions[aid][1] - positions[aid][1])

        # Apply small, capped steps
        max_step_actual = 0.0
        for aid in actor_ids:
            step_x = STEP_SIZE * forces[aid][0]
            step_y = STEP_SIZE * forces[aid][1]
            step_mag = math.hypot(step_x, step_y)

            # Cap step size
            if step_mag > MAX_STEP:
                scale = MAX_STEP / step_mag
                step_x *= scale
                step_y *= scale
                step_mag = MAX_STEP

            positions[aid][0] += step_x
            positions[aid][1] += step_y
            max_step_actual = max(max_step_actual, step_mag)

        # Check convergence
        current_obj = calculate_objective(positions, edges)
        improvement = (prev_obj - current_obj) / prev_obj if prev_obj > 0 else 0.0

        if improvement < IMPROVEMENT_THRESHOLD:
            no_improve += 1
        else:
            no_improve = 0

        if iteration % 10 == 0:
            print(f'Iter {iteration:4d} | obj {current_obj:,.2f} | '
                  f'improve {improvement * 100:5.2f}% | avg step {max_step_actual:.2f}')

        if no_improve >= PATIENCE:
            print(f'\nStopping after {iteration} iterations: '
                  f'improvement < {IMPROVEMENT_THRESHOLD * 100:.2f}% for {PATIENCE} steps.')
            break

        prev_obj = current_obj

    elapsed_time = time.time() - start_time
    final_obj = calculate_objective(positions, edges)

    stats = {
        'iterations': iteration,
        'final_objective': round(final_obj, 2),
        'improvement_from_input': round((calculate_objective(initial_positions, edges) - final_obj)
                                        / calculate_objective(initial_positions, edges) * 100, 2),
        'elapsed_seconds': round(elapsed_time, 2),
        'converged': no_improve >= PATIENCE,
    }

    # Convert positions back to tuples
    final_positions = {k: tuple(v) for k, v in positions.items()}

    return final_positions, stats


def save_positions_csv(actors: list[dict], positions: dict[int, tuple[float, float]]):
    """Save final positions to CSV for database upload."""
    csv_path = OUTPUT_DIR / '04-final-positions.csv'

    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['person_id', 'name', 'x_100', 'y_100'])

        for actor in actors:
            actor_id = actor['person_id']
            x, y = positions[actor_id]
            writer.writerow([actor_id, actor['name'], round(x, 2), round(y, 2)])

    print(f'Saved positions to {csv_path}')


def main():
    print_header('STEP 4: FORCE-DIRECTED RELAXATION')

    # Load Step 3 output
    try:
        step3_data = load_step_output('03-swap-optimization')
        print(f"Loaded Step 3 output ({len(step3_data['actors'])} actors)")
    except FileNotFoundError:
        print('Error: Step 3 output not found. Run Step 3 first.')
        return

    # Load baseline metrics for comparison
    try:
        baseline_data = load_step_output('01-random-baseline')
        baseline_metrics = Metrics(**baseline_data['metrics'])
    except FileNotFoundError:
        baseline_metrics = None

    # Get previous step metrics
    previous_metrics = Metrics(**step3_data['metrics'])
    print(f'Previous avg distance (Step 3): {previous_metrics.avg_distance:.2f}')

    # Reconstruct actors, edges, positions from Step 3
    actors = step3_data['actors']
    edges = [(e['source'], e['target']) for e in step3_data['edges']]

    initial_positions = {
        a['person_id']: (a['x'], a['y'])
        for a in actors
    }

    # Run force relaxation
    final_positions, stats = run_force_relaxation(actors, edges, initial_positions)

    # Calculate final metrics
    metrics = calculate_metrics(final_positions, edges)

    # Print results
    print_metrics(metrics, 'Force Relaxation Metrics')

    improvement_vs_previous = ((previous_metrics.avg_distance - metrics.avg_distance)
                               / previous_metrics.avg_distance * 100)
    print(f'\nImprovement vs Step 3: {improvement_vs_previous:.1f}%')

    if baseline_metrics:
        improvement_vs_baseline = ((baseline_metrics.avg_distance - metrics.avg_distance)
                                   / baseline_metrics.avg_distance * 100)
        print(f'Improvement vs baseline: {improvement_vs_baseline:.1f}%')

    print(f'\nConvergence stats:')
    print(f'  Iterations: {stats["iterations"]}')
    print(f'  Improvement from Step 3 input: {stats["improvement_from_input"]:.1f}%')
    print(f'  Converged: {stats["converged"]}')
    print(f'  Time: {stats["elapsed_seconds"]:.2f}s')

    # Save positions CSV
    save_positions_csv(actors, final_positions)

    # Save output
    output_data = {
        'step': 'Step 4: Force-Directed Relaxation',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'num_actors': len(actors),
            'max_iterations': MAX_ITERATIONS,
            'step_size': STEP_SIZE,
            'max_step': MAX_STEP,
            'attraction_strength': ATTRACTION_STRENGTH,
            'repulsion_strength': REPULSION_STRENGTH,
            'anchor_strength': ANCHOR_STRENGTH,
            'min_distance': MIN_DISTANCE,
            'improvement_threshold': IMPROVEMENT_THRESHOLD,
            'patience': PATIENCE,
        },
        'stats': stats,
        'metrics': metrics.to_dict(),
        'actors': [
            {
                'person_id': a['person_id'],
                'name': a['name'],
                'recognizability': a['recognizability'],
                'degree': a['degree'],
                'ordinal': a['ordinal'],
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

    save_step_output('04-force-relaxation', output_data)

    # Append to progress file
    append_to_progress(
        'Step 4: Force-Directed Relaxation',
        metrics,
        extra_info={
            'Iterations': stats['iterations'],
            'Improvement from Step 3': f'{stats["improvement_from_input"]:.1f}%',
            'Converged': str(stats['converged']),
            'Time': f'{stats["elapsed_seconds"]:.2f}s',
        },
        baseline_metrics=baseline_metrics,
        previous_metrics=previous_metrics,
    )

    print_header('STEP 4 COMPLETE')
    print(f'Actors: {len(actors)}')
    print(f'Edges: {len(edges)}')
    print(f'Avg edge distance: {metrics.avg_distance:.2f}')
    print(f'Improvement vs Step 3: {improvement_vs_previous:.1f}%')
    if baseline_metrics:
        print(f'Improvement vs baseline: {improvement_vs_baseline:.1f}%')
    print()
    print(f'Final positions saved to: {OUTPUT_DIR / "04-final-positions.csv"}')
    print()
    print('All optimization steps complete!')
    print('To upload positions to database, use the CSV file above.')


if __name__ == '__main__':
    main()
