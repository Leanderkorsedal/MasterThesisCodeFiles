# ---- Plotting ---- #
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from thesis_style import apply, FULL_WIDTH
apply()

import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
# =============================================================================
# Read WAMIT .gdf quads
# =============================================================================

def _read_wamit_gdf_quads(gdf_path: str):
    """
    Reads a WAMIT-style .gdf:
      line 1: name
      line 2: ULEN GRAV ...
      line 3: ISX ISY ...
      line 4: NPAN
      then 4*NPAN vertex lines: x y z

    Returns:
      panels: (NPAN, 4, 3) float array
      isx, isy: symmetry flags (0 or 1)
    """
    with open(gdf_path, "r", errors="ignore") as f:
        lines = f.read().splitlines()

    if len(lines) < 5:
        raise RuntimeError("GDF file too short / invalid format")

    sym_parts = lines[2].split()
    isx = int(sym_parts[0])
    isy = int(sym_parts[1])

    npan = int(lines[3].split()[0])

    verts = []
    for ln in lines[4:]:
        ln = ln.strip()
        if not ln:
            continue
        parts = ln.split()
        if len(parts) >= 3:
            verts.append([float(parts[0]), float(parts[1]), float(parts[2])])

    verts = np.asarray(verts, dtype=float)
    if verts.shape[0] != 4 * npan:
        raise RuntimeError(f"Expected {4*npan} vertices, got {verts.shape[0]}")

    return verts.reshape((npan, 4, 3)), isx, isy


# =============================================================================
# Robust outline: boundary edges of waterplane mesh + ISY mirroring
# =============================================================================

def _outline_at_z_from_panels(panels: np.ndarray, z_plane: float,
                               tol: float = 1e-6, snap_decimals: int = 6,
                               isy: int = 0) -> np.ndarray:
    """
    Extract the closed ship waterplane outline at z = z_plane.

    For panels lying entirely on z_plane (waterplane mesh), boundary edges are
    found by counting: edges shared by exactly one panel are boundary edges.
    For ISY=1 (y-symmetry), the half-mesh is mirrored; centerline edges at y=0
    cancel out, leaving the full closed waterplane outline.
    """

    def snap_xy(p):
        return (round(float(p[0]), snap_decimals), round(float(p[1]), snap_decimals))

    def ekey(a, b):
        return (a, b) if a <= b else (b, a)

    # Split panels: those lying on the plane vs. those crossing it
    wp_panels = []
    cross_panels = []
    for quad in panels:
        z = quad[:, 2]
        if np.all(np.abs(z - z_plane) <= tol):
            wp_panels.append(quad)
        elif np.any(z >= z_plane - tol) and np.any(z <= z_plane + tol):
            cross_panels.append(quad)

    # --- Waterplane panels: boundary = edges appearing exactly once ---
    edge_count = Counter()
    for quad in wp_panels:
        for i in range(4):
            a = snap_xy(quad[i])
            b = snap_xy(quad[(i + 1) % 4])
            if a != b:
                edge_count[ekey(a, b)] += 1

    boundary_edges = [k for k, v in edge_count.items() if v == 1]

    # --- Fallback: intersect crossing panels if no waterplane panels found ---
    if not boundary_edges:
        cross_edge_count = Counter()
        for quad in cross_panels:
            pts = quad
            z = pts[:, 2]
            inter = []
            for i in range(4):
                p1, p2 = pts[i], pts[(i + 1) % 4]
                d1, d2 = p1[2] - z_plane, p2[2] - z_plane
                if abs(d1) <= tol and abs(d2) > tol:
                    inter.append(snap_xy(p1))
                elif abs(d2) <= tol and abs(d1) > tol:
                    inter.append(snap_xy(p2))
                elif d1 * d2 < -tol * tol:
                    t = d1 / (d1 - d2)
                    p = p1 + t * (p2 - p1)
                    inter.append(snap_xy(p))
            inter = list(dict.fromkeys(inter))
            if len(inter) == 2 and inter[0] != inter[1]:
                cross_edge_count[ekey(inter[0], inter[1])] += 1
        boundary_edges = [k for k, v in cross_edge_count.items() if v == 1]

    if not boundary_edges:
        raise RuntimeError(f"No boundary edges found at z={z_plane}")

    # --- Mirror for ISY=1: edges at y=0 appear in both halves and cancel ---
    if isy == 1:
        mirrored = [ekey((a[0], -a[1]), (b[0], -b[1])) for a, b in boundary_edges]
        combined = Counter(boundary_edges) + Counter(mirrored)
        # Centerline edges (y=0) are identical after mirroring → count=2 → remove
        boundary_edges = [k for k, v in combined.items() if v == 1]

    if not boundary_edges:
        raise RuntimeError("No boundary edges remain after ISY mirroring")

    # --- Build adjacency and walk into closed loops ---
    adj = {}
    for a, b in boundary_edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)

    visited = set()
    loops = []

    for a, b in boundary_edges:
        if ekey(a, b) in visited:
            continue

        loop = [a, b]
        visited.add(ekey(a, b))
        prev, cur = a, b

        while True:
            nxt = None
            for cand in adj.get(cur, []):
                if cand == prev:
                    continue
                if ekey(cur, cand) not in visited:
                    nxt = cand
                    break
            if nxt is None:
                break
            loop.append(nxt)
            visited.add(ekey(cur, nxt))
            prev, cur = cur, nxt
            if cur == loop[0]:
                break

        if loop[0] == loop[-1] and len(loop) >= 4:
            loops.append(loop)

    if not loops:
        raise RuntimeError("Failed to form a closed outline from boundary edges")

    def poly_area(loop):
        xy = np.asarray(loop, float)
        x, y = xy[:, 0], xy[:, 1]
        return 0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))

    outer = max(loops, key=poly_area)
    return np.asarray(outer, float)


