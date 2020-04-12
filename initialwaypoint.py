import numpy as n

"""
Initial Waypoint Creation
finds the local maxima of the probability array using the argrelmax function of scipy and returns a 2D array of the coordinates of the waypoints
inputs:     prob    -   probability array of the well-pad (3D numpy array of any size)
           xspacing -   spacing in the x direction
           yspacing -   spacing in the y direction
           zspacing -   spacing in the z direction
            power   -   the radius / window size of comparison for the argrelmax check, with a default value of 1 (must be an int)
outputs:    wps     -   array containing the coordinates of the waypoints 
"""

def initwaypoint(prob, xspacing, yspacing, zspacing, power=1):

    # ----------------------
    # Variable Instantiation
    # ----------------------

    first = True                                                                                        # boolean value of whether this is the first entry in the waypoints array
    comp = n.empty([n.shape(prob)[0], n.shape(prob)[1], n.shape(prob)[2], power], dtype = bool)         # preallocate the comparison array

    # ------
    # Engine
    # ------
    
    # perform the comparisons for each power level
    for i in range(0,power):
        comp[:,:,:,i] = ((prob >= n.roll(prob, i+1, 0)) & (prob >= n.roll(prob, -1*(i+1), 0)) & (prob >= n.roll(prob,  i+1, 1)) & (prob >= n.roll(prob, -1*(i+1), 1)) & (prob >= n.roll(prob,  i+1, 2)) & (prob >= n.roll(prob, -1*(i+1), 2)))

    # find the coordinates of the maxima based on the indices of the comparison array
    for i in range(0,n.shape(prob)[0]):                             # loop over the coordinate indices
        for j in range(0, n.shape(prob)[1]):
            for k in range(0, n.shape(prob)[2]):
                # find whether the index is a local maxima by &ing all the individual coordinate layers of the comparison matrix together
                temp = comp[i,j,k,0]
                if not(power == 1):
                    for l in range(0, power):                       # loop over the window sizes if greater than 1
                        temp = temp & comp[i,j,k,l]

                # if the point is a local maxima, add to waypoints array
                if temp:
                    if first:                                                                           # if this is the first entry in wps, create wps
                        first = False
                        wps = n.array([[i*xspacing, j*yspacing, k*zspacing]])
                    else:
                        wps = n.append(wps, [[i*xspacing, j*yspacing, k*zspacing]], axis=0)

    return wps
