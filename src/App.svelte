<script lang="ts">
  import Graph from './lib/components/Graph.svelte';
  import { graph } from './lib/stores/graph';

  let numberOfNodes = $state(100);
  let inputValue = $state('100');

  function handleRegenerate() {
    const n = parseInt(inputValue, 10);
    if (!isNaN(n) && n > 0 && n <= 20000) {
      numberOfNodes = n;
      graph.regenerate(n);
    }
  }

  function handleKeyPress(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      handleRegenerate();
    }
  }
</script>

<main>
  <div class="controls">
    <div class="control-group">
      <label for="node-count">Number of Nodes:</label>
      <input
        id="node-count"
        type="number"
        bind:value={inputValue}
        min="1"
        max="10000"
        onkeypress={handleKeyPress}
      />
      <button onclick={handleRegenerate}>Regenerate</button>
    </div>
  </div>

  <div class="graph-wrapper">
    <Graph />
  </div>
</main>

<style>
  :global(body) {
    margin: 0;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, sans-serif;
    overflow: hidden;
  }

  main {
    width: 100vw;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .controls {
    background: #2c3e50;
    color: white;
    padding: 12px 20px;
    display: flex;
    gap: 20px;
    align-items: center;
    flex-wrap: wrap;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    z-index: 10;
  }

  .control-group {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  label {
    font-size: 14px;
    font-weight: 500;
  }

  input[type='number'] {
    width: 100px;
    padding: 6px 10px;
    border: 1px solid #34495e;
    border-radius: 4px;
    font-size: 14px;
    background: #34495e;
    color: white;
  }

  input[type='number']:focus {
    outline: none;
    border-color: #4a9eff;
    box-shadow: 0 0 0 2px rgba(74, 158, 255, 0.3);
  }

  button {
    padding: 6px 14px;
    background: #4a9eff;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    cursor: pointer;
    transition: background 0.2s;
    font-weight: 500;
  }

  button:hover {
    background: #3d8aef;
  }

  button:active {
    background: #2171e8;
  }

  .graph-wrapper {
    flex: 1;
    overflow: hidden;
  }

  @media (max-width: 768px) {
    .controls {
      flex-direction: column;
      align-items: stretch;
    }

    .control-group {
      justify-content: space-between;
    }
  }
</style>
