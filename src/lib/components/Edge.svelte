<script lang="ts">
  interface Props {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    movieTitle?: string;
  }

  let { x1, y1, x2, y2, movieTitle }: Props = $props();
</script>

<line
  {x1}
  {y1}
  {x2}
  {y2}
  class="edge"
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
  }
</style>
