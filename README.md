# stl-tools

> A small Python library + CLI for the common pre-slice tasks every 3D-print
> hobbyist hits: checking whether a mesh is **manifold** (watertight),
> repairing it if it isn't, adding a **flat base** so the model sits on the
> build plate, and **normalizing units** so the slicer interprets dimensions
> correctly.

Works on any STL (or any other format trimesh can read). Designed initially
to post-process exports from the [Ritn3D](https://www.ritn3d.com) floor-plan-
to-3D-model pipeline before sending them to Cura, PrusaSlicer, Bambu Studio,
or Lychee — but the library has no dependency on Ritn3D and is useful for
any mesh-prep workflow.

## Install

```bash
pip install stl-tools
```

## CLI

```bash
# Inspect a mesh
stl-tools info mymodel.stl

# Repair a non-manifold mesh in place
stl-tools repair broken.stl -o fixed.stl

# Add a 2mm flat base
stl-tools add-base mymodel.stl -o with_base.stl --thickness 2.0

# Scale from meters to millimeters (Blender default → slicer default)
stl-tools scale meters.stl -o mm.stl --factor 1000.0
```

## Library

```python
from stl_tools import (
    load_mesh, save_mesh,
    is_manifold, repair_mesh,
    add_flat_base, set_scale, bbox_info,
)

mesh = load_mesh("input.stl")

if not is_manifold(mesh):
    mesh = repair_mesh(mesh)

# Architectural model: meters → mm, then flat base for the build plate
set_scale(mesh, 1000.0)
mesh = add_flat_base(mesh, thickness_mm=2.0)

print(bbox_info(mesh))
# {'min': (...), 'max': (...), 'size': (...), 'center': (...), 'volume_mm3': ...}

save_mesh(mesh, "ready_to_slice.stl")
```

## What's in scope

| Feature | Status |
|---|---|
| Manifold check | ✓ |
| Standard mesh repair (winding, normals, small holes) | ✓ |
| Flat base addition | ✓ |
| Uniform scale | ✓ |
| Bounding-box reporting | ✓ |

## What's out of scope

This library is intentionally small. For heavier operations — mesh decimation,
remeshing, support generation, slicing itself — use the right tool for the
job:

- **trimesh** itself (this lib wraps it) for richer mesh ops
- **PyMeshLab** for advanced repair, remeshing, decimation
- **Cura / PrusaSlicer / Bambu Studio** for actual slicing and supports
- **Blender's 3D-Print toolbox** for interactive repair on severely broken
  meshes

## Why this exists

Every hobbyist who exports a 3D model from Blender, SketchUp, an AI tool, or
a custom pipeline ends up writing the same five-line trimesh snippet to make
the file slicer-ready. We did too — and after the tenth copy-paste, we wrote
it down as a library.

If you're using Ritn3D's STL export (Pro+ tier) and want to apply additional
post-processing before slicing — different base thickness, different units,
extra repair — pip-install this, run two CLI commands, and you're done.

## Compatibility

- Python 3.9+
- Tested on Linux, macOS, Windows
- STL is the primary target; OBJ, PLY, GLB also work where trimesh supports
  them

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

Built on top of [trimesh](https://github.com/mikedh/trimesh), the standard
Python mesh library. If you find this useful, star [trimesh](https://github.com/mikedh/trimesh)
too — the heavy lifting happens there.

## Maintained by

[Ritn3D](https://www.ritn3d.com) — an AI floor-plan-to-3D-model tool. We
needed slicer-ready STL output for the Pro+ tier, wrote this to do it, and
open-sourced it for everyone else doing the same thing.
