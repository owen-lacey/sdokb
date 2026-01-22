#!/usr/bin/env python3
"""
Shared utilities for graph layout optimization scripts.

Provides common functions for:
- Supabase client initialization
- Vogel spiral layout calculation
- Distance calculations
- Metrics computation
- Progress file management
"""

import os
import json
import math
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Constants
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
OUTPUT_DIR = PROJECT_ROOT / 'optimization_outputs'
PROGRESS_FILE = PROJECT_ROOT / 'OPTIMIZATION_PROGRESS.md'

GOLDEN_RATIO = (1 + 5 ** 0.5) / 2
GOLDEN_ANGLE = 360 * (1 - 1 / GOLDEN_RATIO)  # ~137.5 degrees
DEFAULT_SPACING = 80

# Get graph limit from environment (default to 200 if not set)
DEFAULT_GRAPH_LIMIT = int(os.getenv('VITE_GRAPH_LIMIT'))


@dataclass
class Metrics:
    """Standard metrics reported by all optimization steps."""
    edge_count: int
    total_distance: float
    avg_distance: float
    min_distance: float
    max_distance: float

    def to_dict(self) -> dict:
        return {
            'edge_count': self.edge_count,
            'total_distance': round(self.total_distance, 2),
            'avg_distance': round(self.avg_distance, 2),
            'min_distance': round(self.min_distance, 2),
            'max_distance': round(self.max_distance, 2),
        }

    def __str__(self) -> str:
        return (
            f"Edge count: {self.edge_count}\n"
            f"Total distance: {self.total_distance:,.2f}\n"
            f"Avg distance: {self.avg_distance:.2f}\n"
            f"Min distance: {self.min_distance:.2f}\n"
            f"Max distance: {self.max_distance:.2f}"
        )


def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    supabase_url = os.getenv('VITE_SUPABASE_URL')
    supabase_key = os.getenv('VITE_SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_key:
        raise ValueError('VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must be set in .env')

    return create_client(supabase_url, supabase_key)


def calculate_vogel_position(index: int, spacing: float = DEFAULT_SPACING) -> tuple[float, float]:
    """
    Calculate Vogel spiral position for a given index.

    Args:
        index: Position index (0 = center)
        spacing: Base spacing factor (default 80)

    Returns:
        (x, y) coordinates
    """
    radius = spacing * math.sqrt(index + 1)
    theta_degrees = index * GOLDEN_ANGLE
    theta_radians = math.radians(theta_degrees)

    x = radius * math.cos(theta_radians)
    y = radius * math.sin(theta_radians)

    return x, y


def euclidean_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate Euclidean distance between two points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def fetch_top_actors(supabase: Client, limit: Optional[int] = None) -> list[dict]:
    """
    Fetch top actors ordered by Recognizability.

    Args:
        limit: Number of actors to fetch (defaults to VITE_GRAPH_LIMIT from .env)

    Returns list of dicts with: person_id, name, Recognizability
    """
    if limit is None:
        limit = DEFAULT_GRAPH_LIMIT

    print(f'Fetching top {limit} actors...')

    response = supabase.table('actors') \
        .select('person_id, name, Recognizability') \
        .order('Recognizability', desc=True) \
        .limit(limit) \
        .execute()

    if not response.data:
        raise ValueError('No actors returned from database')

    # Filter out any with null Recognizability (shouldn't happen with order, but safe)
    actors = [a for a in response.data if a.get('Recognizability') is not None]

    print(f'Fetched {len(actors)} actors')
    return actors


def fetch_connections(supabase: Client, actor_ids: list[int]) -> list[dict]:
    """
    Fetch all connections between the given actors.

    Returns list of dicts with: Source, Target
    """
    print('Fetching connections...')

    all_connections = []
    page_size = 1000
    start = 0

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

    print()
    return all_connections


def deduplicate_edges(connections: list[dict], actor_id_set: set[int]) -> list[tuple[int, int]]:
    """
    Deduplicate edges so each actor pair counts once.

    Args:
        connections: List of dicts with Source, Target
        actor_id_set: Set of valid actor IDs to include

    Returns:
        List of (source_id, target_id) tuples (sorted, deduplicated)
    """
    edge_set = set()

    for conn in connections:
        source_id = conn['Source']
        target_id = conn['Target']

        # Only include edges between loaded actors
        if source_id in actor_id_set and target_id in actor_id_set:
            # Store as sorted tuple to deduplicate
            edge = tuple(sorted([source_id, target_id]))
            edge_set.add(edge)

    edges = list(edge_set)
    print(f'Deduplicated to {len(edges)} unique edges')
    return edges


def calculate_metrics(
    positions: dict[int, tuple[float, float]],  # actor_id -> (x, y)
    edges: list[tuple[int, int]]  # (actor_id_1, actor_id_2)
) -> Metrics:
    """
    Calculate standard metrics for a given layout.

    Args:
        positions: Dict mapping actor_id to (x, y) coordinates
        edges: List of (actor_id_1, actor_id_2) tuples

    Returns:
        Metrics object with all standard metrics
    """
    if not edges:
        return Metrics(
            edge_count=0,
            total_distance=0.0,
            avg_distance=0.0,
            min_distance=0.0,
            max_distance=0.0
        )

    distances = []
    for source_id, target_id in edges:
        x1, y1 = positions[source_id]
        x2, y2 = positions[target_id]
        dist = euclidean_distance(x1, y1, x2, y2)
        distances.append(dist)

    total = sum(distances)

    return Metrics(
        edge_count=len(edges),
        total_distance=total,
        avg_distance=total / len(edges),
        min_distance=min(distances),
        max_distance=max(distances)
    )


def ensure_output_dir():
    """Ensure the output directory exists."""
    OUTPUT_DIR.mkdir(exist_ok=True)


def save_step_output(step_name: str, data: dict):
    """Save step output to JSON file."""
    ensure_output_dir()
    filename = OUTPUT_DIR / f'{step_name}.json'

    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f'Saved output to {filename}')


