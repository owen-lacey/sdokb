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

  console.log('Fetching connections from Supabase...');

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
      process.stdout.write(`\rFetched ${allConnections.length} connections...`);
    } else {
      hasMore = false;
    }
  }

  console.log(`\nTotal connections fetched: ${allConnections.length}`);
  return allConnections;
}

async function main() {
  // Load actors
  const actors = loadActors();
  console.log(`Loaded ${actors.length} actors from CSV\n`);

  // Create mapping from person_id to index
  const personIdToIndex = new Map(actors.map(a => [a.person_id, a.index]));

  // Fetch connections
  const actorIds = actors.map(a => a.person_id);
  const connections = await fetchConnections(actorIds);

  // Build adjacency list (which actors are connected to which)
  const adjacencyList = new Map();
  for (let i = 0; i < actors.length; i++) {
    adjacencyList.set(i, new Set());
  }

  // Only include edges between loaded actors
  const actorIdSet = new Set(actorIds);
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

  // Load distance matrix
  const matrixPath = path.join(__dirname, '..', 'distance-matrix-100.json');
  const distanceMatrix = JSON.parse(fs.readFileSync(matrixPath, 'utf8'));

  console.log('\nCalculating average distances for connected actors...\n');
  console.log('Index | Actor Name                  | Connections | Avg Distance');
  console.log('------|----------------------------|-------------|-------------');

  const results = [];

  for (let i = 0; i < actors.length; i++) {
    const connectedActors = adjacencyList.get(i);

    if (connectedActors.size === 0) {
      console.log(`${String(i).padStart(5)} | ${actors[i].name.substring(0, 25).padEnd(25)} |      0      | N/A (no connections)`);
      continue;
    }

    // Calculate average distance only to connected actors
    let sum = 0;
    for (const connectedIndex of connectedActors) {
      sum += distanceMatrix[i][connectedIndex];
    }

    const average = sum / connectedActors.size;
    results.push({
      index: i,
      name: actors[i].name,
      connections: connectedActors.size,
      average
    });

    console.log(
      `${String(i).padStart(5)} | ${actors[i].name.substring(0, 25).padEnd(25)} | ` +
      `${String(connectedActors.size).padStart(11)} | ${average.toFixed(2)}`
    );
  }

  // Calculate overall statistics
  if (results.length > 0) {
    const averages = results.map(r => r.average);
    const overallAverage = averages.reduce((a, b) => a + b, 0) / averages.length;
    const minAverage = Math.min(...averages);
    const maxAverage = Math.max(...averages);
    const minActor = results.find(r => r.average === minAverage);
    const maxActor = results.find(r => r.average === maxAverage);

    console.log('\n' + '='.repeat(70));
    console.log('SUMMARY STATISTICS');
    console.log('='.repeat(70));
    console.log(`Overall average distance: ${overallAverage.toFixed(2)}`);
    console.log(`Minimum average distance: ${minAverage.toFixed(2)} (${minActor.name} - Actor ${minActor.index})`);
    console.log(`Maximum average distance: ${maxAverage.toFixed(2)} (${maxActor.name} - Actor ${maxActor.index})`);
    console.log(`Range: ${(maxAverage - minAverage).toFixed(2)}`);
  }
}

main().catch(console.error);
