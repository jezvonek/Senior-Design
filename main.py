from DistributionSetUp import FindP_WellPad
from initialwaypoint import initwaypoint
from PathGeneration import GeneratePath
import flightdata
import numpy as np

P, Spacing, Shift = FindP_WellPad(Plot_P=False, WellPadNumber = 2)
WayPoints = initwaypoint(P, Spacing[0], Spacing[1], Spacing[2], power=10)

#shift coordinates back
for i in range(len(WayPoints)):
	WayPoints[i][0] = WayPoints[i][0] + Shift[0];
	WayPoints[i][1] = WayPoints[i][1] + Shift[1];
	#f.write(str(point)+"\n")

#write waypoints to file
f = open("./waypoints2.txt","w")
#print(WayPoints)
np.savetxt("./waypoints2.txt", WayPoints)

f.close()
"""

FD = flightdata.FlightData()
FD.import_wellpad_components("./METEC Site Data/equipment_tags/Pad 1.kml")
for component in FD.wellpad_components:
	print(component.pos)
	print(component.name)
WayPoints = np.loadtxt("./waypoints.txt")

GeneratePath(WayPoints, FD.wellpad_components)
"""