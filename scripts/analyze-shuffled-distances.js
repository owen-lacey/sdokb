import { createClient } from '@supabase/supabase-js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize Supabase client
const supabaseUrl = process.env.VITE_SUPABASE_URL;
const supabaseKey = process.env.VITE_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('Error: VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY must be set');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey);

// Fisher-Yates shuffle
function shuffle(array) {
  const shuffled = [...array];
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
  }
  return shuffled;
}

// Read actors CSV to get person_id to index mapping
function loadActors() {
  const csvPath = path.join(__dirname, '..', 'actors_with_positions.csv');
  const csvData = fs.readFileSync(csvPath, 'utf8');
  const lines = csvData.trim().split('\n');

  // Skip header and only take first 100 actors (matching distance matrix size)
  const actors = lines.slice(1, 101).map((line, index) => {
    const [person_id, name] = line.split(',');
    return {
      index,
      person_id: parseInt(person_id),
      name
    };
  });

  return actors;
}

// Fetch connections from Supabase
async function fetchConnections(actorIds) {
  const allConnections = [];
  const pageSize = 1000;
  let start = 0;
  let hasMore = true;

  while (hasMore) {
    const { data, error } = await supabase
      .from('actor_connections')
      .select('Source, Target')
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

async function runAnalysis(actors, connections, distanceMatrix) {
  // Create mapping from person_id to index (shuffled)
  const personIdToIndex = new Map(actors.map((a, idx) => [a.person_id, idx]));

  // Build adjacency list (which actors are connected to which)
  const adjacencyList = new Map();
  for (let i = 0; i < actors.length; i++) {
    adjacencyList.set(i, new Set());
  }

  // Only include edges between loaded actors
  const actorIdSet = new Set(actors.map(a => a.person_id));
  for (const conn of connections) {
    if (actorIdSet.has(conn.Source) && actorIdSet.has(conn.Target)) {
      const sourceIndex = personIdToIndex.get(conn.Source);
      const targetIndex = personIdToIndex.get(conn.Target);

      if (sourceIndex !== undefined && targetIndex !== undefined) {
        adjacencyList.get(sourceIndex).add(targetIndex);
        adjacencyList.get(targetIndex).add(sourceIndex);
      }
    }
  }

  const results = [];

  for (let i = 0; i < actors.length; i++) {
    const connectedActors = adjacencyList.get(i);

    if (connectedActors.size === 0) {
      continue;
    }

    // Calculate average distance only to connected actors
    let sum = 0;
    for (const connectedIndex of connectedActors) {
      sum += distanceMatrix[i][connectedIndex];
    }

    const average = sum / connectedActors.size;
    results.push({ average });
  }

  // Calculate overall average
  const averages = results.map(r => r.average);
  return averages.reduce((a, b) => a + b, 0) / averages.length;
}

async function main() {
  const iterations = parseInt(process.argv[2]) || 10;

  // Load actors
  const baseActors = loadActors();
  console.log(`Running ${iterations} iterations with shuffled positions...\n`);

  // Fetch connections once
  const actorIds = baseActors.map(a => a.person_id);
  const connections = await fetchConnections(actorIds);
  console.log(`Fetched ${connections.length} connections\n`);

  // Load distance matrix
  const matrixPath = path.join(__dirname, '..', 'distance-matrix-100.json');
  const distanceMatrix = JSON.parse(fs.readFileSync(matrixPath, 'utf8'));

  const results = [];

  for (let i = 0; i < iterations; i++) {
    // Shuffle actors (assigns different positions to actors)
    const shuffledActors = shuffle(baseActors);

    const avgDistance = await runAnalysis(shuffledActors, connections, distanceMatrix);
    results.push(avgDistance);

    console.log(`Iteration ${i + 1}: ${avgDistance.toFixed(2)}`);
  }

  console.log('\n' + '='.repeat(50));
  console.log('SUMMARY');
  console.log('='.repeat(50));
  console.log(`Mean: ${(results.reduce((a, b) => a + b, 0) / results.length).toFixed(2)}`);
  console.log(`Min: ${Math.min(...results).toFixed(2)}`);
  console.log(`Max: ${Math.max(...results).toFixed(2)}`);
  console.log(`Range: ${(Math.max(...results) - Math.min(...results)).toFixed(2)}`);
}

main().catch(console.error);