# =============================================================================
# Your plot function
# =============================================================================

def plot(lines, gdf_path="tanker.gdf", z_level=0.0, tol=1e-6):
    fig, ax = plt.subplots(figsize=(FULL_WIDTH, FULL_WIDTH))

    fair_xy = []
    dol_xy = []

    for i, line in enumerate(lines):
        f, q = line.get_position()
        fair_xy.append([f[0], f[1]])
        dol_xy.append([q[0], q[1]])

        ax.scatter(f[0], f[1], s=60, c="b", label="Fairlead" if i == 0 else "")
        ax.scatter(q[0], q[1], s=60, c="r", label="Dolphin" if i == 0 else "")
        ax.plot([f[0], q[0]], [f[1], q[1]], "k--", linewidth=2, alpha=0.6)

    fair_xy = np.asarray(fair_xy, dtype=float) if fair_xy else np.empty((0, 2))
    dol_xy  = np.asarray(dol_xy,  dtype=float) if dol_xy  else np.empty((0, 2))

    # ---- Ship outline at chosen z level ----
    panels, _isx, isy = _read_wamit_gdf_quads(gdf_path)
    outline = _outline_at_z_from_panels(panels, z_plane=z_level, tol=tol, isy=isy)

    x_center = 0.5 * (outline[:, 0].min() + outline[:, 0].max())
    outline = outline.copy()
    outline[:, 0] -= x_center - 4.8  # shift GDF hull to SIMA global (CoG at x=0, midship at x=+4.8)

    ax.plot(outline[:, 0], outline[:, 1], linewidth=3,
            label=f"Ship outline (z={z_level:.3f})")

    all_xy = np.vstack([outline[:, :2], fair_xy, dol_xy]) if (fair_xy.size or dol_xy.size) else outline[:, :2]
    xmin, ymin = all_xy.min(axis=0)
    xmax, ymax = all_xy.max(axis=0)

    pad = 0.08 * max(xmax - xmin, ymax - ymin)
    ax.set_xlim(xmin - pad, xmax + pad)
    ax.set_ylim(ymin - pad, ymax + pad)

    ax.set_xlabel("X [m]")
    ax.set_ylabel("Y [m]")
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="lower right", fontsize=6, markerscale=0.6)

    plt.tight_layout()
    out_dir = Path(__file__).parent / "figures"
    out_dir.mkdir(exist_ok=True)
    fig.savefig(out_dir / "mooring_arrangement.pdf")
    plt.show()
