<script lang="ts">
  import { onMount } from 'svelte';
  import { viewport } from '../stores/viewport';
  import { visibleCircles } from '../stores/graph';
  import Circle from './Circle.svelte';

  let svgElement: SVGSVGElement;
  let containerElement: HTMLDivElement;
  let isDragging = $state(false);
  let dragStart = $state({ x: 0, y: 0 });

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
      {#each $visibleCircles as circle (circle.id)}
        <Circle
          x={circle.x}
          y={circle.y}
          radius={circle.radius}
          delay={circle.delay}
        />
      {/each}
    </g>
  </svg>

  <div class="info-overlay">
    <div>Visible circles: {$visibleCircles.length}</div>
    <div>Zoom: {$viewport.zoom.toFixed(2)}x</div>
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
</style>
