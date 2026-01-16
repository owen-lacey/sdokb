#!/usr/bin/env python3
"""
Gentle force-directed layout relaxation.

Clusters highly connected nodes with small steps, keeps positions close to the
original layout, and enforces a minimum distance to avoid clutter.
"""

import argparse
import csv
import json
import math
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from supabase import create_client, Client

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Load environment variables
load_dotenv()


def load_input(input_path: Path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    actors = data["actors"]
    edges = data["edges"]
    return actors, edges


def normalize_recognizability(actors):
    values = [
        float(actor.get("recognizability", actor.get("Recognizability", 0.0)))
        for actor in actors
    ]
    min_val = min(values)
    max_val = max(values)

    if max_val <= min_val:
        return [0.5 for _ in values]

    scale = max_val - min_val
    return [(value - min_val) / scale for value in values]


def compute_edge_weights(edges, normalized_recog, weight_scale):
    weights = []
    for i, j in edges:
        avg_recog = (normalized_recog[i] + normalized_recog[j]) / 2.0
        weights.append(1.0 + weight_scale * avg_recog)
    return np.array(weights, dtype=float)


def objective(positions, edges, weights):
    total = 0.0
    for (i, j), weight in zip(edges, weights):
        dx = positions[j, 0] - positions[i, 0]
        dy = positions[j, 1] - positions[i, 1]
        total += weight * math.hypot(dx, dy)
    return total


def get_supabase_client() -> Client:
    """Initialize and return Supabase client."""
    supabase_url = os.getenv("VITE_SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("VITE_SUPABASE_ANON_KEY")

    if not supabase_url or not supabase_key:
        raise ValueError(
            "VITE_SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or VITE_SUPABASE_ANON_KEY) "
            "must be set in .env"
        )

    return create_client(supabase_url, supabase_key)


def upsert_positions(
    supabase: Client,
    actors,
    positions,
    table,
    id_column,
    x_column,
    y_column,
    batch_size,
):
    """Update relaxed positions into Supabase."""
    rows = []
    for actor, pos in zip(actors, positions):
        rows.append(
            {
                id_column: actor["person_id"],
                x_column: float(pos[0]),
                y_column: float(pos[1]),
            }
        )

    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        for row in batch:
            actor_id = row[id_column]
            update_payload = {x_column: row[x_column], y_column: row[y_column]}
            supabase.table(table).update(update_payload).eq(id_column, actor_id).execute()
        print(f"Updated {start + len(batch)}/{len(rows)} rows...")


def relax_layout(
    positions,
    edges,
    weights,
    min_distance,
    step_size,
    max_step,
    attraction_strength,
    repulsion_strength,
    anchor_strength,
    max_iterations,
    improvement_threshold,
    patience,
    report_every,
):
    num_nodes = positions.shape[0]
    original_positions = positions.copy()
    prev_obj = objective(positions, edges, weights)
    no_improve = 0

    for iteration in range(1, max_iterations + 1):
        forces = np.zeros_like(positions)

        # Attraction along edges
        for (i, j), weight in zip(edges, weights):
            dx = positions[j, 0] - positions[i, 0]
            dy = positions[j, 1] - positions[i, 1]
            dist = math.hypot(dx, dy)
            if dist == 0.0:
                continue
            direction_x = dx / dist
            direction_y = dy / dist
            magnitude = attraction_strength * weight * dist
            fx = direction_x * magnitude
            fy = direction_y * magnitude
            forces[i, 0] += fx
            forces[i, 1] += fy
            forces[j, 0] -= fx
            forces[j, 1] -= fy

        # Repulsion to enforce minimum distance
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                dx = positions[j, 0] - positions[i, 0]
                dy = positions[j, 1] - positions[i, 1]
                dist = math.hypot(dx, dy)
                if dist == 0.0:
                    direction_x, direction_y = 1.0, 0.0
                    dist = 1e-6
                else:
                    direction_x = dx / dist
                    direction_y = dy / dist

                if dist < min_distance:
                    overlap = min_distance - dist
                    magnitude = repulsion_strength * overlap
                    fx = direction_x * magnitude
                    fy = direction_y * magnitude
                    forces[i, 0] -= fx
                    forces[i, 1] -= fy
                    forces[j, 0] += fx
                    forces[j, 1] += fy

        # Anchor to original positions to avoid large shifts
        forces += anchor_strength * (original_positions - positions)

        # Apply small, capped steps
        steps = step_size * forces
        step_mags = np.linalg.norm(steps, axis=1)
        too_large = step_mags > max_step
        if np.any(too_large):
            steps[too_large] *= (max_step / step_mags[too_large])[:, None]
        positions += steps

        current_obj = objective(positions, edges, weights)
        improvement = (prev_obj - current_obj) / prev_obj if prev_obj > 0 else 0.0

        if improvement < improvement_threshold:
            no_improve += 1
        else:
            no_improve = 0

        if report_every and iteration % report_every == 0:
            avg_step = float(np.mean(step_mags))
            print(
                f"Iter {iteration:4d} | obj {current_obj:,.2f} | "
                f"improve {improvement * 100:5.2f}% | avg step {avg_step:5.2f}"
            )

        if no_improve >= patience:
            print(
                f"Stopping after {iteration} iterations: "
                f"improvement < {improvement_threshold * 100:.2f}% for {patience} steps."
            )
            break

        prev_obj = current_obj

    return positions


def save_positions(output_path, actors, original_positions, positions):
    fieldnames = [
        "person_id",
        "name",
        "Recognizability",
        "original_x",
        "original_y",
        "relaxed_x",
        "relaxed_y",
    ]
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for actor, original_pos, pos in zip(actors, original_positions, positions):
            writer.writerow(
                {
                    "person_id": actor["person_id"],
                    "name": actor["name"],
                    "Recognizability": actor.get(
                        "recognizability", actor.get("Recognizability", 0.0)
                    ),
                    "original_x": float(original_pos[0]),
                    "original_y": float(original_pos[1]),
                    "relaxed_x": float(pos[0]),
                    "relaxed_y": float(pos[1]),
                }
            )


def build_parser():
    parser = argparse.ArgumentParser(
        description="Gently relax actor layout with small steps and min distance."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=PROJECT_ROOT / "optimization-input.json",
        help="Input JSON with actors and edges.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "actors_relaxed_positions.csv",
        help="Output CSV with relaxed positions.",
    )
    parser.add_argument("--min-distance", type=float, default=60.0)
    parser.add_argument("--step-size", type=float, default=0.02)
    parser.add_argument("--max-step", type=float, default=5.0)
    parser.add_argument("--attraction-strength", type=float, default=0.01)
    parser.add_argument("--repulsion-strength", type=float, default=0.5)
    parser.add_argument("--anchor-strength", type=float, default=0.02)
    parser.add_argument("--weight-scale", type=float, default=0.35)
    parser.add_argument(
        "--permutation",
        type=Path,
        default=PROJECT_ROOT / "src/lib/data/optimized-permutation-100.json",
        help="Permutation file mapping actor index to position index.",
    )
    parser.add_argument("--upsert", action="store_true", help="Upsert relaxed positions to Supabase.")
    parser.add_argument("--table", type=str, default="actors")
    parser.add_argument("--id-column", type=str, default="person_id")
    parser.add_argument("--x-column", type=str, default="x_100")
    parser.add_argument("--y-column", type=str, default="y_100")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--max-iterations", type=int, default=500)
    parser.add_argument("--improvement-threshold", type=float, default=0.002)
    parser.add_argument("--patience", type=int, default=15)
    parser.add_argument("--report-every", type=int, default=10)
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    actors, edges = load_input(args.input)
    base_positions = np.array([[actor["x"], actor["y"]] for actor in actors], dtype=float)

    if args.permutation and args.permutation.exists():
        with open(args.permutation, "r", encoding="utf-8") as f:
            permutation_data = json.load(f)
        permutation = permutation_data.get("permutation", [])
        if len(permutation) == len(actors):
            positions = base_positions[np.array(permutation, dtype=int)]
        else:
            print(
                "Permutation size mismatch; using base positions from input file."
            )
            positions = base_positions.copy()
    else:
        positions = base_positions.copy()

    normalized_recog = normalize_recognizability(actors)
    weights = compute_edge_weights(edges, normalized_recog, args.weight_scale)

    print(f"Loaded {len(actors)} actors and {len(edges)} edges.")
    print(
        "Settings: "
        f"min_distance={args.min_distance}, step_size={args.step_size}, "
        f"max_step={args.max_step}, weight_scale={args.weight_scale}"
    )

    relaxed_positions = relax_layout(
        positions=positions,
        edges=edges,
        weights=weights,
        min_distance=args.min_distance,
        step_size=args.step_size,
        max_step=args.max_step,
        attraction_strength=args.attraction_strength,
        repulsion_strength=args.repulsion_strength,
        anchor_strength=args.anchor_strength,
        max_iterations=args.max_iterations,
        improvement_threshold=args.improvement_threshold,
        patience=args.patience,
        report_every=args.report_every,
    )

    save_positions(args.output, actors, positions, relaxed_positions)
    print(f"Saved relaxed positions to {args.output}")

    if args.upsert:
        supabase = get_supabase_client()
        upsert_positions(
            supabase=supabase,
            actors=actors,
            positions=relaxed_positions,
            table=args.table,
            id_column=args.id_column,
            x_column=args.x_column,
            y_column=args.y_column,
            batch_size=args.batch_size,
        )
        print("Supabase upsert complete.")


if __name__ == "__main__":
    main()
