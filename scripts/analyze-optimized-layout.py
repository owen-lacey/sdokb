#!/usr/bin/env python3
"""
Analyze Optimized Layout

Calculates comprehensive metrics comparing original and optimized layouts.
Validates improvement and generates detailed comparison report.
"""

import json
import csv
import math
from pathlib import Path
from collections import defaultdict

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / 'optimization-input.json'
PERMUTATION_FILE = PROJECT_ROOT / 'optimized-permutation.json'
DISTANCE_MATRIX = PROJECT_ROOT / 'distance-matrix-100.json'
OUTPUT_REPORT = PROJECT_ROOT / 'optimization-results.json'


def load_data():
    """Load all necessary data files."""
    print('Loading data files...')

    with open(INPUT_FILE, 'r') as f:
        input_data = json.load(f)

    with open(PERMUTATION_FILE, 'r') as f:
        perm_data = json.load(f)

    with open(DISTANCE_MATRIX, 'r') as f:
        distance_matrix = json.load(f)

    return input_data, perm_data, distance_matrix


def build_adjacency_list(edges, num_actors):
    """Build adjacency list from edges."""
    adjacency = defaultdict(set)

    for edge in edges:
        actor_i, actor_k = edge
        adjacency[actor_i].add(actor_k)
        adjacency[actor_k].add(actor_i)

    return adjacency


def calculate_layout_metrics(permutation, edges, distance_matrix, adjacency, actors):
    """
    Calculate comprehensive metrics for a given layout permutation.

    Args:
        permutation: Actor-to-position mapping (actor_i -> position_j)
        edges: List of edges
        distance_matrix: Distance matrix
        adjacency: Adjacency list
        actors: Actor data

    Returns:
        Dictionary of metrics
    """
    # Total distance across all edges
    total_distance = 0.0
    for edge in edges:
        actor_i, actor_k = edge
        pos_i = permutation[actor_i]
        pos_k = permutation[actor_k]
        total_distance += distance_matrix[pos_i][pos_k]

    # Average distance per edge
    avg_distance_per_edge = total_distance / len(edges) if len(edges) > 0 else 0

    # Calculate per-actor average distance to costars
    per_actor_averages = []
    actor_details = []

    for actor_idx in range(len(actors)):
        connected_actors = adjacency[actor_idx]

        if len(connected_actors) == 0:
            continue  # Skip actors with no connections

        # Calculate average distance to connected actors
        sum_dist = 0.0
        for connected_idx in connected_actors:
            pos_i = permutation[actor_idx]
            pos_j = permutation[connected_idx]
            sum_dist += distance_matrix[pos_i][pos_j]

        avg_dist = sum_dist / len(connected_actors)
        per_actor_averages.append(avg_dist)

        actor_details.append({
            'index': actor_idx,
            'name': actors[actor_idx]['name'],
            'connections': len(connected_actors),
            'avg_distance': avg_dist
        })

    # Overall average across all actors with connections
    overall_avg = sum(per_actor_averages) / len(per_actor_averages) if per_actor_averages else 0

    # Find extremes
    actor_details_sorted = sorted(actor_details, key=lambda x: x['avg_distance'])
    closest_actors = actor_details_sorted[:5] if len(actor_details_sorted) >= 5 else actor_details_sorted
    furthest_actors = actor_details_sorted[-5:] if len(actor_details_sorted) >= 5 else []
    furthest_actors.reverse()

    return {
        'total_distance': total_distance,
        'avg_distance_per_edge': avg_distance_per_edge,
        'overall_avg_distance': overall_avg,
        'min_avg_distance': min(per_actor_averages) if per_actor_averages else 0,
        'max_avg_distance': max(per_actor_averages) if per_actor_averages else 0,
        'closest_actors': closest_actors,
        'furthest_actors': furthest_actors,
        'num_connected_actors': len(per_actor_averages)
    }


def compare_layouts(original_metrics, optimized_metrics):
    """Calculate comparison statistics between layouts."""
    improvement = {
        'total_distance': {
            'original': original_metrics['total_distance'],
            'optimized': optimized_metrics['total_distance'],
            'difference': original_metrics['total_distance'] - optimized_metrics['total_distance'],
            'percent': ((original_metrics['total_distance'] - optimized_metrics['total_distance']) /
                       original_metrics['total_distance'] * 100)
        },
        'avg_per_edge': {
            'original': original_metrics['avg_distance_per_edge'],
            'optimized': optimized_metrics['avg_distance_per_edge'],
            'difference': original_metrics['avg_distance_per_edge'] - optimized_metrics['avg_distance_per_edge'],
            'percent': ((original_metrics['avg_distance_per_edge'] - optimized_metrics['avg_distance_per_edge']) /
                       original_metrics['avg_distance_per_edge'] * 100)
        },
        'overall_avg': {
            'original': original_metrics['overall_avg_distance'],
            'optimized': optimized_metrics['overall_avg_distance'],
            'difference': original_metrics['overall_avg_distance'] - optimized_metrics['overall_avg_distance'],
            'percent': ((original_metrics['overall_avg_distance'] - optimized_metrics['overall_avg_distance']) /
                       original_metrics['overall_avg_distance'] * 100)
        }
    }

    return improvement


