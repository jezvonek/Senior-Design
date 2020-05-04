from DistributionSetUp import FindP_WellPad1
from initialwaypoint import initwaypoint
from PathGeneration import GeneratePath
import flightdata
import numpy as np

#P, Spacing = FindP_WellPad1(Plot_P=False)
#WayPoints = initwaypoint(P, Spacing[0], Spacing[1], Spacing[2], power=10)

#write waypoints to file
#f = open("./waypoints.txt","w")
#print(WayPoints)
#np.savetxt("./waypoints.txt", WayPoints)
#for point in WayPoints:
#	f.write(str(point)+"\n")
#f.close()
FD = flightdata.FlightData()
FD.import_wellpad_components("./METEC Site Data/equipment_tags/Pad 1.kml")
for component in FD.wellpad_components:
	print(component.pos)
	print(component.name)
WayPoints = np.loadtxt("./waypoints.txt")

GeneratePath(WayPoints, FD.wellpad_components)