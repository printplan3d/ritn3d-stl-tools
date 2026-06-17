"""Core mesh-prep functions for stl-tools.

All functions operate on `trimesh.Trimesh` objects in memory and on
file paths for I/O. The library is intentionally small — five core
operations cover the great majority of slicer prep work. For more
exotic mesh ops (decimation, remesh, texture baking) reach for the
underlying trimesh library directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Union

import numpy as np
import trimesh

PathLike = Union[str, Path]


def load_mesh(path: PathLike) -> trimesh.Trimesh:
    """Load an STL (or any trimesh-readable mesh format) from disk.

    Raises ValueError if the file contains a scene with multiple meshes
    rather than a single mesh — callers should concatenate explicitly.
    """
    mesh = trimesh.load(str(path), force="mesh")
    if not isinstance(mesh, trimesh.Trimesh):
        raise ValueError(
            f"{path} contains a scene with multiple meshes; use "
            "trimesh.util.concatenate() and pass the result to stl-tools "
            "directly if you want them merged."
        )
    return mesh


def save_mesh(mesh: trimesh.Trimesh, path: PathLike) -> Path:
    """Save a mesh to disk. Format inferred from extension."""
    out = Path(path)
    mesh.export(str(out))
    return out


def is_manifold(mesh_or_path: Union[trimesh.Trimesh, PathLike]) -> bool:
    """Return True if the mesh is watertight (closed, manifold, no holes).

    Slicers can usually print non-manifold meshes but the resulting
    G-code is unpredictable — extra perimeters, missing infill, or
    failed top surfaces are all common. Repair before slicing.
    """
    mesh = (
        mesh_or_path
        if isinstance(mesh_or_path, trimesh.Trimesh)
        else load_mesh(mesh_or_path)
    )
    return bool(mesh.is_watertight)


def repair_mesh(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    """Attempt to repair a non-manifold mesh in place.

    Runs the standard trimesh repair pipeline: remove duplicate faces,
    fix winding, fill small holes. This handles the common slicer-
    rejection cases. For severely broken meshes (overlapping geometry,
    self-intersections), use a dedicated tool like Meshmixer or
    Blender's 3D-Print toolbox.
    """
    mesh.process(validate=True)
    mesh.remove_duplicate_faces()
    mesh.remove_degenerate_faces()
    trimesh.repair.fix_winding(mesh)
    trimesh.repair.fix_normals(mesh)
    trimesh.repair.fill_holes(mesh)
    return mesh


def add_flat_base(
    mesh: trimesh.Trimesh,
    thickness_mm: float = 2.0,
    plane_z: Union[float, None] = None,
) -> trimesh.Trimesh:
    """Add a flat rectangular base below the mesh.

    Useful for architectural / floor-plan / terrain prints where the
    underside of the model is irregular but you want a flat surface
    sitting on the build plate. The base is a simple extruded
    rectangle matching the XY bounding box of the mesh, with the top
    flush against the lowest Z of the original mesh (or `plane_z` if
    provided).

    Parameters
    ----------
    mesh : Trimesh
        The model to add a base under.
    thickness_mm : float
        Base thickness in millimeters (default 2.0).
    plane_z : float, optional
        Top-of-base Z coordinate. Defaults to mesh.bounds[0][2]
        (lowest point of the mesh).

    Returns
    -------
    Trimesh
        New mesh containing the original + the base, concatenated.
    """
    bounds_min, bounds_max = mesh.bounds
    top_z = plane_z if plane_z is not None else float(bounds_min[2])

    base = trimesh.creation.box(
        extents=[
            float(bounds_max[0] - bounds_min[0]),
            float(bounds_max[1] - bounds_min[1]),
            float(thickness_mm),
        ]
    )
    base.apply_translation([
        float((bounds_min[0] + bounds_max[0]) / 2),
        float((bounds_min[1] + bounds_max[1]) / 2),
        float(top_z - thickness_mm / 2),
    ])
    return trimesh.util.concatenate([mesh, base])


def set_scale(mesh: trimesh.Trimesh, factor: float) -> trimesh.Trimesh:
    """Uniformly scale the mesh in place by `factor`.

    Common factors:
      * 1000.0 — meters → millimeters (Blender default → slicer default)
      * 0.001  — millimeters → meters
      * 25.4   — inches → millimeters
      * 0.01   — centimeters → meters
    """
    if factor <= 0:
        raise ValueError(f"scale factor must be > 0 (got {factor})")
    mesh.apply_scale(factor)
    return mesh


def bbox_info(mesh: trimesh.Trimesh) -> dict:
    """Return a dict describing the mesh's axis-aligned bounding box.

    Output keys:
      ``min``, ``max`` — 3-tuples of x, y, z extremes
      ``size``        — 3-tuple of dx, dy, dz
      ``center``      — 3-tuple of the bounding-box center
      ``volume_mm3``  — convex hull volume estimate (mm³, assumes mm units)
    """
    bounds_min, bounds_max = mesh.bounds
    size = bounds_max - bounds_min
    center = (bounds_min + bounds_max) / 2.0
    return {
        "min": tuple(float(v) for v in bounds_min),
        "max": tuple(float(v) for v in bounds_max),
        "size": tuple(float(v) for v in size),
        "center": tuple(float(v) for v in center),
        "volume_mm3": float(mesh.convex_hull.volume),
    }
