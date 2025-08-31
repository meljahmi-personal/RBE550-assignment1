# meljahmi_hw11_part2-2.py
# RBE-550 Assignment 0 — Part 2.2
# Generate obstacle fields on a 128x128 grid using tetrominoes (I, L, S, T).
# Outputs three PNGs at rho = 10%, 50%, 70%, both in black/white and in colored+gridded form.

from __future__ import annotations
import argparse, random
from typing import List
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colors

GRID_N = 128
DEFAULT_RHOS = [0.10, 0.50, 0.70]
SEED = 42
MAX_TRIES_FACTOR = 200
EMPTY = -1  # marker for free cells

# ---- Tetromino definitions ----
def rot90(a: np.ndarray) -> np.ndarray:
    return np.rot90(a, 1)

def uniq_rots(a: np.ndarray) -> List[np.ndarray]:
    rots = [a]
    for _ in range(3):
        rots.append(rot90(rots[-1]))
    uniq = []
    for r in rots:
        if not any(r.shape == t.shape and np.array_equal(r, t) for t in uniq):
            uniq.append(r)
    return uniq

I = np.array([[1,1,1,1]], dtype=bool)
L = np.array([[1,0],[1,0],[1,1]], dtype=bool)
S = np.array([[0,1,1],[1,1,0]], dtype=bool)
T = np.array([[1,1,1],[0,1,0]], dtype=bool)

CATALOG = {"I": uniq_rots(I), "L": uniq_rots(L), "S": uniq_rots(S), "T": uniq_rots(T)}
NAMES = list(CATALOG.keys())

# ---- Placement helpers ----
def can_place(G: np.ndarray, mask: np.ndarray, r: int, c: int) -> bool:
    h, w = mask.shape
    if r+h > G.shape[0] or c+w > G.shape[1]:
        return False
    return not np.any(G[r:r+h, c:c+w][mask] != EMPTY)


def place(G: np.ndarray, mask: np.ndarray, r: int, c: int, tid: int) -> None:
    h, w = mask.shape
    G[r:r+h, c:c+w][mask] = tid


#f(p) function
def f_rho_labeled(rho: float, n: int, rng: random.Random) -> np.ndarray:
    rho = max(0.0, min(1.0, float(rho)))
    target = int(round(rho * n * n))
    G = np.full((n, n), EMPTY, dtype=int)

    placed, tries, tid = 0, 0, 0
    max_tries = max(MAX_TRIES_FACTOR * n, 10000)

    while placed < target and tries < max_tries:
        tries += 1
        mask = rng.choice(CATALOG[rng.choice(NAMES)])
        h, w = mask.shape
        r = rng.randrange(0, n - h + 1)
        c = rng.randrange(0, n - w + 1)
        if can_place(G, mask, r, c):
            place(G, mask, r, c, tid)
            placed += int(mask.sum())
            tid += 1
    return G


# ---- Rendering ----
def save_gridded(G: np.ndarray, rho: float, path: str) -> None:
    max_id = G.max() if G.max() >= 0 else 0
    cmap = plt.colormaps.get_cmap('tab20')  # no LUT arg
    norm = colors.Normalize(vmin=-1, vmax=max_id)

    fig, ax = plt.subplots(figsize=(6,6), dpi=150)
    ax.imshow(G, cmap=cmap, norm=norm, interpolation="nearest", origin="lower")

    # draw faint gridlines like Figure 3 in homework
    ax.set_xticks(np.arange(-0.5, G.shape[1], 1), minor=True)
    ax.set_yticks(np.arange(-0.5, G.shape[0], 1), minor=True)
    ax.grid(which="minor", color="black", linewidth=0.2, alpha=0.25)

    ax.set_xticks([]); ax.set_yticks([])
    actual = (G != EMPTY).mean()
    ax.set_title(f"Tetromino field {G.shape[0]}×{G.shape[1]} — ρ target {rho:.2f}, actual {actual:.3f}", fontsize=10)
    plt.tight_layout(); fig.savefig(path); plt.close(fig)


def save_bw(G: np.ndarray, rho: float, path: str) -> None:
    BW = (G != EMPTY)
    fig, ax = plt.subplots(figsize=(6,6), dpi=150)
    ax.imshow(BW, cmap="gray_r", interpolation="nearest", origin="lower")
    ax.set_xticks([]); ax.set_yticks([])
    actual = BW.mean()
    ax.set_title(f"Obstacle Field {BW.shape[0]}×{BW.shape[1]} — ρ target {rho:.2f}, actual {actual:.3f}", fontsize=10)
    plt.tight_layout(); fig.savefig(path); plt.close(fig)


# ---- Main ----
def parse_args():
    p = argparse.ArgumentParser(description="RBE-550 A0 Part 2.2 — Tetromino obstacle fields")
    p.add_argument("--n", type=int, default=GRID_N)
    p.add_argument("--rho", type=float, nargs="*", default=DEFAULT_RHOS)
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--bw_only", action="store_true", help="emit only black/white images")
    return p.parse_args()


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    for rho in args.rho:
        G = f_rho_labeled(rho, args.n, rng)
        if not args.bw_only:
            save_gridded(G, rho, f"obstacles_rho_{int(round(rho*100))}_gridded.png")
        save_bw(G, rho, f"obstacles_rho_{int(round(rho*100))}.png")


if __name__ == "__main__":
    main()

