<script lang="ts">
  import { createEventDispatcher } from 'svelte';

  interface Props {
    id: number;
    x: number;
    y: number;
    radius: number;
    delay?: number;
    name?: string;
    isHovered?: boolean;
    isDimmed?: boolean;
  }

  let {
    id,
    x,
    y,
    radius,
    delay = 0,
    name,
    isHovered = false,
    isDimmed = false
  }: Props = $props();

  const dispatch = createEventDispatcher<{ hover: number; unhover: void }>();
</script>

<circle
  cx={x}
  cy={y}
  r={radius}
  class="graph-circle"
  class:hovered={isHovered}
  class:dimmed={isDimmed}
  role="button"
  tabindex="0"
  aria-label={name || "Graph node"}
  onmouseenter={() => dispatch('hover', id)}
  onmouseleave={() => dispatch('unhover')}
  onfocus={() => dispatch('hover', id)}
  onblur={() => dispatch('unhover')}
  onclick={() => console.log(name)}
>
  {#if name}
    <title>{name}</title>
  {/if}
</circle>

<style>
  .graph-circle {
    fill: #4a9eff;
    stroke: #2171e8;
    stroke-width: 2;
    cursor: pointer;
    transform-box: fill-box;
    transform-origin: center;
    transition: opacity 120ms ease, filter 120ms ease, stroke-width 120ms ease, transform 120ms ease;
  }

  .graph-circle.hovered {
    fill: #6bb3ff;
    stroke: #3d8aef;
    stroke-width: 3;
    transform: scale(1.2);
    filter: drop-shadow(0 0 8px rgba(74, 158, 255, 0.6));
  }

  .graph-circle.dimmed {
    opacity: 0.25;
  }
</style>
