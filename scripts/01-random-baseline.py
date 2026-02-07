#!/usr/bin/env python3
"""
Step 1: Random Baseline

Establishes a baseline by calculating metrics with randomly shuffled ordinal positions.
This gives us a reference point to measure optimization improvements against.

Usage:
    python scripts/01-random-baseline.py
"""

import os
import random
from datetime import datetime

from optimization_utils import (
    get_supabase_client,
    fetch_top_actors,
    fetch_connections,
    deduplicate_edges,
    calculate_vogel_position,
    calculate_metrics,
    save_step_output,
    append_to_progress,
    print_header,
    print_metrics,
)


def main():
    print_header('STEP 1: RANDOM BASELINE')

    # Set random seed for reproducibility (optional - remove for true randomness)
    random.seed(42)

    # Initialize Supabase client
    supabase = get_supabase_client()

    # Fetch top actors (uses VITE_GRAPH_LIMIT from .env)
    actors = fetch_top_actors(supabase, int(os.getenv('VITE_GRAPH_LIMIT', '100')))

    # Create actor ID set and list
    actor_ids = [a['person_id'] for a in actors]
    actor_id_set = set(actor_ids)

    # Fetch and deduplicate connections
    connections = fetch_connections(supabase, actor_ids)
    edges = deduplicate_edges(connections, actor_id_set)

    # Create random ordinal assignment (shuffle positions 0-99)
    ordinal_positions = list(range(len(actors)))
    random.shuffle(ordinal_positions)

    # Assign random ordinals and calculate Vogel positions
    actor_ordinals = {}  # actor_id -> ordinal
    positions = {}  # actor_id -> (x, y)

    for i, actor in enumerate(actors):
        actor_id = actor['person_id']
        ordinal = ordinal_positions[i]
        actor_ordinals[actor_id] = ordinal
        positions[actor_id] = calculate_vogel_position(ordinal)

    # Calculate metrics
    metrics = calculate_metrics(positions, edges)

    # Print results
    print_metrics(metrics, 'Random Baseline Metrics')

    # Save output
    output_data = {
        'step': 'Step 1: Random Baseline',
        'timestamp': datetime.now().isoformat(),
        'config': {
            'num_actors': len(actors),
            'random_seed': 42,
        },
        'metrics': metrics.to_dict(),
        'actors': [
            {
                'person_id': a['person_id'],
                'name': a['name'],
                'recognizability': a['Recognizability'],
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

    save_step_output('01-random-baseline', output_data)

    # Append to progress file
    append_to_progress(
        'Step 1: Random Baseline',
        metrics,
        extra_info={
            'Random seed': 42,
            'Description': 'Baseline with randomly shuffled ordinal positions',
        }
    )

    print_header('STEP 1 COMPLETE')
    print(f'Actors: {len(actors)}')
    print(f'Edges: {len(edges)}')
    print(f'Avg edge distance: {metrics.avg_distance:.2f}')
    print()
    print('Run Step 2 next: python scripts/02-centrality-ordering.py')


if __name__ == '__main__':
    main()
