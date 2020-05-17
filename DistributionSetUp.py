import flightdata
from ProbDist import ProbDist
import numpy as np
import matplotlib.pyplot as plt

def FindP_WellPad(Plot_P = True, WellPadNumber = 1, WindSpeed = 2, WindDirection = 0):
	#Plot_P is a boolean that determines whether or not the probability distribution is plotted
	FD = flightdata.FlightData();
	FD.import_wellpad_components("./METEC Site Data/equipment_tags/Pad {}.kml".format(WellPadNumber))
	#FD.import_inflight_measurements("./METEC Site Data/sample_uas_dataset.csv") #use this to find the size of the well pad

	#determine the range of the coordinates so that we can shift them to make all coordinates (i*delta_x, j*delta_y, k*delta_z)
	min_x =0; min_y=0; min_z = 0; 
	max_x=0; max_y=0; max_z=0;

	for item in FD.wellpad_components:
		if item.pos[0]<min_x:
			min_x = item.pos[0]
		elif item.pos[0]>max_x:
			max_x = item.pos[0]

		if item.pos[1]<min_y:
			min_y = item.pos[1]
		elif item.pos[1]>max_y:
			max_y = item.pos[1]

		if item.pos[2]>max_z:
			max_z = item.pos[2]

	"""
	for item in FD.inflight_data['x']:
		if item<min_x:
			min_x = item;
		elif item>max_x:
			max_x = item;

	for item in FD.inflight_data['y']:
		if item<min_y:
			min_y = item;
		elif item>max_y:
			max_y = item;

	for item in FD.inflight_data['z']:
		if item<min_z:
			min_z = item;
		elif item>max_z:
			max_z = item;
	"""

	#shift all coordinates
	Shift = [min_x-40, min_y-40,0];
	for i in range(0,len(FD.wellpad_components)):
		#add 3m to the z component of the component location since we don't have the real height of the components
		FD.wellpad_components[i].pos = FD.wellpad_components[i].pos - Shift + [0,0,3];

	'''
	FD.inflight_data['x'] = FD.inflight_data['x'] - min_x;
	FD.inflight_data['y'] = FD.inflight_data['y'] - min_y;
	FD.inflight_data['z'] = FD.inflight_data['z'] - min_z;
	'''

	#define the size of the wellpad, in meters
	size = [max_x-(min_x)+60, max_y-(min_y)+60, max_z+6];
	print(size)

	#try changing these numbers as necessary
	grid_size = (200,200,20);

	#define wind speed as initial speed
	#may want to change this to use current wind speed in future
	#also need to check that wind direction is defined the way we think
	if WellPadNumber == 1:
		WindSpeed = FD.inflight_data['wind_speeds'][0];
		WindDirection = FD.inflight_data['wind_directions'][0];

	Dist = ProbDist(size, grid_size, FD.wellpad_components, WindSpeed, WindDirection);
	Spacing = [size[0]/grid_size[0], size[1]/grid_size[1], size[2]/grid_size[2]];

	if Plot_P:
		#define a 2D array that is a layer of the probability distribution
		P_layer = np.zeros((grid_size[0], grid_size[1]))
		for i in range(grid_size[0]):
			for j in range(grid_size[1]):
				P_layer[i,j] = Dist.P[i,j,9];

		X = np.zeros(grid_size[0])
		Y = np.zeros(grid_size[1])

		for i in range(grid_size[0]): 
			X[i] = i*Spacing[0] + Shift[0];
		for j in range(grid_size[1]): 
			Y[j] = j*Spacing[1] + Shift[1];

		Xm, Ym = np.meshgrid(X,Y,indexing='ij')
		plt.contourf(Xm,Ym, P_layer)
		plt.colorbar()
		for item in FD.wellpad_components:
			plt.plot(item.pos[0]+Shift[0], item.pos[1]+Shift[1],'ko')
		plt.xlabel('x (m)')
		plt.ylabel('y (m)')
		plt.title('Initial Probability Distribution for Well Pad {}'.format(WellPadNumber))
		plt.show()

	return Dist.P, Spacing, Shift
