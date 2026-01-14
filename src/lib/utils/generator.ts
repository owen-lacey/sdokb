import type { Circle } from '../types';
import { getCirclePosition, GOLDEN_ANGLE } from './layout';

export function generateCirclePositions(numberOfNodes: number): Circle[] {
  const circles: Circle[] = [];

  for (let i = 0; i < numberOfNodes; i++) {
    const { x, y } = getCirclePosition(i);

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

export { GOLDEN_ANGLE };
