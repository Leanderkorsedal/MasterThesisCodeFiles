import numpy as np
from variables import COG

# ---- CALCULATION of Mooring Stiffness ---- # =======================================================================================

# Stiffness matrix initialization
ndofs = 6
K = np.zeros((ndofs, ndofs))

def calculateStiffness(lines, r0=COG):
    K = np.zeros((6, 6))
    for line in lines:
        K += line.linear_stiffness_6x6(r0=r0)
    return K

#=====================================================================================================================================
                        


