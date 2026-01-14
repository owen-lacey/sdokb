<script lang="ts">
  import { scale } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';

  interface Props {
    x: number;
    y: number;
    radius: number;
    delay?: number;
    name?: string;
  }

  let { x, y, radius, delay = 0, name }: Props = $props();

  let hovered = $state(false);
</script>

<circle
  cx={x}
  cy={y}
  r={radius}
  class="graph-circle"
  class:hovered
  role="button"
  tabindex="0"
  aria-label={name || "Graph node"}
  onmouseenter={() => hovered = true}
  onmouseleave={() => hovered = false}
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
  }

  .graph-circle.hovered {
    fill: #6bb3ff;
    stroke: #3d8aef;
    stroke-width: 3;
    filter: drop-shadow(0 0 8px rgba(74, 158, 255, 0.6));
  }
</style>