def print_metrics_table(original_metrics, optimized_metrics, improvement):
    """Print formatted comparison table."""
    print()
    print('='*80)
    print('LAYOUT COMPARISON')
    print('='*80)
    print()
    print(f"{'Metric':<30} | {'Original':<15} | {'Optimized':<15} | {'Improvement':<12}")
    print('-'*80)

    # Total distance
    print(f"{'Total Distance':<30} | "
          f"{original_metrics['total_distance']:>15,.2f} | "
          f"{optimized_metrics['total_distance']:>15,.2f} | "
          f"{improvement['total_distance']['percent']:>11.2f}%")

    # Average per edge
    print(f"{'Avg Distance per Edge':<30} | "
          f"{original_metrics['avg_distance_per_edge']:>15.2f} | "
          f"{optimized_metrics['avg_distance_per_edge']:>15.2f} | "
          f"{improvement['avg_per_edge']['percent']:>11.2f}%")

    # Overall average
    print(f"{'Overall Avg (per actor)':<30} | "
          f"{original_metrics['overall_avg_distance']:>15.2f} | "
          f"{optimized_metrics['overall_avg_distance']:>15.2f} | "
          f"{improvement['overall_avg']['percent']:>11.2f}%")

    print()
    print('Range Statistics:')
    print(f"{'Min Avg Distance':<30} | "
          f"{original_metrics['min_avg_distance']:>15.2f} | "
          f"{optimized_metrics['min_avg_distance']:>15.2f}")

    print(f"{'Max Avg Distance':<30} | "
          f"{original_metrics['max_avg_distance']:>15.2f} | "
          f"{optimized_metrics['max_avg_distance']:>15.2f}")


def print_top_actors(actors_list, title):
    """Print table of top actors by average distance."""
    print()
    print(f'{title}:')
    print(f"{'Actor':<30} | {'Connections':<11} | {'Avg Distance':<12}")
    print('-'*60)

    for actor in actors_list:
        print(f"{actor['name'][:29]:<30} | "
              f"{actor['connections']:>11} | "
              f"{actor['avg_distance']:>12.2f}")


def save_results(original_metrics, optimized_metrics, improvement, perm_metadata):
    """Save comprehensive results to JSON file."""
    print(f'\nSaving results to {OUTPUT_REPORT}...')

    results = {
        'metadata': perm_metadata,
        'original_layout': original_metrics,
        'optimized_layout': optimized_metrics,
        'improvement': improvement,
        'success_criteria': {
            'better_than_710px': optimized_metrics['overall_avg_distance'] < 710,
            'better_than_650px': optimized_metrics['overall_avg_distance'] < 650,
            'improvement_gt_10pct': improvement['overall_avg']['percent'] > 10,
            'improvement_gt_20pct': improvement['overall_avg']['percent'] > 20
        }
    }

    with open(OUTPUT_REPORT, 'w') as f:
        json.dump(results, f, indent=2)

    print(f'Results saved to {OUTPUT_REPORT}')


def main():
    """Main execution function."""
    print('='*80)
    print('OPTIMIZED LAYOUT ANALYSIS')
    print('='*80)

    try:
        # Load data
        input_data, perm_data, distance_matrix = load_data()

        actors = input_data['actors']
        edges = input_data['edges']
        optimized_perm = perm_data['optimized_permutation']

        print(f"Loaded {len(actors)} actors and {len(edges)} edges")

        # Build adjacency list
        adjacency = build_adjacency_list(edges, len(actors))

        # Identity permutation (original layout)
        identity_perm = list(range(len(actors)))

        # Calculate metrics for both layouts
        print('\nCalculating metrics for original layout...')
        original_metrics = calculate_layout_metrics(
            identity_perm, edges, distance_matrix, adjacency, actors
        )

        print('Calculating metrics for optimized layout...')
        optimized_metrics = calculate_layout_metrics(
            optimized_perm, edges, distance_matrix, adjacency, actors
        )

        # Compare layouts
        improvement = compare_layouts(original_metrics, optimized_metrics)

        # Print results
        print_metrics_table(original_metrics, optimized_metrics, improvement)

        # Print closest and furthest actors for optimized layout
        print_top_actors(optimized_metrics['closest_actors'], 'Closest to Costars (Optimized)')
        print_top_actors(optimized_metrics['furthest_actors'], 'Furthest from Costars (Optimized)')

        # Success criteria
        print()
        print('='*80)
        print('SUCCESS CRITERIA')
        print('='*80)
        criteria = [
            (optimized_metrics['overall_avg_distance'] < 710,
             f"✓ Average < 710 px: {optimized_metrics['overall_avg_distance']:.2f}",
             f"✗ Average < 710 px: {optimized_metrics['overall_avg_distance']:.2f}"),
            (optimized_metrics['overall_avg_distance'] < 650,
             f"✓ Average < 650 px: {optimized_metrics['overall_avg_distance']:.2f}",
             f"✗ Average < 650 px: {optimized_metrics['overall_avg_distance']:.2f}"),
            (improvement['overall_avg']['percent'] > 10,
             f"✓ Improvement > 10%: {improvement['overall_avg']['percent']:.2f}%",
             f"✗ Improvement > 10%: {improvement['overall_avg']['percent']:.2f}%"),
            (improvement['overall_avg']['percent'] > 20,
             f"✓ Improvement > 20%: {improvement['overall_avg']['percent']:.2f}%",
             f"✗ Improvement > 20%: {improvement['overall_avg']['percent']:.2f}%")
        ]

        for passed, success_msg, fail_msg in criteria:
            print(success_msg if passed else fail_msg)

        # Comparison to baseline from report
        print()
        print('Comparison to Distance Analysis Report:')
        print(f'  Original layout (from report): 739.37 px')
        print(f'  Original layout (calculated):  {original_metrics["overall_avg_distance"]:.2f} px')
        print(f'  Best random shuffle:           710.59 px')
        print(f'  Optimized layout:              {optimized_metrics["overall_avg_distance"]:.2f} px')

        # Save results
        save_results(original_metrics, optimized_metrics, improvement, perm_data['metadata'])

        print()
        print('='*80)
        print('ANALYSIS COMPLETE')
        print('='*80)

    except Exception as e:
        print(f'\nError: {e}')
        raise


if __name__ == '__main__':
    main()
