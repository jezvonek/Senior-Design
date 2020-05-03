import numpy as np
import math

class LeakPresent:

    def __init__(self, Q, H, atmosphere='normal'):
        """Initializes concentration model object

        Parameters
        ----------
        Q : float
            Flow rate
        H : float
            Height of point source
        atmosphere : string, optional
            State of the atmosphere. Either 'unstable', 'neutral', or 'stable'

        """

        self.Q = Q 
        self.H = H
        self.atmosphere = atmosphere

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
        if x > 0:
            y = point[1]
            z = point[2]

            sigmay, sigmaz = self.get_sigma_values(x)

            frac = self.Q / (2 * math.pi * sigmay * sigmaz * u)
            first = math.exp(-((y/sigmay)**2)/2)
            second = math.exp(-(((z-self.H)/sigmay)**2)/2)
            third = math.exp(-(((z+self.H)/sigmay)**2)/2)

            return frac * first * (second + third)
        else:
            return 0

    def get_sigma_values(self, x):
        if self.atmosphere == 'unstable':
            sigmay = 0.493 * (x ** 0.88)
            sigmaz = 0.087 * (x ** 1.10)
        elif self.atmosphere == 'normal':
            sigmay = 0.128 * (x ** 0.90)
            sigmaz = 0.093 * (x ** 0.85)
        elif self.atmosphere == 'stable':
            sigmay = 0.067 * (x ** 0.90)
            sigmaz = 0.057 * (x ** 0.80)

        return sigmay, sigmaz
