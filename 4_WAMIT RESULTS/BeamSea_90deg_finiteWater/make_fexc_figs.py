"""Generate first-order wave excitation-force figures (one per DOF) for the appendix,
matching the style of the RAO figures in Response_AllHeadings.ipynb."""
import os
import re
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)                       # so save() writes into ./figures next to the RAO PDFs
sys.path.insert(0, BASE)
from thesis_style import apply, full, save
apply()

WAMIT_ROOT = os.path.join(BASE, "WAMIT_Results")

# --- Identical heading -> colour/linestyle mapping as the RAO figures in Response_AllHeadings.ipynb ---
COLORS = {"0°": "#003f88", "45°": "#0096c7", "90°": "#2d8653",
          "135°": "#e76f51", "180°": "#c1121f"}
LS = {"0°": "-", "45°": (0, (6, 1.5)), "90°": (0, (2, 1.5)),
      "135°": (0, (4, 1.5, 1, 1.5)), "180°": (0, (1, 1.5))}
HEADINGS = {"0°": ("0deg", "0"), "45°": ("45deg", "45"), "90°": ("90deg", "90"),
            "135°": ("135deg", "135"), "180°": ("180deg", "180")}

DOF_NAMES  = ["surge", "sway", "heave", "roll", "pitch", "yaw"]
DOF_LABELS = ["Surge", "Sway", "Heave", "Roll", "Pitch", "Yaw"]


def load_fexc(folder, hdg, dof):
    """Return (omega, magnitude, unit_string) for one heading/DOF CSV."""
    path = os.path.join(WAMIT_ROOT, folder, "Fexc",
                        f"Excitation Force 1_{dof} heading {hdg}_0o mag.csv")
    df = pd.read_csv(path, sep=";", skiprows=1, encoding="utf-8")
    omega = df.iloc[:, 0].to_numpy(dtype=float)
    mag   = df.iloc[:, 1].to_numpy(dtype=float)
    m = re.search(r"\[(.*?)\]", str(df.columns[1]))   # unit between [ ]
    unit = m.group(1).strip() if m else ""
    return omega, mag, unit


def is_moment(unit):
    """Classify force vs moment from the header unit (N/m -> force, Nm/m -> moment)."""
    base = unit.split("/")[0].strip().lower().replace("*", "").replace("·", "").replace(" ", "")
    return base in ("nm", "nmm")        # 'nm' = Nm (moment); 'n' = N (force)


# Sanity-check accumulators
peak = {}

for j, dof in enumerate(DOF_NAMES):
    fig, ax = plt.subplots(figsize=full())
    unit_seen = None
    for label, (folder, hdg) in HEADINGS.items():
        omega, mag, unit = load_fexc(folder, hdg, dof)
        unit_seen = unit
        ax.plot(omega, mag / 1000.0, color=COLORS[label], ls=LS[label], lw=1.5, label=label)
        peak[(dof, label)] = mag.max()

    if is_moment(unit_seen):
        ylabel = r"Excitation moment [kN$\cdot$m/m]"
    else:
        ylabel = r"Excitation force [kN/m]"

    ax.set_xlabel(r"$\omega$ [rad/s]")
    ax.set_ylabel(ylabel)
    ax.legend(title="Wave heading")
    plt.tight_layout()
    save(fig, f"Fexc_{dof}")
    plt.close(fig)
    print(f"saved figures/Fexc_{dof}.pdf   (unit '{unit_seen}' -> "
          f"{'moment' if is_moment(unit_seen) else 'force'})")

# ---- Sanity check ----
print("\n=== Sanity check (peak magnitudes) ===")
print(f"Sway  @ 90°  : {peak[('sway','90°')]/1000:,.1f} kN/m")
print(f"Surge @ 0°   : {peak[('surge','0°')]/1000:,.1f} kN/m")
print(f"Surge @ 180° : {peak[('surge','180°')]/1000:,.1f} kN/m")
ratio0   = peak[('sway','90°')] / peak[('surge','0°')]
ratio180 = peak[('sway','90°')] / peak[('surge','180°')]
print(f"Sway@90 / Surge@0   = {ratio0:.1f}x")
print(f"Sway@90 / Surge@180 = {ratio180:.1f}x")
