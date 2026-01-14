<script lang="ts">
  interface Props {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    movieTitle?: string;
    dimmed?: boolean;
  }

  let { x1, y1, x2, y2, movieTitle, dimmed = false }: Props = $props();
</script>

<line
  {x1}
  {y1}
  {x2}
  {y2}
  class="edge"
  class:dimmed={dimmed}
>
  {#if movieTitle}
    <title>{movieTitle}</title>
  {/if}
</line>

<style>
  .edge {
    stroke: #999;
    stroke-width: 1;
    stroke-opacity: 0.6;
    pointer-events: stroke;
    transition: stroke-opacity 120ms ease;
  }

  .edge.dimmed {
    stroke-opacity: 0;
    pointer-events: none;
  }
</style>
