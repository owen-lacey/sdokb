import type { Circle, Bounds } from '../types';

export class Quadtree {
  private bounds: Bounds;
  private capacity: number;
  private circles: Circle[] = [];
  private divided: boolean = false;
  private northeast?: Quadtree;
  private northwest?: Quadtree;
  private southeast?: Quadtree;
  private southwest?: Quadtree;

  constructor(bounds: Bounds, capacity: number = 4) {
    this.bounds = bounds;
    this.capacity = capacity;
  }

  insert(circle: Circle): boolean {
    // Ignore circles that don't belong in this quad tree
    if (!this.contains(circle)) {
      return false;
    }

    // If there's space in this quad tree, add the circle here
    if (this.circles.length < this.capacity) {
      this.circles.push(circle);
      return true;
    }

    // Otherwise, subdivide and add the circle to whichever node will accept it
    if (!this.divided) {
      this.subdivide();
    }

    return (
      this.northeast!.insert(circle) ||
      this.northwest!.insert(circle) ||
      this.southeast!.insert(circle) ||
      this.southwest!.insert(circle)
    );
  }

  query(range: Bounds, buffer: number = 0): Circle[] {
    const found: Circle[] = [];

    // Expand the range by the buffer
    const expandedRange: Bounds = {
      x: range.x - buffer,
      y: range.y - buffer,
      width: range.width + buffer * 2,
      height: range.height + buffer * 2
    };

    // If the range doesn't intersect this quad, return empty
    if (!this.intersects(expandedRange)) {
      return found;
    }

    // Check circles in this quad
    for (const circle of this.circles) {
      if (this.rangeContains(expandedRange, circle)) {
        found.push(circle);
      }
    }

    // If subdivided, check children
    if (this.divided) {
      found.push(...this.northeast!.query(range, buffer));
      found.push(...this.northwest!.query(range, buffer));
      found.push(...this.southeast!.query(range, buffer));
      found.push(...this.southwest!.query(range, buffer));
    }

    return found;
  }

  private contains(circle: Circle): boolean {
    return (
      circle.x >= this.bounds.x &&
      circle.x < this.bounds.x + this.bounds.width &&
      circle.y >= this.bounds.y &&
      circle.y < this.bounds.y + this.bounds.height
    );
  }

  private intersects(range: Bounds): boolean {
    return !(
      range.x > this.bounds.x + this.bounds.width ||
      range.x + range.width < this.bounds.x ||
      range.y > this.bounds.y + this.bounds.height ||
      range.y + range.height < this.bounds.y
    );
  }

  private rangeContains(range: Bounds, circle: Circle): boolean {
    return (
      circle.x >= range.x &&
      circle.x < range.x + range.width &&
      circle.y >= range.y &&
      circle.y < range.y + range.height
    );
  }

  private subdivide(): void {
    const x = this.bounds.x;
    const y = this.bounds.y;
    const w = this.bounds.width / 2;
    const h = this.bounds.height / 2;

    this.northeast = new Quadtree({ x: x + w, y: y, width: w, height: h }, this.capacity);
    this.northwest = new Quadtree({ x: x, y: y, width: w, height: h }, this.capacity);
    this.southeast = new Quadtree({ x: x + w, y: y + h, width: w, height: h }, this.capacity);
    this.southwest = new Quadtree({ x: x, y: y + h, width: w, height: h }, this.capacity);

    this.divided = true;
  }
}

export function buildQuadtree(circles: Circle[]): Quadtree {
  // Find the bounds of all circles
  if (circles.length === 0) {
    return new Quadtree({ x: 0, y: 0, width: 1000, height: 1000 });
  }

  let minX = circles[0].x;
  let maxX = circles[0].x;
  let minY = circles[0].y;
  let maxY = circles[0].y;

  for (const circle of circles) {
    minX = Math.min(minX, circle.x - circle.radius);
    maxX = Math.max(maxX, circle.x + circle.radius);
    minY = Math.min(minY, circle.y - circle.radius);
    maxY = Math.max(maxY, circle.y + circle.radius);
  }

  // Add some padding
  const padding = 100;
  const bounds: Bounds = {
    x: minX - padding,
    y: minY - padding,
    width: maxX - minX + padding * 2,
    height: maxY - minY + padding * 2
  };

  const quadtree = new Quadtree(bounds);
  for (const circle of circles) {
    quadtree.insert(circle);
  }

  return quadtree;
}
