# meljahmi_hw1_part2-2_min.py
# RBE-550 Assignment 1 — Part 2.2 (Minimal Submission)
# ----------------------------------------------------
# Generates obstacle fields on an N×N grid using tetrominoes (I, L, S, T).
# Saves BLACK/WHITE EPS images for ρ in {0.10, 0.50, 0.70} by default.
# Use --png to also save PNGs. That’s it.

from __future__ import annotations
import argparse, random
from typing import List, Dict, Tuple
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

# Defaults
GRID_N = 128
DEFAULT_RHOS = [0.10, 0.50, 0.70]
SEED = 42
EMPTY = -1
MAX_TRIES_FACTOR = 200  # scales placement attempts with grid size

# --- Tetromino masks (True=occupied) ---
def rot90(a: np.ndarray) -> np.ndarray:
    return np.rot90(a, 1)

def uniq_rots(a: np.ndarray) -> List[np.ndarray]:
    rots = [a]
    for _ in range(3):
        rots.append(rot90(rots[-1]))
    uniq: List[np.ndarray] = []
    for r in rots:
        if not any(r.shape == t.shape and np.array_equal(r, t) for t in uniq):
            uniq.append(r)
    return uniq

I = np.array([[1,1,1,1]], dtype=bool)
L = np.array([[1,0],[1,0],[1,1]], dtype=bool)
S = np.array([[0,1,1],[1,1,0]], dtype=bool)
T = np.array([[1,1,1],[0,1,0]], dtype=bool)

CATALOG: Dict[str, List[np.ndarray]] = {
    "I": uniq_rots(I),
    "L": uniq_rots(L),
    "S": uniq_rots(S),
    "T": uniq_rots(T),
}
NAMES = list(CATALOG.keys())

# --- Placement helpers ---
def can_place(G: np.ndarray, mask: np.ndarray, r: int, c: int) -> bool:
    h, w = mask.shape
    if r+h > G.shape[0] or c+w > G.shape[1]:
        return False
    return not np.any(G[r:r+h, c:c+w][mask] != EMPTY)

def place(G: np.ndarray, mask: np.ndarray, r: int, c: int) -> int:
    h, w = mask.shape
    G[r:r+h, c:c+w][mask] = 1  # mark occupied (single value is enough for B/W)
    return int(mask.sum())

def f_rho(rho: float, n: int, rng: random.Random) -> np.ndarray:
    """Greedily place random tetrominoes until target coverage is reached (or tries run out)."""
    rho = max(0.0, min(1.0, float(rho)))
    target = int(round(rho * n * n))
    G = np.full((n, n), EMPTY, dtype=int)

    placed, tries = 0, 0
    max_tries = max(MAX_TRIES_FACTOR * n, 10000)

    while placed < target and tries < max_tries:
        tries += 1
        shape = rng.choice(NAMES)
        mask = rng.choice(CATALOG[shape])
        h, w = mask.shape
        r = rng.randrange(0, n - h + 1)
        c = rng.randrange(0, n - w + 1)
        if can_place(G, mask, r, c):
            placed += place(G, mask, r, c)

    return G

# --- Rendering (black/white only) ---
def save_bw(G: np.ndarray, rho: float, out_eps: Path, out_png: Path | None) -> None:
    BW = (G != EMPTY)
    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
    ax.imshow(BW, cmap="gray_r", interpolation="nearest", origin="lower")
    ax.set_xticks([]); ax.set_yticks([])
    actual = BW.mean()
    ax.set_title(f"Obstacle Field {G.shape[0]}×{G.shape[1]} — ρ target {rho:.2f}, actual {actual:.3f}", fontsize=10)
    plt.tight_layout()
    fig.savefig(out_eps, format="eps")
    if out_png is not None:
        fig.savefig(out_png)
    plt.close(fig)

# --- CLI ---
def parse_args():
    p = argparse.ArgumentParser(
        description="RBE-550 A1 Part 2.2 — Minimal: black/white EPS figures for given ρ values.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    p.add_argument("--rho", type=float, nargs="+", default=DEFAULT_RHOS, metavar="R",
                   help="coverage levels in [0,1] (e.g., 0.10 0.50 0.70)")
    p.add_argument("--n", type=int, default=GRID_N, metavar="N",
                   help="grid size (N×N)")
    p.add_argument("--seed", type=int, default=SEED, metavar="S",
                   help="random seed for reproducibility")
    p.add_argument("--outdir", type=Path, default=Path("."), help="output directory")
    p.add_argument("--png", action="store_true", help="also save PNG files (in addition to EPS)")
    return p.parse_args()

# --- Main ---
def main():
    args = parse_args()
    rng = random.Random(args.seed)
    args.outdir.mkdir(parents=True, exist_ok=True)

    for rho in args.rho:
        G = f_rho(rho, args.n, rng)
        label = int(round(rho * 100))
        eps_path = args.outdir / f"obstacles_rho_{label}.eps"
        png_path = (args.outdir / f"obstacles_rho_{label}.png") if args.png else None
        save_bw(G, rho, eps_path, png_path)
        print(f"Saved: {eps_path}" + ("" if png_path is None else f", {png_path}"))

if __name__ == "__main__":
    main()

