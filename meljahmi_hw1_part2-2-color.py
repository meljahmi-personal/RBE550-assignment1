# meljahmi_hw1_part2-2-color.py
# RBE-550 Assignment 1 — Part 2.2 (Obstacle Fields)
# =============================================================================
# PURPOSE
#   Generate random obstacle fields on an N×N grid using tetrominoes (I, L, S, T).
#   Output figures at specified coverage ratios ρ (e.g., 0.10, 0.50, 0.70).
#
# WHAT THIS SCRIPT PRODUCES
#   - Black/white PNGs (always).
#   - Optional colored+gridded PNGs with a legend (--color).
#   - Optional EPS versions of the above (--save-eps).
#   - Optional CSV with per-ρ statistics: piece counts and coverage (--save-csv).
#
# WHY THIS MATCHES THE HOMEWORK
#   - Uses I/L/S/T tetrominoes, allows rotations, prevents overlap.
#   - Supports ρ = 10%, 50%, 70% (defaults).
#   - Produces figures similar to those in the handout.
#
# QUICK USAGE
#   python3 meljahmi_hw1_part2-2.py                # PNG (B/W), ρ=0.10,0.50,0.70
#   python3 meljahmi_hw1_part2-2.py --color        # also make colored+gridded PNGs w/ legend
#   python3 meljahmi_hw1_part2-2.py --save-eps     # also write EPS versions
#   python3 meljahmi_hw1_part2-2.py --rho 0.25 0.4 --n 96 --color --save-eps --verbose
#
# NOTES
#   - “Coverage” ρ is (# occupied cells) / (N*N).
#   - Random packing can’t hit target exactly; script reports actual ρ.
# =============================================================================

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors, patches


# ---------------------------
# Defaults / constants
# ---------------------------
GRID_N = 128                         # default grid size: N×N
DEFAULT_RHOS = [0.10, 0.50, 0.70]    # default coverage targets
SEED = 42                            # default RNG seed (reproducible)
MAX_TRIES_FACTOR = 200               # placement attempts scale factor
EMPTY = -1                           # marker for “free” cell in grid

# Encode tetromino types as small ints so we can color them reliably.
TYPE_TO_CODE = {"I": 0, "L": 1, "S": 2, "T": 3}
CODE_TO_TYPE = {v: k for k, v in TYPE_TO_CODE.items()}


# ---------------------------
# Tetromino definitions
# ---------------------------
def rot90(a: np.ndarray) -> np.ndarray:
    """Return a 90°-rotated copy of boolean mask `a`.

    Args:
        a: Boolean 2D array where True indicates a filled cell.

    Returns:
        Rotated mask (clockwise or counterclockwise—np.rot90 rotates CCW).
    """
    return np.rot90(a, 1)


def uniq_rots(a: np.ndarray) -> List[np.ndarray]:
    """Return all unique 90° rotations of mask `a`.

    Some shapes (e.g., the I tetromino) have only 2 unique rotations;
    this function filters duplicates by shape and contents.

    Args:
        a: Boolean 2D array for the base orientation.

    Returns:
        List of boolean masks representing distinct rotations.
    """
    rots = [a]
    for _ in range(3):
        rots.append(rot90(rots[-1]))
    uniq: List[np.ndarray] = []
    for r in rots:
        if not any(r.shape == t.shape and np.array_equal(r, t) for t in uniq):
            uniq.append(r)
    return uniq


# Boolean masks for base orientations (True = filled cell)
I = np.array([[1, 1, 1, 1]], dtype=bool)
L = np.array([[1, 0],
              [1, 0],
              [1, 1]], dtype=bool)
S = np.array([[0, 1, 1],
              [1, 1, 0]], dtype=bool)
T = np.array([[1, 1, 1],
              [0, 1, 0]], dtype=bool)

# Map each type to its unique rotations
CATALOG: Dict[str, List[np.ndarray]] = {
    "I": uniq_rots(I),
    "L": uniq_rots(L),
    "S": uniq_rots(S),
    "T": uniq_rots(T),
}
NAMES = list(CATALOG.keys())


