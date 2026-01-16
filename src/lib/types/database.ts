export interface Actor {
  person_id: number;
  name: string;
  Recognizability: number;
  ordinal_100?: number;
  x_100?: number | null;
  y_100?: number | null;
}

export interface Movie {
  movie_id: number;
  title: string;
  original_title: string | null;
  original_language: string | null;
  release_date: string | null;
  runtime: number | null;
  vote_count: number | null;
  vote_average: number | null;
  revenue: number | null;
  budget: number | null;
  adult: boolean;
  genres: string[] | null;
  production_countries: string[] | null;
}

export interface ActorConnection {
  id: number;
  Source: number;
  Target: number;
  movie_id: number;
  movie_title: string;
  release_date: string | null;
}

export interface ActorNode extends Actor {
  radius: number;
}

export interface GraphEdge {
  source: number;
  target: number;
  movieTitle: string;
}
