import flightdata
from ProbDist import ProbDist
import numpy as np
import matplotlib.pyplot as plt

FD = flightdata.FlightData();
FD.import_wellpad_components("./METEC Site Data/equipment_tags/Pad 1.kml")
FD.import_inflight_measurements("./METEC Site Data/sample_uas_dataset.csv") #use this to find the size of the well pad

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

	if item.pos[2]<min_z:
		min_z = item.pos[2]
	elif item.pos[2]>max_z:
		max_z = item.pos[2]

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

#shift all coordinates
for i in range(0,len(FD.wellpad_components)):
	#add 3m to the z component of the component location since we don't have the real height of the components
	FD.wellpad_components[i].pos = FD.wellpad_components[i].pos - [min_x, min_y, min_z] + [0,0,3];

'''
FD.inflight_data['x'] = FD.inflight_data['x'] - min_x;
FD.inflight_data['y'] = FD.inflight_data['y'] - min_y;
FD.inflight_data['z'] = FD.inflight_data['z'] - min_z;
'''

#define the size of the wellpad, in meters
size = [max_x-min_x, max_y-min_y, max_z-min_z];

#try changing these numbers as necessary
grid_size = (100,100,10);

#define wind speed as initial speed
#may want to change this to use current wind speed in future
#also need to check that wind direction is defined the way we think
WindSpeed = FD.inflight_data['wind_speeds'][0];
WindDirection = FD.inflight_data['wind_directions'][0];

Dist = ProbDist(size, grid_size, FD.wellpad_components, WindSpeed, WindDirection);

#print(Dist.P)
#define a 2D array that is a layer of the probability distribution
P_layer = np.zeros((grid_size[0], grid_size[1]))
for i in range(grid_size[0]):
	for j in range(grid_size[1]):
		P_layer[i,j] = Dist.P[i,j,5];

plt.contourf(P_layer)
plt.show()