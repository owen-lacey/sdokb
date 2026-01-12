import type { Circle } from '../types';

// Golden angle in degrees: 360° × (1 - 1/φ) where φ is the golden ratio
// This produces the optimal divergence angle for phyllotactic spirals
const GOLDEN_RATIO = (1 + Math.sqrt(5)) / 2;
const GOLDEN_ANGLE = 360 * (1 - 1 / GOLDEN_RATIO);

export function generateCirclePositions(numberOfNodes: number): Circle[] {
  const circles: Circle[] = [];

  // Vogel's method (sunflower spiral) - guarantees no overlaps
  const spacing = 80; // Controls how tightly packed the spiral is

  for (let i = 0; i < numberOfNodes; i++) {
    const { x, y } = getCirclePosition(i, spacing);

    // Add some variation to circle sizes
    const radius = 20;

    circles.push({
      id: i,
      x,
      y,
      radius: Math.round(radius)
    });
  }

  return circles;
}

function getCirclePosition(index: number, spacing: number): { x: number; y: number } {
  const radius = spacing * Math.sqrt(index + 1);
  const theta = index * GOLDEN_ANGLE;// Approx 137.5 degrees per node

  // Convert polar to cartesian
  const radians = theta * (Math.PI / 180);
  return {
    x: radius * Math.cos(radians),
    y: radius * Math.sin(radians)
  };
}
