import { writable } from 'svelte/store';
import type { ViewportState } from '../types';

const initialViewport: ViewportState = {
  x: 0,
  y: 0,
  zoom: 1,
  width: 1000,
  height: 800
};

function createViewportStore() {
  const { subscribe, set, update } = writable<ViewportState>(initialViewport);

  return {
    subscribe,
    pan: (dx: number, dy: number) => {
      update(v => ({
        ...v,
        x: v.x + dx,
        y: v.y + dy
      }));
    },
    zoom: (factor: number, centerX?: number, centerY?: number) => {
      update(v => {
        const newZoom = Math.max(0.25, Math.min(5, v.zoom * factor));

        // If center point provided, zoom towards that point
        if (centerX !== undefined && centerY !== undefined) {
          const zoomRatio = newZoom / v.zoom;
          return {
            ...v,
            zoom: newZoom,
            x: centerX - (centerX - v.x) * zoomRatio,
            y: centerY - (centerY - v.y) * zoomRatio
          };
        }

        return { ...v, zoom: newZoom };
      });
    },
    setSize: (width: number, height: number) => {
      update(v => ({ ...v, width, height }));
    },
    reset: () => {
      set(initialViewport);
    }
  };
}

export const viewport = createViewportStore();
