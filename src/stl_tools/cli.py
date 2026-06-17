"""Command-line interface for stl-tools.

Usage examples::

    stl-tools info input.stl
    stl-tools repair input.stl --output fixed.stl
    stl-tools add-base input.stl --output with_base.stl --thickness 2.0
    stl-tools scale input.stl --output scaled.stl --factor 1000.0
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from stl_tools.core import (
    add_flat_base,
    bbox_info,
    is_manifold,
    load_mesh,
    repair_mesh,
    save_mesh,
    set_scale,
)


def _cmd_info(args: argparse.Namespace) -> int:
    mesh = load_mesh(args.input)
    info = {
        "input": str(args.input),
        "vertices": int(len(mesh.vertices)),
        "faces": int(len(mesh.faces)),
        "is_watertight": bool(mesh.is_watertight),
        **bbox_info(mesh),
    }
    print(json.dumps(info, indent=2))
    return 0


def _cmd_repair(args: argparse.Namespace) -> int:
    mesh = load_mesh(args.input)
    fixed = repair_mesh(mesh)
    out = save_mesh(fixed, args.output or args.input)
    watertight = is_manifold(fixed)
    sys.stderr.write(
        f"Repaired → {out} (watertight={watertight})\n"
    )
    return 0 if watertight else 1


def _cmd_add_base(args: argparse.Namespace) -> int:
    mesh = load_mesh(args.input)
    with_base = add_flat_base(mesh, thickness_mm=args.thickness)
    out = save_mesh(with_base, args.output or args.input)
    sys.stderr.write(f"Base added → {out} (thickness={args.thickness}mm)\n")
    return 0


def _cmd_scale(args: argparse.Namespace) -> int:
    mesh = load_mesh(args.input)
    scaled = set_scale(mesh, args.factor)
    out = save_mesh(scaled, args.output or args.input)
    sys.stderr.write(f"Scaled by {args.factor}× → {out}\n")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="stl-tools",
        description="Prepare STL meshes for 3D printing — repair, base, scale.",
    )
    subs = parser.add_subparsers(dest="cmd", required=True)

    p_info = subs.add_parser("info", help="Print mesh stats + bounding box.")
    p_info.add_argument("input", type=Path)
    p_info.set_defaults(func=_cmd_info)

    p_repair = subs.add_parser("repair", help="Attempt to fix non-manifold mesh.")
    p_repair.add_argument("input", type=Path)
    p_repair.add_argument("-o", "--output", type=Path, default=None)
    p_repair.set_defaults(func=_cmd_repair)

    p_base = subs.add_parser("add-base", help="Add a flat rectangular base.")
    p_base.add_argument("input", type=Path)
    p_base.add_argument("-o", "--output", type=Path, default=None)
    p_base.add_argument("--thickness", type=float, default=2.0,
                        help="Base thickness in mm (default 2.0)")
    p_base.set_defaults(func=_cmd_add_base)

    p_scale = subs.add_parser("scale", help="Uniformly scale by factor.")
    p_scale.add_argument("input", type=Path)
    p_scale.add_argument("-o", "--output", type=Path, default=None)
    p_scale.add_argument("--factor", type=float, required=True,
                        help="Scale factor (e.g. 1000.0 for m→mm)")
    p_scale.set_defaults(func=_cmd_scale)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
