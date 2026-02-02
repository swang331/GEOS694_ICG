#!/usr/bin/env python3
import math
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# PATHS
INFILE = Path("/Users/serinawang/Downloads/pe1a_Kim.elacinput.txt")
OUTFILE = Path("/Users/serinawang/Desktop/seiac.elacinput")

# Air-ring config
RINGS_M = [100.0, 300.0, 500.0]  # radii in meters
N_PER_SEMI = 181  # number of points per semicircle (0..180°)
Z_SHIFT_M = 0.0  # ElAc convention: z is negative upward (more negative is higher)


def parse_source_xy(lines):
    """Find a line starting with 'source ' and extract x, y (floats)."""
    sx = sy = None
    for line in lines:
        if line.strip().startswith("source "):
            mx = re.search(r"\bx=([-\d.]+)", line)
            my = re.search(r"\by=([-\d.]+)", line)
            if mx and my:
                sx = float(mx.group(1))
                sy = float(my.group(1))
                break

    if sx is None or sy is None:
        raise RuntimeError(
            "Could not find 'source' line with x= and y= in the input file."
        )
    return sx, sy


def fix_all_rec_z(lines):
    """
    For every existing 'rec ' line in the original file, set z=0.00.
    (Air-ring receivers are added later and keep their own z.)
    """
    out_lines = []
    for line in lines:
        if line.strip().startswith("rec "):
            line = re.sub(r"z=([-\d.]+)", "z=0.00", line, count=1)
        out_lines.append(line)
    return out_lines


def semicircle_points_ns(sx, sy, radius_m, n_points, z_shift_m):
    """
    NS vertical plane: x fixed at sx, y varies, z describes a semicircle above ground.
    ElAc convention: z is negative upward.
    """
    phis = np.linspace(0.0, math.pi, n_points)  # 0..180 degrees
    xs, ys, zs = [], [], []

    for phi in phis:
        y = sy + radius_m * math.cos(phi)  # horizontal offset in NS
        h = radius_m * math.sin(phi)  # height above ground (>= 0)
        z = -(h + z_shift_m)
        xs.append(sx)
        ys.append(y)
        zs.append(z)

    return xs, ys, zs


def semicircle_points_ew(sx, sy, radius_m, n_points, z_shift_m):
    """
    EW vertical plane: y fixed at sy, x varies, z describes a semicircle above ground.
    ElAc convention: z is negative upward.
    """
    phis = np.linspace(0.0, math.pi, n_points)  # 0..180 degrees
    xs, ys, zs = [], [], []

    for phi in phis:
        x = sx + radius_m * math.cos(phi)  # horizontal offset in EW
        h = radius_m * math.sin(phi)  # height above ground (>= 0)
        z = -(h + z_shift_m)
        xs.append(x)
        ys.append(sy)
        zs.append(z)

    return xs, ys, zs


def format_rec_line(x, y, z, name):
    """
    Produce an ElAc receiver line:
      rec x=... y=... z=... variables=acoustic sacformat=1 file=<name>
    """
    return (
        f"rec x={x:.2f} y={y:.2f} z={z:.2f} "
        f"variables=acoustic sacformat=1 file={name}"
    )


def main():
    if not INFILE.exists():
        raise FileNotFoundError(f"Input file not found: {INFILE}")

    lines = INFILE.read_text(encoding="utf-8").splitlines()

    # 1) Get source x,y
    sx, sy = parse_source_xy(lines)
    print(f"Parsed source position: x={sx:.2f}, y={sy:.2f}")

    # 2) Set z=0.00 for ALL existing receivers
    lines = fix_all_rec_z(lines)

    # 3) Generate air-ring receivers in NS and EW planes
    air_lines = []
    ns_points = []  # for plotting: (y, z, radius_m)
    ew_points = []  # for plotting: (x, z, radius_m)

    for ring_idx, radius_m in enumerate(RINGS_M, start=1):
        # NS semicircle → HX<ring>_<point>
        xs_ns, ys_ns, zs_ns = semicircle_points_ns(
            sx, sy, radius_m, N_PER_SEMI, Z_SHIFT_M
        )
        for pt_idx, (x, y, z) in enumerate(zip(xs_ns, ys_ns, zs_ns), start=1):
            name = f"HX{ring_idx}_{pt_idx}"
            air_lines.append(format_rec_line(x, y, z, name))
            ns_points.append((y, z, radius_m))

        # EW semicircle → HY<ring>_<point>
        xs_ew, ys_ew, zs_ew = semicircle_points_ew(
            sx, sy, radius_m, N_PER_SEMI, Z_SHIFT_M
        )
        for pt_idx, (x, y, z) in enumerate(zip(xs_ew, ys_ew, zs_ew), start=1):
            name = f"HY{ring_idx}_{pt_idx}"
            air_lines.append(format_rec_line(x, y, z, name))
            ew_points.append((x, z, radius_m))

    print(
        f"Generated {len(air_lines)} air-station receivers "
        f"({len(RINGS_M)} rings × {N_PER_SEMI} pts × 2 planes)."
    )

    # 4) Append the air receiver lines to the modified file content
    lines_out = list(lines)
    lines_out.append("")  # blank line for separation
    lines_out.extend(air_lines)

    # 5) Write to OUTFILE
    OUTFILE.parent.mkdir(parents=True, exist_ok=True)
    OUTFILE.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    print(f"Wrote updated ElAc input to: {OUTFILE}")

    # 6) Plot NS and EW cross sections (y vs z, x vs z)
    if ns_points and ew_points:
        fig, (ax_ns, ax_ew) = plt.subplots(
            1, 2, figsize=(12, 5), constrained_layout=True
        )

        # NS plane: y vs z
        ys, zs, _ = zip(*ns_points)
        ax_ns.scatter(ys, zs, s=20)
        ax_ns.set_xlabel("y (m) [NS]")
        ax_ns.set_ylabel("z (m)")
        ax_ns.set_title("Air stations – NS vertical cross-section")
        ax_ns.axhline(0.0, ls="--", lw=0.8)  # ground (z=0)
        ax_ns.invert_yaxis()  # more negative (higher) plots upwards

        # EW plane: x vs z
        xs, zs2, _ = zip(*ew_points)
        ax_ew.scatter(xs, zs2, s=20)
        ax_ew.set_xlabel("x (m) [EW]")
        ax_ew.set_ylabel("z (m)")
        ax_ew.set_title("Air stations – EW vertical cross-section")
        ax_ew.axhline(0.0, ls="--", lw=0.8)
        ax_ew.invert_yaxis()

        rings_str = ", ".join(f"{r:g}" for r in RINGS_M)
        plt.suptitle(
            f"Air stations (R={rings_str} m), z-shift = {Z_SHIFT_M:g} m"
        )
        plt.show()


if __name__ == "__main__":
    main()
