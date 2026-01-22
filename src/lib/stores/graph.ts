import { writable, derived } from 'svelte/store';
import type { Circle, CircleWithDelay, GraphEdge } from '../types';
import { Quadtree, buildQuadtree } from '../utils/quadtree';
import { getViewportBounds, getViewportCenter, addLoadDelays } from '../utils/culling';
import { viewport } from './viewport';
import { fetchTopActors, fetchActorConnections } from '../services/graphData';
import { getCirclePosition } from '../utils/layout';

interface GraphState {
  allCircles: Circle[];
  edges: GraphEdge[];
  quadtree: Quadtree | null;
  loading: boolean;
  error: string | null;
}

const initialState: GraphState = {
  allCircles: [],
  edges: [],
  quadtree: null,
  loading: false,
  error: null
};

function createGraphStore() {
  const { subscribe, set, update } = writable<GraphState>(initialState);

  async function loadActors(count: number) {
    update(state => ({ ...state, loading: true, error: null }));

    try {
      // Fetch top N actors by ordinal_100
      const actors = await fetchTopActors(count);

      const circles: Circle[] = actors.map((actor, index) => {
        const hasPersisted =
          typeof actor.x_100 === 'number' && typeof actor.y_100 === 'number';
        const positionIndex = actor.ordinal_100 ?? index;
        const position = hasPersisted
          ? { x: actor.x_100 as number, y: actor.y_100 as number }
          : getCirclePosition(positionIndex);

        return {
          id: actor.person_id,
          x: position.x,
          y: position.y,
          radius: actor.radius,
          name: actor.name,
          recognizability: actor.Recognizability
        };
      });

      // Fetch connections between these actors
      const actorIds = actors.map(a => a.person_id);
      const connections = await fetchActorConnections(actorIds);

      // Filter to only include edges between loaded actors and deduplicate
      const actorIdSet = new Set(actorIds);
      const edgeMap = new Map<string, GraphEdge>();

      connections
        .filter(c => actorIdSet.has(c.Source) && actorIdSet.has(c.Target))
        .forEach(c => {
          // Create a unique key for each actor pair (order-independent)
          const key = [c.Source, c.Target].sort((a, b) => a - b).join('-');

          // Only add if we haven't seen this pair before
          if (!edgeMap.has(key)) {
            edgeMap.set(key, {
              source: c.Source,
              target: c.Target,
              movieTitle: c.movie_title
            });
          }
        });

      const edges: GraphEdge[] = Array.from(edgeMap.values());

      const quadtree = buildQuadtree(circles);

      update(state => ({
        ...state,
        allCircles: circles,
        edges,
        quadtree,
        loading: false
      }));
    } catch (error) {
      console.error('Failed to load actors:', error);
      update(state => ({
        ...state,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load data'
      }));
    }
  }

  // Initialize on store creation
  loadActors(parseInt(import.meta.env.VITE_GRAPH_LIMIT));

  return {
    subscribe
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
