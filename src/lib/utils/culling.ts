import type { Circle, Bounds, Point, ViewportState, CircleWithDelay } from '../types';

export function getViewportBounds(viewport: ViewportState): Bounds {
  // Convert viewport state to bounds for quadtree query
  return {
    x: -viewport.x / viewport.zoom,
    y: -viewport.y / viewport.zoom,
    width: viewport.width / viewport.zoom,
    height: viewport.height / viewport.zoom
  };
}

export function getViewportCenter(viewport: ViewportState): Point {
  const bounds = getViewportBounds(viewport);
  return {
    x: bounds.x + bounds.width / 2,
    y: bounds.y + bounds.height / 2
  };
}

export function calculateLoadDelay(circle: Circle, viewportCenter: Point): number {
  // Calculate distance from circle to viewport center
  const dx = circle.x - viewportCenter.x;
  const dy = circle.y - viewportCenter.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  // Map distance to delay (0-400ms)
  // Closer circles load first
  const maxDelay = 400;
  const maxDistance = 1000; // Distance at which we cap the delay

  const delay = Math.min((distance / maxDistance) * maxDelay, maxDelay);
  return delay;
}

export function addLoadDelays(circles: Circle[], viewportCenter: Point): CircleWithDelay[] {
  return circles.map(circle => ({
    ...circle,
    delay: calculateLoadDelay(circle, viewportCenter)
  }));
}
