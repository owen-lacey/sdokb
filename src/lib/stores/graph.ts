import { writable, derived } from 'svelte/store';
import type { Circle, CircleWithDelay } from '../types';
import { Quadtree, buildQuadtree } from '../utils/quadtree';
import { generateCirclePositions } from '../utils/generator';
import { getViewportBounds, getViewportCenter, addLoadDelays } from '../utils/culling';
import { viewport } from './viewport';

interface GraphState {
  numberOfNodes: number;
  allCircles: Circle[];
  quadtree: Quadtree | null;
}

const initialState: GraphState = {
  numberOfNodes: 100,
  allCircles: [],
  quadtree: null
};

function createGraphStore() {
  const { subscribe, set, update } = writable<GraphState>(initialState);

  // Initialize with default number of nodes
  const circles = generateCirclePositions(100);
  const quadtree = buildQuadtree(circles);
  set({
    numberOfNodes: 100,
    allCircles: circles,
    quadtree
  });

  return {
    subscribe,
    regenerate: (numberOfNodes: number) => {
      const circles = generateCirclePositions(numberOfNodes);
      const quadtree = buildQuadtree(circles);
      set({
        numberOfNodes,
        allCircles: circles,
        quadtree
      });
    }
  };
}

export const graph = createGraphStore();

// Derived store for visible circles with delays
export const visibleCircles = derived(
  [graph, viewport],
  ([$graph, $viewport]) => {
    if (!$graph.quadtree) {
      return [];
    }

    const bounds = getViewportBounds($viewport);
    const buffer = 200; // Load circles 200px outside viewport
    const visible = $graph.quadtree.query(bounds, buffer);
    const center = getViewportCenter($viewport);

    return addLoadDelays(visible, center);
  }
);