# ---------------------------
# Placement (grid filling)
# ---------------------------
def can_place(grid: np.ndarray, mask: np.ndarray, r: int, c: int) -> bool:
    """Check whether `mask` can be placed at (r, c) without overlap or out-of-bounds.

    Args:
        grid: N×N integer array with EMPTY for free, or type codes for occupied.
        mask: boolean shape mask (True = will occupy).
        r, c: top-left placement indices.

    Returns:
        True if placement is fully in-bounds and on EMPTY cells; False otherwise.
    """
    h, w = mask.shape
    if r + h > grid.shape[0] or c + w > grid.shape[1]:
        return False
    return not np.any(grid[r:r + h, c:c + w][mask] != EMPTY)


def place(grid: np.ndarray, mask: np.ndarray, r: int, c: int, type_code: int) -> int:
    """Write `type_code` into grid cells covered by `mask` placed at (r, c).

    Args:
        grid: N×N integer array.
        mask: boolean mask of a tetromino orientation.
        r, c: top-left indices where mask is applied.
        type_code: small int indicating tetromino type (see TYPE_TO_CODE).

    Returns:
        The number of newly occupied cells (sum of mask).
    """
    h, w = mask.shape
    grid[r:r + h, c:c + w][mask] = type_code
    return int(mask.sum())


def f_rho_labeled(rho: float, n: int, rng: random.Random) -> Tuple[np.ndarray, Dict[str, int]]:
    """Fill an N×N grid with randomly placed tetrominoes until target coverage is reached.

    Strategy:
        - Repeatedly sample a tetromino type and a random orientation, then a random
          top-left location; place it if it fits w/out overlap.
        - Stop when the number of occupied cells hits the target or we exceed a
          reasonable number of attempts (to avoid infinite loops at high density).

    Args:
        rho: target coverage in [0, 1] (e.g., 0.10 for 10%).
        n: grid size (N×N).
        rng: random.Random instance (seeded for reproducibility).

    Returns:
        (grid, stats):
            grid: N×N int array with cell values = EMPTY or type_code (0..3).
            stats: dict { "I": count, "L": count, "S": count, "T": count } of pieces placed.
    """
    rho = max(0.0, min(1.0, float(rho)))   # clamp to [0, 1]
    target_cells = int(round(rho * n * n))

    grid = np.full((n, n), EMPTY, dtype=int)
    stats: Dict[str, int] = {k: 0 for k in NAMES}

    placed_cells, tries = 0, 0
    max_tries = max(MAX_TRIES_FACTOR * n, 10000)  # scale attempts w/ grid size

    while placed_cells < target_cells and tries < max_tries:
        tries += 1

        # 1) Pick a tetromino type and one of its unique rotations
        tname = rng.choice(NAMES)
        mask = rng.choice(CATALOG[tname])

        # 2) Pick a random top-left position that could fit (by shape size)
        h, w = mask.shape
        rr = rng.randrange(0, n - h + 1)
        cc = rng.randrange(0, n - w + 1)

        # 3) Check overlap/bounds; place if valid
        if can_place(grid, mask, rr, cc):
            placed_cells += place(grid, mask, rr, cc, TYPE_TO_CODE[tname])
            stats[tname] += 1

    return grid, stats


