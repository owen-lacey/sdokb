import type { ActorConnection, ActorNode } from '../types/database';

interface GraphDataJson {
  generated: string;
  actors: {
    person_id: number;
    name: string;
    recognizability: number;
    ordinal: number;
    x: number;
    y: number;
  }[];
  edges: {
    source: number;
    target: number;
  }[];
}

// Cache the data in memory (one fetch per session)
let cachedData: GraphDataJson | null = null;

async function fetchGraphData(): Promise<GraphDataJson> {
  if (cachedData) {
    return cachedData;
  }

  const dataUrl = import.meta.env.VITE_DATA_BASE_URL;
  if (!dataUrl) {
    throw new Error('VITE_DATA_BASE_URL environment variable is not set');
  }
  const graphLimit = import.meta.env.VITE_GRAPH_LIMIT;
  if (!graphLimit) {
    throw new Error('VITE_GRAPH_LIMIT environment variable is not set');
  }

  const response = await fetch(`${dataUrl}/graph-data-${graphLimit}.json`);
  if (!response.ok) {
    throw new Error(`Failed to fetch graph data: ${response.statusText}`);
  }

  cachedData = await response.json();
  return cachedData!;
}

export async function fetchTopActors(limit: number): Promise<ActorNode[]> {
  const data = await fetchGraphData();

  // Sort by ordinal and take the first `limit` actors
  const sortedActors = [...data.actors]
    .sort((a, b) => a.ordinal - b.ordinal)
    .slice(0, limit);

  return sortedActors.map(actor => ({
    person_id: actor.person_id,
    name: actor.name,
    Recognizability: actor.recognizability,
    ordinal_100: actor.ordinal,
    x_100: actor.x,
    y_100: actor.y,
    radius: calculateRadius(actor.recognizability)
  }));
}

export async function fetchActorConnections(actorIds: number[]): Promise<ActorConnection[]> {
  if (actorIds.length === 0) return [];

  const data = await fetchGraphData();
  const actorIdSet = new Set(actorIds);

  // Filter edges to only include those between the specified actors
  // and deduplicate by creating a unique key for each edge
  const seenEdges = new Set<string>();
  const connections: ActorConnection[] = [];

  for (const edge of data.edges) {
    if (actorIdSet.has(edge.source) && actorIdSet.has(edge.target)) {
      // Create a unique key for the edge (sorted to handle bidirectional)
      const key = [edge.source, edge.target].sort((a, b) => a - b).join('-');
      if (!seenEdges.has(key)) {
        seenEdges.add(key);
        connections.push({
          id: connections.length,
          Source: edge.source,
          Target: edge.target,
          movie_id: 0,
          movie_title: '',
          release_date: null
        });
      }
    }
  }

  return connections;
}

function calculateRadius(recognizability: number): number {
  const minRadius = 8;
  const maxRadius = 32;
  // Scale recognizability (0-100) to radius range
  return minRadius + (recognizability / 100) * (maxRadius - minRadius);
}
