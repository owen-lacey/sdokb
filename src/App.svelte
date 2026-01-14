<script lang="ts">
  import Graph from './lib/components/Graph.svelte';
</script>

<main>
  <Graph />
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
  }
</style>