# ---------------------------
# Rendering (figures)
# ---------------------------
def save_color_with_legend(
    grid: np.ndarray,
    rho: float,
    out_png: Path,
    out_eps: Path | None,
    show_grid: bool = True,
) -> None:
    """Save a colored+gridded visualization with legend mapping I/L/S/T.

    Color mapping:
        EMPTY -> white
        I,L,S,T -> distinct categorical colors.
    Legend shows which color corresponds to which tetromino letter.

    Args:
        grid: N×N int grid with EMPTY or type codes (0..3).
        rho: target coverage (for title).
        out_png: file path for PNG.
        out_eps: optional file path for EPS (if None, EPS is skipped).
        show_grid: draw faint 1×1 grid lines to mimic the handout’s look.
    """
    # Explicit categorical colors (white + 4 distinct hues):
    cmap_list = ["#ffffff", "#4e79a7", "#f28e2b", "#e15759", "#76b7b2"]
    cmap = colors.ListedColormap(cmap_list)

    # BoundaryNorm splits values into bins: [-1]=EMPTY, then 0..3 for I,L,S,T
    bounds = [-1.5, -0.5, 0.5, 1.5, 2.5, 3.5]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.imshow(grid, cmap=cmap, norm=norm, interpolation="nearest", origin="lower")

    # Optional faint grid lines (visual aid)
    if show_grid:
        ax.set_xticks(np.arange(-0.5, grid.shape[1], 1), minor=True)
        ax.set_yticks(np.arange(-0.5, grid.shape[0], 1), minor=True)
        ax.grid(which="minor", color="black", linewidth=0.2, alpha=0.25)

    ax.set_xticks([]); ax.set_yticks([])

    # Build legend with color patches labeled by tetromino letter.
    legend_handles = [
        patches.Patch(facecolor=cmap_list[1], edgecolor="black", label="I"),
        patches.Patch(facecolor=cmap_list[2], edgecolor="black", label="L"),
        patches.Patch(facecolor=cmap_list[3], edgecolor="black", label="S"),
        patches.Patch(facecolor=cmap_list[4], edgecolor="black", label="T"),
    ]
    ax.legend(handles=legend_handles, title="Tetromino", loc="upper right",
              framealpha=0.9, fontsize=8)

    actual = (grid != EMPTY).mean()
    ax.set_title(
        f"Tetromino field {grid.shape[0]}×{grid.shape[1]} — ρ target {rho:.2f}, actual {actual:.3f}",
        fontsize=10,
    )

    plt.tight_layout()
    fig.savefig(out_png)
    if out_eps is not None:
        fig.savefig(out_eps, format="eps")
    plt.close(fig)


def save_bw(grid: np.ndarray, rho: float, out_png: Path, out_eps: Path | None) -> None:
    """Save a black/white occupancy plot (white = free, black = occupied).

    Args:
        grid: N×N int grid with EMPTY or type codes.
        rho: target coverage (for title).
        out_png: file path for PNG.
        out_eps: optional file path for EPS (if None, EPS is skipped).
    """
    BW = (grid != EMPTY)

    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.imshow(BW, cmap="gray_r", interpolation="nearest", origin="lower")
    ax.set_xticks([]); ax.set_yticks([])

    actual = BW.mean()
    ax.set_title(
        f"Obstacle Field {BW.shape[0]}×{BW.shape[1]} — ρ target {rho:.2f}, actual {actual:.3f}",
        fontsize=10,
    )

    plt.tight_layout()
    fig.savefig(out_png)
    if out_eps is not None:
        fig.savefig(out_eps, format="eps")
    plt.close(fig)


