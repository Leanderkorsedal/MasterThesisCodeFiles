import numpy as np
from variables import COG, T0, E, A

# ---- Object Oriented programming ----#

class Mooringline:
    def __init__(self, fairlead_pos, quay_pos, T0, EA):
        self.fairlead0 = np.asarray(fairlead_pos, dtype=float)   # equilibrium fairlead
        self.quay_pos  = np.asarray(quay_pos, dtype=float)       # fixed quay point

        self.T0 = float(T0)
        self.EA = float(EA)

        self.L0 = np.linalg.norm(self.fairlead0 - self.quay_pos)
        self.k  = self.EA / self.L0                             # Mooring line object's spring stiffness


    def moved_fairlead(self, eta, r_ref=COG):
        eta = np.asarray(eta, dtype=float)
        dx = eta[0:3]          # surge, sway, heave
        th = eta[3:6]          # roll, pitch, yaw (rad)

        r = self.fairlead0 - np.asarray(r_ref, dtype=float)
        s = dx + np.cross(th, r)     # point displacement from rigid body motion

        return self.fairlead0 + s

    
    # Get positions of line ends
    def get_position(self):
        return self.fairlead0, self.quay_pos
    
    # Calculate force and moment contributions after applying a displacement
    def force_and_moment(self, eta, r0=COG):
        p = self.moved_fairlead(eta, r_ref=r0)
        q = self.quay_pos
    
        l_vec = q - p
        l = np.linalg.norm(l_vec)
        u = l_vec / (l + 1e-12)
    
        T = self.T0 + self.k * (l - self.L0)
        if T < 0.0:
            T = 0.0  # tension-only (valgfritt, men ofte fysisk nødvendig)
    
        F = T * u
    
        # Bruk konstant momentarm fra likevekt (konsistent med linear_stiffness_6x6)
        r = self.fairlead0 - np.asarray(r0, float)
        M = np.cross(r, F)
        return F, M

    
    def linear_stiffness_6x6(self, r0=COG):
        # Equilibrium geometry
        p0 = self.fairlead0
        q0 = self.quay_pos
        lvec = q0 - p0
        l0 = np.linalg.norm(lvec)
        u0 = lvec / (l0 + 1e-12)
    
        I3 = np.eye(3)
    
        # 3x3 stiffness at the fairlead (taut linear line)
        K3 = self.k * np.outer(u0, u0) + (self.T0 / (l0 + 1e-12)) * (I3 - np.outer(u0, u0))
    
        # Map 6DOF motion at reference point r0 to point displacement at fairlead:
        # dp = J * eta where eta=[dx,dy,dz,phi,theta,psi]
        r = p0 - np.asarray(r0, dtype=float)
    
        def skew(a):
            ax, ay, az = a
            return np.array([[0, -az, ay],
                             [az, 0, -ax],
                             [-ay, ax, 0]], dtype=float)
    
        J = np.hstack([I3, -skew(r)])  # 3x6
    
        # 6x6 generalized stiffness contribution from this line
        K6 = J.T @ K3 @ J
        return K6

# Creating object instances of Mooringline
def initMooring(fairlead, quay_dolphin):

    lines = [
        Mooringline(fairlead_pos=fp, quay_pos=qp, T0=T0, EA=E*A)

        for fp, qp in zip(fairlead, quay_dolphin)
    ]

    return lines
