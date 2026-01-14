import pandas as pd
import math

GOLDEN_RATIO = (1 + math.sqrt(5)) / 2
GOLDEN_ANGLE = 360 * (1 - 1 / GOLDEN_RATIO)
SPACING = 80

def get_vogel_position(index, spacing):
    radius = spacing * math.sqrt(index + 1)
    theta = index * GOLDEN_ANGLE
    radians = math.radians(theta)
    return radius * math.cos(radians), radius * math.sin(radians)

# Load actors CSV
actors_df = pd.read_csv('/Users/owen/src/Personal/dgbmc/extract/data/actor_details.csv')

# Sort by recognizability (descending) - most recognizable at center
actors_df = actors_df.sort_values('Recognizability', ascending=False).reset_index(drop=True)

# Calculate positions using Vogel's spiral
positions = [get_vogel_position(i, SPACING) for i in range(len(actors_df))]
actors_df['x'] = [pos[0] for pos in positions]
actors_df['y'] = [pos[1] for pos in positions]

# Save with positions
actors_df.to_csv('actors_with_positions.csv', index=False)
print(f"Processed {len(actors_df)} actors")