# ---------------------------
# Command-line interface
# ---------------------------
def parse_args() -> argparse.Namespace:
    """Build and parse command-line options for the script.

    Flags overview:
        --rho R [R ...]   list of coverage levels in [0,1]
        --n N             grid size (N×N)
        --seed S          RNG seed
        --color           also emit colored+gridded PNGs with legend
        --no-grid         (w/ --color) omit faint grid lines
        --save-eps        also emit EPS in addition to PNG
        --outdir PATH     output directory (created if missing)
        --save-csv PATH   write per-ρ stats to CSV
        --verbose         print piece counts and coverage details
    """
    p = argparse.ArgumentParser(
        prog="meljahmi_hw1_part2-2-color.py",
        description=(
            "RBE-550 A1 Part 2.2 — Tetromino obstacle fields.\n"
            "PNGs by default; add --color for colored+gridded with legend; add --save-eps for EPS."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--rho", type=float, nargs="+", default=DEFAULT_RHOS, metavar="R",
                   help="coverage ratios in [0,1] (e.g., 0.10 0.50 0.70)")
    p.add_argument("--n", type=int, default=GRID_N, metavar="N",
                   help="grid size; produces an N×N field")
    p.add_argument("--seed", type=int, default=SEED, metavar="S",
                   help="random seed for reproducible results")
    p.add_argument("--color", action="store_true",
                   help="also emit colored+gridded PNGs with a legend (I/L/S/T)")
    p.add_argument("--no-grid", action="store_true",
                   help="when used with --color, omit faint 1×1 grid lines")
    p.add_argument("--save-eps", action="store_true",
                   help="also write EPS files alongside PNG")
    p.add_argument("--outdir", type=Path, default=Path("."),
                   help="directory to write images (created if needed)")
    p.add_argument("--save-csv", type=Path, metavar="PATH",
                   help="optional CSV path to write per-ρ statistics")
    p.add_argument("--verbose", action="store_true",
                   help="print detailed stats to stdout")
    return p.parse_args()


# ---------------------------
# Main
# ---------------------------
def main() -> None:
    """Entrypoint: fill grids for requested ρ values, save figures and stats."""
    args = parse_args()
    rng = random.Random(args.seed)
    args.outdir.mkdir(parents=True, exist_ok=True)

    csv_rows: List[Dict[str, object]] = []

    for rho in args.rho:
        # 1) Generate an obstacle field that aims for target coverage ρ
        grid, piece_counts = f_rho_labeled(rho, args.n, rng)

        # 2) Prepare output filenames
        label = int(round(rho * 100))
        bw_png = args.outdir / f"obstacles_rho_{label}.png"
        bw_eps = (args.outdir / f"obstacles_rho_{label}.eps") if args.save_eps else None

        # 3) Save black/white occupancy figure (always)
        save_bw(grid, rho, bw_png, bw_eps)

        # 4) Optionally save colored+gridded figure with legend
        if args.color:
            color_png = args.outdir / f"obstacles_rho_{label}_gridded.png"
            color_eps = (args.outdir / f"obstacles_rho_{label}_gridded.eps") if args.save_eps else None
            save_color_with_legend(grid, rho, color_png, color_eps, show_grid=(not args.no_grid))

        # 5) Compute and record statistics that demonstrate requirement compliance
        total_cells = args.n * args.n
        occ_cells = int((grid != EMPTY).sum())
        actual_rho = occ_cells / total_cells if total_cells else 0.0

        row = {
            "n": args.n,
            "rho_target": float(rho),
            "rho_actual": round(actual_rho, 6),
            "cells_total": total_cells,
            "cells_occupied": occ_cells,
            "count_I": piece_counts["I"],
            "count_L": piece_counts["L"],
            "count_S": piece_counts["S"],
            "count_T": piece_counts["T"],
        }
        csv_rows.append(row)

        if args.verbose:
            saved = [str(bw_png)]
            if args.save_eps and bw_eps is not None:
                saved.append(str(bw_eps))
            if args.color:
                saved.append(str(color_png))
                if args.save_eps and color_eps is not None:
                    saved.append(str(color_eps))

            print(f"\nρ target {rho:.2f} | actual {actual_rho:.3f}")
            print(f"  cells: {occ_cells} / {total_cells}")
            print("  pieces:", f"I={row['count_I']}", f"L={row['count_L']}",
                  f"S={row['count_S']}", f"T={row['count_T']}")
            print("  saved:", ", ".join(saved))

    # 6) Optionally dump stats to CSV for your submission appendix
    if args.save_csv:
        args.save_csv.parent.mkdir(parents=True, exist_ok=True)
        with open(args.save_csv, "w", newline="") as f:
            fieldnames = [
                "n", "rho_target", "rho_actual", "cells_total", "cells_occupied",
                "count_I", "count_L", "count_S", "count_T",
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        if args.verbose:
            print(f"\nWrote stats CSV: {args.save_csv}")


if __name__ == "__main__":
    main()

