import numpy as np
import math

class LeakPresent:

    def __init__(self, Q, sigmay, sigmaz, u, H):
        """Initializes concentration model object

        Parameters
        ----------
        Q : float
            Flow rate
        sigmay : float
            Standard deviation along y-axis
        sigmaz : float
            Standard deviation along z-axis
        u : float
            Wind speed
        H : float
            Height of point source

        """

        self.Q = Q 
        self.sigmay = sigmay
        self.sigmaz = sigmaz
        self.u = u 
        self.H = H

    def predict(self, point):
        """Takes location downstream of emission source and returns expected
        concentration value

        Parameters
        ----------
        point : np.array
            NumPy array of length 3, representing the (x,y,z) coordinates of
            the point in question

        Returns
        ----------
        float
            Predicted concentration value

        """

        x = point[0]
        y = point[1]
        z = point[2]
        frac = self.Q / (2 * math.pi * self.sigmay * self.sigmaz * self.u)
        first = math.exp(-((y/self.sigmay)**2)/2)
        second = math.exp(-(((z-self.H)/self.sigmay)**2)/2)
        third = math.exp(-(((z+self.H)/self.sigmay)**2)/2)

        return frac * first * (second + third)