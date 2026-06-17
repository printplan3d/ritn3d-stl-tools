"""stl-tools — prepare STL meshes for 3D printing.

A small Python library + CLI for the common pre-slice tasks every
3D-print hobbyist hits sooner or later: checking whether a mesh is
manifold (watertight), repairing it if not, adding a flat base so the
model has somewhere to sit on the build plate, normalizing units so
the slicer interprets dimensions correctly, and reporting bounding box
info.

Generic — works on any STL. Designed initially to post-process exports
from the Ritn3D floor-plan-to-3D-model pipeline before sending them to
Cura, PrusaSlicer, Bambu Studio, or Lychee, but the library has no
dependency on Ritn3D and is useful for any mesh-prep workflow.
"""

from stl_tools.core import (
    add_flat_base,
    bbox_info,
    is_manifold,
    load_mesh,
    repair_mesh,
    save_mesh,
    set_scale,
)

__version__ = "0.1.0"

__all__ = [
    "__version__",
    "add_flat_base",
    "bbox_info",
    "is_manifold",
    "load_mesh",
    "repair_mesh",
    "save_mesh",
    "set_scale",
]
