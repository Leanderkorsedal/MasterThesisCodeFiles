import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def read_gdf(path: str):
    """
    Reads a WAMIT-style .gdf:
      line 1: name/description
      line 2: ULEN GRAV
      line 3: ISX ISY
      line 4: number of panels (N)
      then 4*N lines of XYZ points (4 points per panel)

    Returns:
      header (dict), panels (np.ndarray of shape (N,4,3))
    """
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        name = f.readline().strip()
        ulen_grav = f.readline().strip()
        isx_isy = f.readline().strip()
        n_panels_line = f.readline().strip()

        try:
            n_panels = int(n_panels_line.split()[0])
        except ValueError as e:
            raise ValueError(f"Could not parse number of panels from line: {n_panels_line!r}") from e

        # Load remaining numeric data (should be 4*n_panels rows, 3 columns)
        data = np.loadtxt(f)

    expected_rows = 4 * n_panels
    if data.shape[0] != expected_rows or data.shape[1] != 3:
        raise ValueError(
            f"Unexpected data shape {data.shape}. Expected ({expected_rows}, 3). "
            f"(Check file formatting / panel count.)"
        )

    panels = data.reshape(n_panels, 4, 3)

    header = {
        "name": name,
        "ulen_grav": ulen_grav,
        "isx_isy": isx_isy,
        "n_panels": n_panels,
    }
    return header, panels


def set_axes_equal(ax):
    """Make 3D axes have equal scale so geometry isn't distorted."""
    x_limits = ax.get_xlim3d()
    y_limits = ax.get_ylim3d()
    z_limits = ax.get_zlim3d()

    x_range = abs(x_limits[1] - x_limits[0])
    y_range = abs(y_limits[1] - y_limits[0])
    z_range = abs(z_limits[1] - z_limits[0])

    x_mid = np.mean(x_limits)
    y_mid = np.mean(y_limits)
    z_mid = np.mean(z_limits)

    plot_radius = 0.5 * max([x_range, y_range, z_range])

    ax.set_xlim3d([x_mid - plot_radius, x_mid + plot_radius])
    ax.set_ylim3d([y_mid - plot_radius, y_mid + plot_radius])
    ax.set_zlim3d([z_mid - plot_radius, z_mid + plot_radius])


def plot_gdf(panels, title="GDF mesh", show_edges=False, max_panels=None):
    """
    panels: (N,4,3)
    show_edges: draw panel edges (slower)
    max_panels: if set, plot only the first max_panels panels for speed
    """
    if max_panels is not None and panels.shape[0] > max_panels:
        panels_to_plot = panels[:max_panels]
        title = f"{title} (showing {max_panels}/{panels.shape[0]} panels)"
    else:
        panels_to_plot = panels

    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    poly = Poly3DCollection(
        panels_to_plot,
        linewidths=0.2 if show_edges else 0.0,
        edgecolor="k" if show_edges else "none",
        alpha=0.85,
    )
    ax.add_collection3d(poly)

    # Autoscale to the data bounds
    xyz = panels_to_plot.reshape(-1, 3)
    ax.set_xlim(xyz[:, 0].min(), xyz[:, 0].max())
    ax.set_ylim(xyz[:, 1].min(), xyz[:, 1].max())
    ax.set_zlim(xyz[:, 2].min(), xyz[:, 2].max())
    set_axes_equal(ax)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")

    plt.tight_layout()
    safe_title = "".join(c if c.isalnum() or c in " _-" else "_" for c in title).strip()
    plt.savefig(f"{safe_title}.pdf", bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    path = "RemeshedManifold.gdf"  # <-- change to your file path
    header, panels = read_gdf(path)

    print("Header:")
    for k, v in header.items():
        print(f"  {k}: {v}")

    # Fast surface view (no edges)
    plot_gdf(panels, title=header["name"], show_edges=False)

    # If you want edges (slower), try:
    # plot_gdf(panels, title=header["name"], show_edges=True, max_panels=3000)
