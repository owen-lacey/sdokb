import { supabase } from '../supabase/client';
import type { Actor, ActorConnection, ActorNode } from '../types/database';

export async function fetchTopActors(limit: number = 100): Promise<ActorNode[]> {
  const allActors: Actor[] = [];
  const pageSize = 1000;
  let remainingLimit = limit;
  let start = 0;

  while (remainingLimit > 0) {
    const currentPageSize = Math.min(pageSize, remainingLimit);

    const { data, error } = await supabase
      .from('actors')
      .select('person_id, name, Recognizability')
      .order('Recognizability', { ascending: false })
      .range(start, start + currentPageSize - 1);

    if (error) throw error;

    if (data && data.length > 0) {
      allActors.push(...data);
      start += data.length;
      remainingLimit -= data.length;

      // If we got less than requested, we've reached the end
      if (data.length < currentPageSize) {
        break;
      }
    } else {
      break;
    }
  }

  return allActors.map(actor => ({
    ...actor,
    radius: calculateRadius(actor.Recognizability)
  }));
}

export async function fetchActorConnections(actorIds: number[]): Promise<ActorConnection[]> {
  if (actorIds.length === 0) return [];

  const allConnections: ActorConnection[] = [];
  const pageSize = 1000;
  let start = 0;
  let hasMore = true;

  while (hasMore) {
    const { data, error } = await supabase
      .from('actor_connections')
      .select('id, Source, Target, movie_id, movie_title, release_date')
      .or('Source.in.(' + actorIds.join(',') + '),Target.in.(' + actorIds.join(',') + ')')
      .range(start, start + pageSize - 1);

    if (error) throw error;

    if (data && data.length > 0) {
      allConnections.push(...data);
      hasMore = data.length === pageSize;
      start += pageSize;
    } else {
      hasMore = false;
    }
  }

  return allConnections;
}

function calculateRadius(recognizability: number): number {
  const minRadius = 8;
  const maxRadius = 32;
  // Scale recognizability (0-100) to radius range
  return minRadius + (recognizability / 100) * (maxRadius - minRadius);
}
