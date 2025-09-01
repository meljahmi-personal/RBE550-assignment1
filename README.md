# RBE-550 Assignment 1 – Turtle Graphics & Obstacle Fields

## Overview
This repository contains my solutions for **Assignment 1 (TURTLES)** in RBE-550 Motion Planning.

The assignment has two parts:

1. **Victor Sierra Search Pattern**  
   - Implemented using Python’s `turtle` graphics.  
   - Three separate scripts produce different layouts of the search pattern:  
     - `zigzag_pattern.py` – zigzag layout  
     - `radial_pattern.py` – radial layout  
     - `linear_pattern.py` – linear layout  
   - Each script draws **three equilateral triangles** and encloses them with a **dashed circle** (search boundary).  
   - Output is saved as `.eps` images.

2. **Obstacle Fields**  
   - Implemented in `meljahmi_hw1_part2-2.py`.  
   - Generates random obstacle fields on a 128×128 grid using tetromino shapes (I, L, S, T).  
   - Coverage levels (ρ) of 10%, 50%, and 70% are supported.  
   - Outputs **black/white EPS images** (required). PNG is optional.  
   - These outputs correspond directly to *Figure 3* in the assignment handout.

---

## Requirements
- Python 3.10.12  
- OS: Ubuntu 22.04, Linux kernel 6.8.0-78-generic  
- Standard library: `turtle`, `math`  
- Additional libraries (for obstacles): `numpy`, `matplotlib`  

The full environment is listed in [`requirements.txt`](requirements.txt).

---

## Setting Up a Virtual Environment

It is best practice to install dependencies inside a **virtual environment** so they don’t interfere with system packages.

1. Create a new virtual environment (Python 3.10+):
   ```bash
   python3 -m venv venv
   ```

2. Activate the environment:
   - On Linux/macOS:
     ```bash
     source venv/bin/activate
     ```
   - On Windows (PowerShell):
     ```powershell
     venv\Scripts\Activate.ps1
     ```

3. Install dependencies from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

4. When finished, deactivate:
   ```bash
   deactivate
   ```

---

## Running the Code

### Victor Sierra Search Patterns
Run the scripts separately:
```bash
python3 zigzag_pattern.py
python3 radial_pattern.py
python3 linear_pattern.py
```

Or run all of them at once (if `run_patterns.sh` is executable):
```bash
./run_patterns.sh
```

Each script saves its output as:
- `victor_sierra_zigzag.eps`
- `victor_sierra_radial.eps`
- `victor_sierra_linear.eps`

---

### Obstacle Fields
Run the obstacle generator:
```bash
python3 meljahmi_hw1_part2-2.py
```

This will generate fields with default coverage rates ρ = 0.10, 0.50, 0.70.

Options:
```bash
--rho <floats>    # custom coverage (e.g. --rho 0.25 0.40)
--n <int>         # grid size (default 128 for 128×128)
--seed <int>      # random seed for reproducibility
--outdir <path>   # output directory
--png             # also save PNG files (in addition to EPS)
```

#### Coverage ρ explained
Coverage is the fraction of grid cells occupied by tetromino obstacles:

- Grid = 128×128 = 16,384 cells.  
- ρ = 0.10 → ~1,638 cells occupied.  
- ρ = 0.50 → ~8,192 cells occupied.  
- ρ = 0.70 → ~11,468 cells occupied.  

The script also reports the **actual coverage** in each figure title.

#### Usage
```bash
# Default: produces EPS for ρ = 0.10, 0.50, 0.70
python3 meljahmi_hw1_part2-2.py

# Also save PNGs (optional)
python3 meljahmi_hw1_part2-2.py --png

# Custom coverage and grid size
python3 meljahmi_hw1_part2-2.py --rho 0.25 0.40 --n 96 --png
```

#### Outputs
- Black/white EPS images: `obstacles_rho_10.eps`, `obstacles_rho_50.eps`, `obstacles_rho_70.eps`  
- (Optional) PNG images: `obstacles_rho_10.png`, `obstacles_rho_50.png`, `obstacles_rho_70.png`  
