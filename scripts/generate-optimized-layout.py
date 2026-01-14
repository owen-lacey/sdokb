#!/usr/bin/env python3
"""
Generate Optimized Layout

Converts the optimized permutation back to actual (x, y) positions for each actor.
Outputs CSV file with both original and optimized positions.
"""

import json
import csv
from pathlib import Path
import math

# Configuration
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
INPUT_FILE = PROJECT_ROOT / 'optimization-input.json'
PERMUTATION_FILE = PROJECT_ROOT / 'optimized-permutation.json'
OUTPUT_CSV = PROJECT_ROOT / 'actors_optimized_positions.csv'

# Vogel spiral parameters (from layout.ts)
GOLDEN_ANGLE = 137.5  # degrees
SPACING = 80  # pixels


def calculate_vogel_position(index, spacing=SPACING):
    """
    Calculate Vogel spiral position for a given index.

    This replicates the getCirclePosition function from layout.ts

    Args:
        index: Position index (0-99)
        spacing: Spacing parameter (default 80)

    Returns:
        Tuple of (x, y) coordinates
    """
    radius = spacing * math.sqrt(index + 1)
    theta_degrees = index * GOLDEN_ANGLE
    theta_radians = math.radians(theta_degrees)

    x = radius * math.cos(theta_radians)
    y = radius * math.sin(theta_radians)

    return x, y


def load_data():
    """Load actors and optimized permutation."""
    print(f'Loading actors from {INPUT_FILE}...')
    with open(INPUT_FILE, 'r') as f:
        input_data = json.load(f)

    print(f'Loading permutation from {PERMUTATION_FILE}...')
    with open(PERMUTATION_FILE, 'r') as f:
        perm_data = json.load(f)

    return input_data['actors'], perm_data['optimized_permutation']


def generate_optimized_layout(actors, permutation):
    """
    Generate optimized layout by assigning actors to positions via permutation.

    Args:
        actors: List of actor dictionaries with original positions
        permutation: Optimized permutation array (actor_i -> position_j)

    Returns:
        List of actors with both original and optimized positions
    """
    print('Generating optimized layout...')

    # Precompute all Vogel spiral positions
    all_positions = [calculate_vogel_position(i) for i in range(len(actors))]

    # Create result with both original and optimized positions
    result = []

    for actor in actors:
        actor_index = actor['index']
        optimized_position_index = permutation[actor_index]

        # Get optimized position coordinates
        opt_x, opt_y = all_positions[optimized_position_index]

        result.append({
            'person_id': actor['person_id'],
            'name': actor['name'],
            'Recognizability': actor['recognizability'],
            'original_x': actor['x'],
            'original_y': actor['y'],
            'optimized_x': opt_x,
            'optimized_y': opt_y,
            'original_position_index': actor_index,
            'optimized_position_index': optimized_position_index
        })

    print(f'Generated layout for {len(result)} actors')
    return result


def save_to_csv(layout_data):
    """Save layout data to CSV file."""
    print(f'Saving optimized layout to {OUTPUT_CSV}...')

    fieldnames = [
        'person_id', 'name', 'Recognizability',
        'original_x', 'original_y',
        'optimized_x', 'optimized_y',
        'original_position_index', 'optimized_position_index'
    ]

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(layout_data)

    print(f'Saved {len(layout_data)} actors to CSV')


def calculate_movement_statistics(layout_data):
    """Calculate statistics about how much actors moved."""
    print('\nCalculating movement statistics...')

    movements = []
    position_changes = []

    for actor in layout_data:
        # Euclidean distance moved
        dx = actor['optimized_x'] - actor['original_x']
        dy = actor['optimized_y'] - actor['original_y']
        distance = math.sqrt(dx*dx + dy*dy)
        movements.append(distance)

        # Position index change
        pos_change = abs(actor['optimized_position_index'] - actor['original_position_index'])
        position_changes.append(pos_change)

    avg_movement = sum(movements) / len(movements)
    max_movement = max(movements)
    min_movement = min(movements)

    avg_pos_change = sum(position_changes) / len(position_changes)
    max_pos_change = max(position_changes)

    # Count actors that moved significantly
    significant_moves = sum(1 for m in movements if m > 100)

    print(f'Average movement distance: {avg_movement:.2f} px')
    print(f'Max movement distance: {max_movement:.2f} px')
    print(f'Min movement distance: {min_movement:.2f} px')
    print(f'Average position index change: {avg_pos_change:.2f}')
    print(f'Max position index change: {max_pos_change}')
    print(f'Actors moved >100px: {significant_moves}/{len(movements)}')

    return {
        'avg_movement': avg_movement,
        'max_movement': max_movement,
        'min_movement': min_movement,
        'avg_pos_change': avg_pos_change,
        'max_pos_change': max_pos_change,
        'significant_moves': significant_moves
    }


def main():
    """Main execution function."""
    print('='*70)
    print('OPTIMIZED LAYOUT GENERATION')
    print('='*70)
    print()

    try:
        # Load data
        actors, permutation = load_data()

        # Verify permutation
        if len(permutation) != len(actors):
            raise ValueError(
                f'Permutation length ({len(permutation)}) does not match '
                f'number of actors ({len(actors)})'
            )

        # Verify permutation is valid (contains 0-99 exactly once)
        perm_set = set(permutation)
        if perm_set != set(range(len(actors))):
            raise ValueError('Invalid permutation: does not contain 0-99 exactly once')

        # Generate layout
        layout_data = generate_optimized_layout(actors, permutation)

        # Calculate movement statistics
        movement_stats = calculate_movement_statistics(layout_data)

        # Save to CSV
        save_to_csv(layout_data)

        print()
        print('='*70)
        print('LAYOUT GENERATION COMPLETE')
        print('='*70)
        print(f'Output file: {OUTPUT_CSV}')
        print(f'Total actors: {len(layout_data)}')

    except Exception as e:
        print(f'\nError: {e}')
        raise


if __name__ == '__main__':
    main()