def load_step_output(step_name: str) -> dict:
    """Load step output from JSON file."""
    filename = OUTPUT_DIR / f'{step_name}.json'

    if not filename.exists():
        raise FileNotFoundError(f'Step output not found: {filename}')

    with open(filename, 'r') as f:
        return json.load(f)


def append_to_progress(
    step_name: str,
    metrics: Metrics,
    extra_info: Optional[dict] = None,
    baseline_metrics: Optional[Metrics] = None,
    previous_metrics: Optional[Metrics] = None
):
    """
    Append step results to the progress tracking file.

    Args:
        step_name: Name of the step (e.g., "Step 1: Random Baseline")
        metrics: Current step metrics
        extra_info: Optional dict of additional info to include
        baseline_metrics: Metrics from Step 1 for comparison
        previous_metrics: Metrics from previous step for comparison
    """
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Build the content
    lines = [f'\n### {step_name}']
    lines.append(f'*Timestamp: {timestamp}*\n')

    lines.append(f'- Edge count: {metrics.edge_count}')
    lines.append(f'- Total distance: {metrics.total_distance:,.2f}')
    lines.append(f'- Avg distance: {metrics.avg_distance:.2f}')
    lines.append(f'- Min distance: {metrics.min_distance:.2f}')
    lines.append(f'- Max distance: {metrics.max_distance:.2f}')

    # Add comparison to previous step
    if previous_metrics and previous_metrics.avg_distance > 0:
        pct_change = ((metrics.avg_distance - previous_metrics.avg_distance)
                      / previous_metrics.avg_distance * 100)
        arrow = '↓' if pct_change < 0 else '↑'
        lines.append(f'- **vs previous step: {arrow}{abs(pct_change):.1f}%**')

    # Add comparison to baseline
    if baseline_metrics and baseline_metrics.avg_distance > 0:
        pct_change = ((metrics.avg_distance - baseline_metrics.avg_distance)
                      / baseline_metrics.avg_distance * 100)
        arrow = '↓' if pct_change < 0 else '↑'
        lines.append(f'- **vs baseline: {arrow}{abs(pct_change):.1f}%**')

    # Add extra info
    if extra_info:
        lines.append('')
        for key, value in extra_info.items():
            lines.append(f'- {key}: {value}')

    lines.append('')

    content = '\n'.join(lines)

    # Append to file (create with header if needed)
    if not PROGRESS_FILE.exists():
        header = f'# Graph Layout Optimization Progress\n\n## Run: {timestamp}\n'
        with open(PROGRESS_FILE, 'w') as f:
            f.write(header)

    with open(PROGRESS_FILE, 'a') as f:
        f.write(content)

    print(f'Updated {PROGRESS_FILE}')


def print_header(title: str):
    """Print a formatted header."""
    print()
    print('=' * 70)
    print(title)
    print('=' * 70)
    print()


def print_metrics(metrics: Metrics, label: str = 'Metrics'):
    """Print metrics in a formatted way."""
    print(f'\n{label}:')
    print('-' * 40)
    print(metrics)
    print('-' * 40)


def generate_graph_json(
    actors: list[dict],
    edges: list[tuple[int, int]],
    positions: dict[int, tuple[float, float]],
    ordinals: dict[int, int]
) -> str:
    """
    Generate frontend-ready JSON for the graph visualization.

    Args:
        actors: List of actor dicts with person_id, name, recognizability
        edges: List of (source_id, target_id) tuples
        positions: Dict mapping actor_id to (x, y)
        ordinals: Dict mapping actor_id to ordinal

    Returns:
        Path to the saved JSON file
    """
    ensure_output_dir()

    actor_count = len(actors)
    json_filename = OUTPUT_DIR / f'graph-data-{actor_count}.json'

    data = {
        'generated': datetime.now().isoformat(),
        'actors': [
            {
                'person_id': actor['person_id'],
                'name': actor['name'],
                'recognizability': actor.get('recognizability') or actor.get('Recognizability'),
                'ordinal': ordinals[actor['person_id']],
                'x': round(positions[actor['person_id']][0], 2),
                'y': round(positions[actor['person_id']][1], 2),
            }
            for actor in actors
        ],
        'edges': [
            {'source': source, 'target': target}
            for source, target in edges
        ],
    }

    with open(json_filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f'Saved graph data to {json_filename}')
    return str(json_filename)
