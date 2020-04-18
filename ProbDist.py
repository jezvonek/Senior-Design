#initialize class with size of well pad, list of coordinates for potential leaks (components), wind speed
#need to import dave allen statistics for each type of equipment
import numpy as np 

class ProbDist:
	def __init__(self, 
		         size, #[L, W, H] dimensions of the well pad, in meters
		         grid_size, #(n_L, n_W, n_H) tuple with number of grid points in each direction
		         LeakPoints, #list of points where we are assuming there might be a point source leak
		         PointStats, #list of statistics corresponding to the probability of emission for each point in the list LeakPoints
		         v_wind, #current wind speed
		         wind_dir, #current wind direction; we assume this is a unit vector in the xy-plane
		         Sigma): #[sigma_y, sigma_z] standard deviations corresponding to the dispersion model
		
		self.size = size;
		self.grid_size = grid_size;
		self.LeakPoints = LeakPoints;
		self.PointStats = PointStats;
		self.v_wind = v_wind;
		self.wind_dir = wind_dir;
		self.Sigma = Sigma;

		#find increments = [delta_l, delta_w, delta_h]
		self.increments = [];
		for i in length(size):
			self.increments.append(size[i]/grid_size[i])

		self.P = self.ComputeDistribution()
	
	def ComputeDistribution(self):
		#define empty 3d array
		P = np.zeros(grid_size);

		#define standard deviations in y and z directions
		sigma_y = Sigma[0];
		sigma_z = Sigma[1];

		#for point in self.LeakPoints:
			#for i, j, k in 3D array, compute the concentration due to that leak
		for n in length(self.LeakPoints):
			LP = self.LeakPoints(n);
			H = LP[2]; #this should be at half the height of the equipment
			Stat = self.PointStats(n);
			
			for i in grid_size[0]:
				for j in grid_size[1]:
					for k in grid_size[2]:
						#find x,y,z in well pad coordinate system
						x_temp = i*self.increments[0] - LP[0];
						y_temp = j*self.increments[1] - LP[1];
						z = k*self.increments[2];

						#now convert the x,y,z to the coordinate system defined by Hodgkinson et al.
						x = self.wind_dir[0]*x_temp + self.wind_dir[1]*y_temp;
						y = -self.wind_dir[1]*x_temp + self.wind_dir[0]*y_temp;

						#weight the distribution by the statistics given from Allen et al.
						P[i,j,k] = P[i,j,k] + Stat/(2*np.pi*sigma_y*sigma_z*self.v_wind)*np.exp(-0.5*(y/sigma_y)^2)*(np.exp(-0.5*((z-H)/sigma_z)^2) + np.exp(-0.5*((z+H)/sigma_z)^2));


		#find some of value at all points and then divide each point by that number
		Scale = np.sum(P);
		P = P/Scale; #divide the probability distribution by the sum of its elements so that the sum of the probabilities for each point is 1

		return P

	def WindSpeedUpdate(self, new_v_wind, new_wind_dir):
		self.v_wind = new_v_wind;
		self.wind_dir = new_wind_dir;

		self.P = self.ComputeDistribution()

	def GetProb(self, x,y,z):
		#check that x,y,z are in the grid
		if not (0<=x<=self.size[0] and 0<=y<=self.size[1] and 0<=z<=self.size[2]):
			raise Exception('Coordinates are not within the well pad region.')

		#find the closest indices corresponding to x,y,z
		i = floor(x/self.increments[0])
		j = floor(y/self.increments[1])
		k = floor(z/self.increments[2])

		Prob = self.P[i,j,k]

		return Prob

	#for if/when we do the Bayesian inference update
	# def DistUpdate(self,MethaneData):