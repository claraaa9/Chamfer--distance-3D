"""Evaluate geometric similarity between two 3D models with Chamfer distance."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree


def load_mesh_as_points(file_path: str | Path, num_points: int = 10_000) -> np.ndarray:
    """
    Load a 3D mesh file and sample points from its surface.

    Parameters
    ----------
    file_path:
        Path to the 3D model file, e.g. .obj, .stl, .ply, .glb.
    num_points:
        Number of points sampled from the mesh surface.

    Returns
    -------
    points:
        A numpy array with shape (num_points, 3).
    """
    mesh = trimesh.load(file_path, force="mesh")

    if mesh.is_empty:
        raise ValueError(f"Mesh is empty: {file_path}")

    points, _ = trimesh.sample.sample_surface(mesh, num_points)
    return points.astype(np.float64)


def normalize_points(points: np.ndarray) -> np.ndarray:
    """
    Normalize point cloud.

    1. Move its center to the origin.
    2. Scale it so that the largest dimension of its bounding box is 1.
    """
    points = np.asarray(points, dtype=np.float64)

    center = points.mean(axis=0)
    points = points - center

    bbox_min = points.min(axis=0)
    bbox_max = points.max(axis=0)
    scale = np.max(bbox_max - bbox_min)

    if scale == 0:
        raise ValueError("Point cloud has zero scale.")

    return points / scale


def chamfer_distance(
    a: np.ndarray,
    b: np.ndarray,
    squared: bool = True,
) -> tuple[float, float, float]:
    """
    Compute bidirectional Chamfer distance between two point clouds.

    Parameters
    ----------
    a:
        Point cloud A, shape (n, 3).
    b:
        Point cloud B, shape (m, 3).
    squared:
        If True, use squared Euclidean distance.

    Returns
    -------
    total_cd:
        A-to-B distance + B-to-A distance.
    a_to_b:
        Mean nearest-neighbor distance from A to B.
    b_to_a:
        Mean nearest-neighbor distance from B to A.
    """
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)

    if a.ndim != 2 or a.shape[1] != 3:
        raise ValueError("A must have shape (n, 3).")

    if b.ndim != 2 or b.shape[1] != 3:
        raise ValueError("B must have shape (m, 3).")

    tree_b = cKDTree(b)
    tree_a = cKDTree(a)

    dist_a_to_b, _ = tree_b.query(a)
    dist_b_to_a, _ = tree_a.query(b)

    if squared:
        dist_a_to_b = dist_a_to_b**2
        dist_b_to_a = dist_b_to_a**2

    a_to_b = float(dist_a_to_b.mean())
    b_to_a = float(dist_b_to_a.mean())
    total_cd = a_to_b + b_to_a

    return total_cd, a_to_b, b_to_a


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate two 3D models with bidirectional Chamfer distance.",
    )
    parser.add_argument("model_a", help="Path to model A, for example a RealityCapture model.")
    parser.add_argument("model_b", help="Path to model B, for example an AI-generated model.")
    parser.add_argument(
        "--num-points",
        type=int,
        default=10_000,
        help="Number of surface points sampled from each mesh. Default: 10000.",
    )
    parser.add_argument(
        "--no-normalize",
        action="store_true",
        help="Skip centering and scale normalization.",
    )
    parser.add_argument(
        "--not-squared",
        action="store_true",
        help="Use Euclidean distance instead of squared Euclidean distance.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    points_a = load_mesh_as_points(args.model_a, args.num_points)
    points_b = load_mesh_as_points(args.model_b, args.num_points)

    if not args.no_normalize:
        points_a = normalize_points(points_a)
        points_b = normalize_points(points_b)

    total_cd, a_to_b, b_to_a = chamfer_distance(
        points_a,
        points_b,
        squared=not args.not_squared,
    )

    print("Chamfer Distance")
    print("----------------")
    print(f"A to B: {a_to_b:.8f}")
    print(f"B to A: {b_to_a:.8f}")
    print(f"Total:  {total_cd:.8f}")


if __name__ == "__main__":
    main()

