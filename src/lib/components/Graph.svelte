<script lang="ts">
  import { onMount } from 'svelte';
  import { viewport } from '../stores/viewport';
  import { visibleCircles, graph } from '../stores/graph';
  import Circle from './Circle.svelte';
  import Edge from './Edge.svelte';

  let svgElement: SVGSVGElement;
  let containerElement: HTMLDivElement;
  let isDragging = $state(false);
  let dragStart = $state({ x: 0, y: 0 });
  let hoveredCircleId = $state<number | null>(null);

  // Compute visible edges (only show when a node is hovered, and only edges connected to it)
  let visibleEdges = $derived.by(() => {
    if (hoveredCircleId === null) return [];

    const visibleIds = new Set($visibleCircles.map(c => c.id));
    return $graph.edges.filter(e =>
      (e.source === hoveredCircleId || e.target === hoveredCircleId) &&
      (visibleIds.has(e.source) || visibleIds.has(e.target))
    );
  });

  // Create lookup for circle positions
  let circlePositions = $derived.by(() => {
    const map = new Map<number, { x: number; y: number }>();
    $graph.allCircles.forEach(c => map.set(c.id, { x: c.x, y: c.y }));
    return map;
  });

  onMount(() => {
    // Set initial viewport size based on container
    const updateSize = () => {
      if (containerElement) {
        const rect = containerElement.getBoundingClientRect();
        viewport.setSize(rect.width, rect.height);
      }
    };

    updateSize();
    window.addEventListener('resize', updateSize);

    return () => {
      window.removeEventListener('resize', updateSize);
    };
  });

  function handleMouseDown(e: MouseEvent) {
    isDragging = true;
    dragStart = { x: e.clientX, y: e.clientY };
    e.preventDefault();
  }

  function handleMouseMove(e: MouseEvent) {
    if (!isDragging) return;

    const dx = e.clientX - dragStart.x;
    const dy = e.clientY - dragStart.y;

    viewport.pan(dx, dy);
    dragStart = { x: e.clientX, y: e.clientY };
  }

  function handleMouseUp() {
    isDragging = false;
  }

  function handleWheel(e: WheelEvent) {
    e.preventDefault();
    const factor = e.deltaY > 0 ? 0.98 : 1.02;

    // Get mouse position relative to SVG
    const rect = svgElement.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    viewport.zoom(factor, mouseX, mouseY);
  }

  let connectedCircleIds = $derived.by(() => {
    if (hoveredCircleId === null) return null;
    const connected = new Set<number>();
    connected.add(hoveredCircleId);
    for (const edge of $graph.edges) {
      if (edge.source === hoveredCircleId || edge.target === hoveredCircleId) {
        connected.add(edge.source);
        connected.add(edge.target);
      }
    }
    return connected;
  });

</script>

<div
  class="graph-container"
  bind:this={containerElement}
  role="application"
  aria-label="Interactive graph"
>
  <svg
    bind:this={svgElement}
    width="100%"
    height="100%"
    onmousedown={handleMouseDown}
    onmousemove={handleMouseMove}
    onmouseup={handleMouseUp}
    onmouseleave={handleMouseUp}
    onwheel={handleWheel}
    style="cursor: {isDragging ? 'grabbing' : 'grab'}"
  >
    <g
      transform="translate({$viewport.x}, {$viewport.y}) scale({$viewport.zoom})"
      style="will-change: transform"
    >
      <!-- Render edges first (behind circles) -->
      {#each visibleEdges as edge (`${edge.source}-${edge.target}-${edge.movieTitle}`)}
        {@const sourcePos = circlePositions.get(edge.source)}
        {@const targetPos = circlePositions.get(edge.target)}
        {#if sourcePos && targetPos}
          <Edge
            x1={sourcePos.x}
            y1={sourcePos.y}
            x2={targetPos.x}
            y2={targetPos.y}
            movieTitle={edge.movieTitle}
          />
        {/if}
      {/each}

      <!-- Render circles -->
      {#each $visibleCircles as circle (circle.id)}
        <Circle
          id={circle.id}
          x={circle.x}
          y={circle.y}
          radius={circle.radius}
          delay={circle.delay}
          name={circle.name}
          isHovered={hoveredCircleId === circle.id}
          isDimmed={hoveredCircleId !== null && !connectedCircleIds?.has(circle.id)}
          on:hover={(event) => hoveredCircleId = event.detail}
          on:unhover={() => hoveredCircleId = null}
        />
      {/each}
    </g>
  </svg>

  <div class="info-overlay">
    <div>Visible actors: {$visibleCircles.length}</div>
    <div>Visible edges: {visibleEdges.length}</div>
    <div>Zoom: {$viewport.zoom.toFixed(2)}x</div>
    {#if $graph.loading}
      <div class="loading">Loading...</div>
    {/if}
    {#if $graph.error}
      <div class="error">{$graph.error}</div>
    {/if}
  </div>
</div>

<style>
  .graph-container {
    width: 100%;
    height: 100%;
    position: relative;
    overflow: hidden;
    background: linear-gradient(to bottom, #f8f9fa, #e9ecef);
  }

  svg {
    display: block;
    user-select: none;
  }

  .info-overlay {
    position: absolute;
    top: 10px;
    right: 10px;
    background: rgba(255, 255, 255, 0.9);
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 12px;
    font-family: monospace;
    pointer-events: none;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    color: red;
  }

  .info-overlay div {
    margin: 2px 0;
  }

  .loading {
    color: #0066cc;
    font-weight: bold;
  }

  .error {
    color: #dc3545;
    font-weight: bold;
  }
</style>
