from DistributionSetUp import FindP_WellPad1
from initialwaypoint import initwaypoint

P, Spacing = FindP_WellPad1(Plot_P=False);
WayPoints = initwaypoint(P, Spacing[0], Spacing[1], Spacing[2], power=10)

#write waypoints to file
f = open("./waypoints.txt","w")
for point in WayPoints:
	f.write(str(point)+"\n")
f.close()