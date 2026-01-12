import type { Circle } from '../types';

/**
 * Calculates Euclidean distance between two circles based on their center positions.
 *
 * Uses the standard distance formula: sqrt((x2-x1)² + (y2-y1)²)
 *
 * @param c1 - First circle
 * @param c2 - Second circle
 * @returns Euclidean distance between circle centers
 */
function euclideanDistance(c1: Circle, c2: Circle): number {
	const dx = c2.x - c1.x;
	const dy = c2.y - c1.y;
	return Math.sqrt(dx * dx + dy * dy);
}

/**
 * Creates an n×n distance matrix from an array of circles.
 *
 * The distance matrix is a square matrix where entry [i][j] represents
 * the Euclidean distance from circle i to circle j based on their
 * center positions (x, y coordinates).
 *
 * Matrix properties:
 * - Diagonal entries (i === j) are exactly 0
 * - Matrix is symmetric: distance[i][j] === distance[j][i]
 * - All distances are non-negative
 * - Uses Euclidean distance formula: sqrt((x2-x1)² + (y2-y1)²)
 *
 * Performance characteristics:
 * - Time complexity: O(n²) where n is the number of circles
 * - Space complexity: O(n²)
 * - Optimized to compute only upper triangle and mirror to lower triangle
 *
 * @param circles - Array of Circle objects with x, y coordinates
 * @returns n×n matrix where n = circles.length, or empty array if input is empty
 *
 * @example
 * ```typescript
 * const circles = generateCirclePositions(3);
 * const matrix = createDistanceMatrix(circles);
 *
 * // Access distance from circle 0 to circle 1
 * const dist = matrix[0][1];
 *
 * // Verify symmetry
 * console.assert(matrix[0][1] === matrix[1][0]);
 *
 * // Verify diagonal is zero
 * console.assert(matrix[0][0] === 0);
 * ```
 */
export function createDistanceMatrix(circles: Circle[]): number[][] {
	const n = circles.length;

	// Handle empty input
	if (n === 0) {
		return [];
	}

	// Initialize n×n matrix with zeros
	// Diagonal entries remain 0 (distance from node to itself)
	const matrix: number[][] = Array.from({ length: n }, () => Array(n).fill(0));

	// Compute upper triangle only (j > i) and mirror to lower triangle
	// This optimization reduces computations from n² to n(n-1)/2
	for (let i = 0; i < n; i++) {
		for (let j = i + 1; j < n; j++) {
			const distance = euclideanDistance(circles[i], circles[j]);
			matrix[i][j] = distance;
			matrix[j][i] = distance; // Exploit symmetry
		}
	}

	return matrix;
}
