// Golden angle in degrees: 360° × (1 - 1/φ) where φ is the golden ratio
const GOLDEN_RATIO = (1 + Math.sqrt(5)) / 2;
export const GOLDEN_ANGLE = 360 * (1 - 1 / GOLDEN_RATIO);

// Default spacing - matches original layout
export const DEFAULT_SPACING = 80;

/**
 * Calculate position for a node in a Vogel spiral (phyllotactic pattern)
 * @param index - Index of the node in the sequence (0-based)
 * @param spacing - Controls density of the spiral
 * @returns {x, y} coordinates
 */
export function getCirclePosition(
  index: number,
  spacing: number = DEFAULT_SPACING
): { x: number; y: number } {
  const radius = spacing * Math.sqrt(index + 1);
  const theta = index * GOLDEN_ANGLE;

  const radians = theta * (Math.PI / 180);
  return {
    x: radius * Math.cos(radians),
    y: radius * Math.sin(radians)
  };
}
