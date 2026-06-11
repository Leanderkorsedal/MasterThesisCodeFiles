from objects import initMooring
import plot
import pandas as pd
from variables import fairlead_points, quay_dolphin_points
from calculation import calculateStiffness

# Creating objects
lines = initMooring(fairlead_points, quay_dolphin_points)

# Calculate stiffness
K = calculateStiffness(lines)

# Save K to CSV
pd.DataFrame(K).to_csv("K_Matrix.csv", index=False, header=False)

# Plot
plot.plot(lines, gdf_path="tanker.gdf", z_level=0.0)
