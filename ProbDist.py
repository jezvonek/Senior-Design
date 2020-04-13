#initialize class with size of well pad, list of coordinates for potential leaks (components), wind speed
#need to import dave allen statistics for each type of equipment
import numpy as np 

class ProbDist:
	def __init__(self, 
		         size, #[L, W, H] dimensions of the well pad, in meters
		         grid_size, #[n_L, n_W, n_H] number of grid points in each direction
		         LeakPoints, #list of points where we are assuming there might be a point source leak
		         PointStats, #list of statistics corresponding to the probability of emission for each point in the list LeakPoints
		         v_wind): #current wind speed
		
		self.size = size;
		self.grid_size = grid_size;
		self.LeakPoints = LeakPoints;

		#find increments = [delta_l, delta_w, delta_h]
		self.increments = [];
		for i in length(size):
			self.increments.append(self.size[i]/self.grid_size[i])

		self.P = self.ComputeDistribution()
	
	def ComputeDistribution(self):
		#define empty 3d array
		for point in self.LeakPoints:
			#for i, j, k in 3D array, compute the concentration due to that leak

		#find some of value at all points and then divide each point by that number


	def WindSpeedUpdate(self, new_v_wind):

