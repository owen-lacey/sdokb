#!/usr/bin/env python3
"""
Step 2: Centrality Ordering

Places most highly-connected actors in the center of the Vogel layout.
Actors are sorted by degree (connection count) and assigned ordinal positions
with highest degree actors getting the center positions.

Usage:
    python scripts/02-centrality-ordering.py
"""

from collections import defaultdict
from datetime import datetime

from optimization_utils import (
    get_supabase_client,
    fetch_top_actors,
    fetch_connections,
    deduplicate_edges,
    calculate_vogel_position,
    calculate_metrics,
    save_step_output,
    load_step_output,
    append_to_progress,
    print_header,
    print_metrics,
    Metrics,
)


def calculate_degrees(edges: list[tuple[int, int]], actor_ids: list[int]) -> dict[int, int]:
    """
    Calculate the degree (connection count) for each actor.

    Args:
        edges: List of (actor_id_1, actor_id_2) tuples
        actor_ids: List of all actor IDs

    Returns:
        Dict mapping actor_id to degree
    """
    degree = defaultdict(int)

    # Initialize all actors with 0 degree
    for actor_id in actor_ids:
        degree[actor_id] = 0

    # Count connections
    for source_id, target_id in edges:
        degree[source_id] += 1
        degree[target_id] += 1

    return dict(degree)


def main():
    print_header('STEP 2: CENTRALITY ORDERING')

    # Load baseline metrics for comparison
    try:
        baseline_data = load_step_output('01-random-baseline')
        baseline_metrics = Metrics(**baseline_data['metrics'])
        print(f'Loaded baseline metrics (avg distance: {baseline_metrics.avg_distance:.2f})')
    except FileNotFoundError:
        print('Warning: Could not load baseline metrics from Step 1')
        baseline_metrics = None

    # Initialize Supabase client
    supabase = get_supabase_client()

    # Fetch top 100 actors
    actors = fetch_top_actors(supabase, limit=100)

    # Create actor ID set and list
    actor_ids = [a['person_id'] for a in actors]
    actor_id_set = set(actor_ids)

    # Fetch and deduplicate connections
    connections = fetch_connections(supabase, actor_ids)
    edges = deduplicate_edges(connections, actor_id_set)

    # Calculate degree for each actor
    degrees = calculate_degrees(edges, actor_ids)

    # Sort actors by degree (descending) - highest degree gets center position
    actors_by_degree = sorted(actors, key=lambda a: degrees[a['person_id']], reverse=True)

    # Assign ordinal positions: highest degree -> position 0 (center)
    actor_ordinals = {}  # actor_id -> ordinal
    positions = {}  # actor_id -> (x, y)

    for ordinal, actor in enumerate(actors_by_degree):
        actor_id = actor['person_id']
        actor_ordinals[actor_id] = ordinal
        positions[actor_id] = calculate_vogel_position(ordinal)

    # Calculate metrics
    metrics = calculate_metrics(positions, edges)

    # Print results
    print_metrics(metrics, 'Centrality Ordering Metrics')

    if baseline_metrics:
        improvement = ((baseline_metrics.avg_distance - metrics.avg_distance)
                       / baseline_metrics.avg_distance * 100)
        print(f'\nImprovement vs baseline: {improvement:.1f}%')

    # Print top 10 actors by degree
    print('\nTop 10 actors by degree (connections):')
    print('-' * 50)
    for i, actor in enumerate(actors_by_degree[:10]):
        actor_id = actor['person_id']
        print(f"  {i+1}. {actor['name']}: {degrees[actor_id]} connections")

    # Save output
    output_data = {
        'step': 'Step 2: Centrality Ordering',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'num_actors': len(actors),
            'ordering': 'degree_descending',
        },
        'metrics': metrics.to_dict(),
        'actors': [
            {
                'person_id': a['person_id'],
                'name': a['name'],
                'recognizability': a['Recognizability'],
                'degree': degrees[a['person_id']],
                'ordinal': actor_ordinals[a['person_id']],
                'x': positions[a['person_id']][0],
                'y': positions[a['person_id']][1],
            }
            for a in actors
        ],
        'edges': [
            {'source': e[0], 'target': e[1]}
            for e in edges
        ],
    }

    save_step_output('02-centrality-ordering', output_data)

    # Append to progress file
    append_to_progress(
        'Step 2: Centrality Ordering',
        metrics,
        extra_info={
            'Ordering': 'By degree (connection count), descending',
            'Top actor': f"{actors_by_degree[0]['name']} ({degrees[actors_by_degree[0]['person_id']]} connections)",
        },
        baseline_metrics=baseline_metrics,
    )

    print_header('STEP 2 COMPLETE')
    print(f'Actors: {len(actors)}')
    print(f'Edges: {len(edges)}')
    print(f'Avg edge distance: {metrics.avg_distance:.2f}')
    if baseline_metrics:
        print(f'Improvement vs baseline: {improvement:.1f}%')
    print()
    print('Run Step 3 next: python scripts/03-swap-optimization.py')


if __name__ == '__main__':
    main()
