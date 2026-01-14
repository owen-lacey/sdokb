export interface Point {
  x: number;
  y: number;
}

export interface Bounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface Circle {
  id: number;
  x: number;
  y: number;
  radius: number;
  name?: string;
  recognizability?: number;
}

export interface ViewportState {
  x: number;
  y: number;
  zoom: number;
  width: number;
  height: number;
}

export interface CircleWithDelay extends Circle {
  delay: number;
}

export interface GraphEdge {
  source: number;
  target: number;
  movieTitle: string;
}
