# Importing libraries
import numpy as np
import matplotlib.pyplot as plt

# Defining variables
E = 1.3628e+09                  # Young's modulus of mooring lines
A = 0.0855**2*np.pi/4            # Crossectional area
T0 = 0.824e5                    # Pre-tension

# Ship main dimensions
L = 250.                     # Length at waterline (Lwl)
B = 36.                      # Breadth of ship
T = 12.                     # Draught of ship
Cb = 0.71                   # Block coefficient

# Defining global coordinates origo
origo = np.zeros(3)

# Defining ship COG
COG =  np.array([-4.83, 0., 3.0])

# Creating the points for the mooring lines)
r = 35                      # Distance [m] between fairlead and quay bollard (MEG4)

# Fairlead and Mooring Bollard points
fairlead_points = np.array([
    [-125,        0,      9.0],
    [-125,        0,      9.0],
    [-104,       18,      9.0],
    [-70,        18,      9.0],
    [ 61,        18,      9.0],
    [ 85,        18,      9.0],
    [ 115,        0,      9.0],
    [ 115,        0,      9.0]
], dtype=float)

quay_dolphin_points = np.array([
    [fairlead_points[0][0] + (B/2+r  - fairlead_points[0][1]) / np.tan(150*np.pi/180),  B/2 + r,   4.0],
    [fairlead_points[1][0] + (B/2+r  - fairlead_points[1][1]) / np.tan(105*np.pi/180),  B/2 + r,   4.0],
    [fairlead_points[2][0] + (B/2+r  - fairlead_points[2][1]) / np.tan(75*np.pi/180),   B/2 + r,   4.0],
    [-10.5,                                                                                B/2 + 10,  4.0],
    [ 10.5,                                                                                B/2 + 10,  4.0],
    [fairlead_points[5][0] + (B/2+r  - fairlead_points[5][1]) / np.tan(105*np.pi/180),  B/2 + r,   4.0],
    [fairlead_points[6][0] + (B/2+r  - fairlead_points[6][1]) / np.tan(75*np.pi/180),   B/2 + r,   4.0],
    [fairlead_points[7][0] + (B/2+r  - fairlead_points[7][1]) / np.tan(30*np.pi/180),   B/2 + r,   4.0],
], dtype=float)
