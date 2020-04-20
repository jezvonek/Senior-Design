import numpy as np
import math

class LeakPresent:

    def __init__(self, Q, sigmay, sigmaz, H):
        """Initializes concentration model object

        Parameters
        ----------
        Q : float
            Flow rate
        sigmay : float
            Standard deviation along y-axis
        sigmaz : float
            Standard deviation along z-axis
        H : float
            Height of point source

        """

        self.Q = Q 
        self.sigmay = sigmay
        self.sigmaz = sigmaz
        self.H = H

    def predict_local_coors(self, point, source, wind_speed, wind_direction):
        """Using a point in global coordinates, transforms the point into local
        coordinates and returns the prediction

        Parameters
        ----------
        point : np.array
            NumPy array of length 3, representing the (x,y,z) coordinates of
            the point in question. Point given in global coordinates
        source : np.array
            NumPy array of length 3, representing the (x,y,z) coordinates of
            the emission source in question. Point given in global coordinates
        wind_speed : float
            Wind speed
        wind_direction : float
            Angle of wind direction in degrees, with 0 being along the x-axis,
            90 along the y-axis, and so on

        Returns
        ----------
        float
            Predicted concentration value

        """

        angle_rad = - wind_direction * 180 / math.pi

        point = point - source
        rot_point = point
        rot_point[0] = point[0] * math.cos(angle_rad) - point[1] * math.sin(angle_rad)
        rot_point[1] = point[1] * math.cos(angle_rad) + point[0] * math.sin(angle_rad)

        return self.predict_wind_coors(rot_point, wind_speed)

    def predict_wind_coors(self, point, u):
        """Takes location downstream of emission source and returns expected
        concentration value

        Parameters
        ----------
        point : np.array
            NumPy array of length 3, representing the (x,y,z) coordinates of
            the point in question
        u : float
            Wind speed

        Returns
        ----------
        float
            Predicted concentration value

        """

        x = point[0]
        y = point[1]
        z = point[2]
        frac = self.Q / (2 * math.pi * self.sigmay * self.sigmaz * u)
        first = math.exp(-((y/self.sigmay)**2)/2)
        second = math.exp(-(((z-self.H)/self.sigmay)**2)/2)
        third = math.exp(-(((z+self.H)/self.sigmay)**2)/2)

        return frac * first * (second + third)