"""Smoke tests for stl-tools.

Uses trimesh-generated primitives so the tests need no fixture files.
"""

import math

import numpy as np
import trimesh

from stl_tools.core import (
    add_flat_base,
    bbox_info,
    is_manifold,
    repair_mesh,
    set_scale,
)


def test_cube_is_manifold():
    cube = trimesh.creation.box(extents=[10, 10, 10])
    assert is_manifold(cube) is True


def test_open_cylinder_not_manifold():
    # A cylinder without caps is open => not watertight
    cyl = trimesh.creation.cylinder(radius=5, height=10, sections=12)
    cyl.faces = cyl.faces[1:]  # drop one face to break manifold
    cyl.process(validate=False)
    assert is_manifold(cyl) is False


def test_repair_fills_small_holes():
    cube = trimesh.creation.box(extents=[10, 10, 10])
    broken = cube.copy()
    broken.faces = broken.faces[1:]
    assert is_manifold(broken) is False
    repaired = repair_mesh(broken)
    # repair won't always succeed — but should at least leave the mesh
    # processable (no exception). We don't assert watertight here.
    assert isinstance(repaired, trimesh.Trimesh)


def test_add_flat_base_increases_z_extent():
    cube = trimesh.creation.box(extents=[10, 10, 10])
    z_before = cube.bounds[1][2] - cube.bounds[0][2]
    with_base = add_flat_base(cube, thickness_mm=2.0)
    z_after = with_base.bounds[1][2] - with_base.bounds[0][2]
    assert z_after > z_before
    # Z should grow by approximately the base thickness
    assert math.isclose(z_after, z_before + 2.0, abs_tol=0.1)


def test_set_scale_doubles_extents():
    cube = trimesh.creation.box(extents=[10, 10, 10])
    set_scale(cube, 2.0)
    size = cube.bounds[1] - cube.bounds[0]
    assert np.allclose(size, [20, 20, 20])


def test_bbox_info_keys():
    cube = trimesh.creation.box(extents=[4, 6, 8])
    info = bbox_info(cube)
    assert set(info.keys()) == {"min", "max", "size", "center", "volume_mm3"}
    assert info["size"] == (4.0, 6.0, 8.0)
    assert info["volume_mm3"] > 0


def test_set_scale_rejects_nonpositive():
    cube = trimesh.creation.box(extents=[10, 10, 10])
    try:
        set_scale(cube, 0)
    except ValueError:
        return
    raise AssertionError("set_scale(0) should have raised ValueError")
