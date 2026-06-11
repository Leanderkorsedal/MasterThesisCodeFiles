"""
thesis_style.py
---------------
Matplotlib style settings matching the Overleaf thesis.

Usage (top of every notebook / script):
    from thesis_style import apply, FULL_WIDTH, HALF_WIDTH, THIRD_WIDTH
    apply()

Figure widths (in inches) based on thesis text width ~145 mm (5.72 in):
    FULL_WIDTH  : spans the full text column
    HALF_WIDTH  : two figures side by side
    THIRD_WIDTH : three figures side by side
"""

import shutil

import matplotlib as mpl
import matplotlib.pyplot as plt
from pathlib import Path

# LaTeX text rendering needs a LaTeX installation; fall back to mathtext if absent
_HAS_LATEX = shutil.which("latex") is not None

# ── Figure widths ──────────────────────────────────────────────────────────────
FULL_WIDTH  = 5.72   # inches  (≈ 145 mm)
HALF_WIDTH  = 2.76   # inches  (≈  70 mm)
THIRD_WIDTH = 1.79   # inches  (≈  45 mm)

def full(height_ratio=0.6):
    """Return (width, height) for a full-width figure."""
    return (FULL_WIDTH, FULL_WIDTH * height_ratio)

def half(height_ratio=0.8):
    """Return (width, height) for a half-width figure."""
    return (HALF_WIDTH, HALF_WIDTH * height_ratio)

# ── Apply style ────────────────────────────────────────────────────────────────
def apply():
    """Apply thesis-consistent rcParams to the current session."""
    mpl.rcParams.update({
        # --- Font ---
        "font.family":        "serif",
        "font.serif":         ["Latin Modern Roman"],
        "font.size":          10,

        # --- LaTeX rendering ---
        "text.usetex":        _HAS_LATEX,
        "text.latex.preamble": r"\usepackage{lmodern}\usepackage{amsmath}",

        # --- Axes ---
        "axes.labelsize":     10,
        "axes.titlesize":     10,
        "axes.linewidth":     0.8,
        "axes.grid":          True,
        "grid.linewidth":     0.4,
        "grid.alpha":         0.5,
        "grid.linestyle":     "--",

        # --- Ticks ---
        "xtick.labelsize":    9,
        "ytick.labelsize":    9,
        "xtick.direction":    "in",
        "ytick.direction":    "in",
        "xtick.major.width":  0.8,
        "ytick.major.width":  0.8,
        "xtick.minor.visible": False,
        "ytick.minor.visible": False,

        # --- Lines ---
        "lines.linewidth":    1.5,
        "lines.markersize":   4,

        # --- Legend ---
        "legend.fontsize":    9,
        "legend.framealpha":  0.9,
        "legend.edgecolor":   "0.8",

        # --- Figure ---
        "figure.figsize":     (FULL_WIDTH, FULL_WIDTH * 0.6),
        "figure.dpi":         150,
        "savefig.dpi":        300,
        "savefig.bbox":       "tight",
        "savefig.pad_inches": 0.02,
        "savefig.format":     "pdf",
    })


def save(fig, name: str, subdir: str = "figures"):
    """Save fig as a PDF into <cwd>/<subdir>/<name>.pdf, creating the folder if needed."""
    out = Path.cwd() / subdir
    out.mkdir(exist_ok=True)
    fig.savefig(out / f"{name}.pdf")
