#!/usr/bin/env python3
"""
Data Preparation Script for Actor Layout Optimization

Fetches top 100 actors and their connections from Supabase,
loads the precomputed distance matrix, and prepares data for optimization.
"""

import os
import json
import csv
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
ACTORS_CSV = PROJECT_ROOT / 'actors_with_positions.csv'
DISTANCE_MATRIX = PROJECT_ROOT / 'distance-matrix-100.json'
OUTPUT_FILE = PROJECT_ROOT / 'optimization-input.json'


def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    supabase_url = os.getenv('VITE_SUPABASE_URL')
    supabase_key = os.getenv('VITE_SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_key:
        raise ValueError('VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must be set in .env')

    return create_client(supabase_url, supabase_key)


def load_actors_from_csv():
    """Load actor data from CSV file."""
    print(f'Loading actors from {ACTORS_CSV}...')

    actors = []
    with open(ACTORS_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for index, row in enumerate(reader):
            if index >= 100:  # Only first 100 actors
                break

            actors.append({
                'index': index,
                'person_id': int(row['person_id']),
                'name': row['name'],
                'recognizability': float(row['Recognizability']),
                'x': float(row['x']),
                'y': float(row['y'])
            })

    print(f'Loaded {len(actors)} actors')
    return actors


def fetch_connections(supabase: Client, actor_ids: list) -> list:
    """Fetch all connections between actors from Supabase."""
    print('Fetching connections from Supabase...')

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


def build_edge_list(actors: list, connections: list):
    """
    Build edge list using actor indices.

    Returns:
        - edges: list of [actor_i, actor_k] pairs (using indices 0-99)
        - edge_count: total number of unique edges
    """
    print('Building edge list...')

    # Create mapping from person_id to index
    person_id_to_index = {actor['person_id']: actor['index'] for actor in actors}
    actor_id_set = set(actor['person_id'] for actor in actors)

    # Use a set to deduplicate edges (since connections might be stored both ways)
    edge_set = set()

    for conn in connections:
        source_id = conn['Source']
        target_id = conn['Target']

        # Only include edges between loaded actors
        if source_id in actor_id_set and target_id in actor_id_set:
            source_idx = person_id_to_index[source_id]
            target_idx = person_id_to_index[target_id]

            # Store as sorted tuple to avoid duplicates
            edge = tuple(sorted([source_idx, target_idx]))
            edge_set.add(edge)

    # Convert to list of lists
    edges = [list(edge) for edge in edge_set]

    print(f'Built {len(edges)} unique edges')
    return edges


def load_distance_matrix():
    """Load precomputed distance matrix from JSON file."""
    print(f'Loading distance matrix from {DISTANCE_MATRIX}...')

    with open(DISTANCE_MATRIX, 'r') as f:
        matrix = json.load(f)

    print(f'Loaded {len(matrix)}x{len(matrix[0])} distance matrix')
    return matrix


def save_optimization_input(actors: list, edges: list, distance_matrix: list):
    """Save prepared data to JSON file for optimization."""
    print(f'Saving optimization input to {OUTPUT_FILE}...')

    data = {
        'metadata': {
            'num_actors': len(actors),
            'num_edges': len(edges),
            'description': 'Prepared data for actor layout optimization'
        },
        'actors': actors,
        'edges': edges,
        'distance_matrix': distance_matrix
    }

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print(f'Saved optimization input ({len(actors)} actors, {len(edges)} edges)')


def main():
    """Main execution function."""
    print('='*70)
    print('ACTOR LAYOUT OPTIMIZATION - DATA PREPARATION')
    print('='*70)
    print()

    try:
        # Load actors from CSV
        actors = load_actors_from_csv()

        # Initialize Supabase client
        supabase = get_supabase_client()

        # Fetch connections
        actor_ids = [actor['person_id'] for actor in actors]
        connections = fetch_connections(supabase, actor_ids)

        # Build edge list
        edges = build_edge_list(actors, connections)

        # Load distance matrix
        distance_matrix = load_distance_matrix()

        # Verify dimensions
        if len(distance_matrix) != len(actors):
            raise ValueError(
                f'Distance matrix size ({len(distance_matrix)}) does not match '
                f'number of actors ({len(actors)})'
            )

        # Save prepared data
        save_optimization_input(actors, edges, distance_matrix)

        print()
        print('='*70)
        print('DATA PREPARATION COMPLETE')
        print('='*70)
        print(f'Output file: {OUTPUT_FILE}')
        print(f'Actors: {len(actors)}')
        print(f'Edges: {len(edges)}')
        print(f'Average connections per actor: {2 * len(edges) / len(actors):.1f}')

    except Exception as e:
        print(f'\nError: {e}')
        raise


if __name__ == '__main__':
    main()
