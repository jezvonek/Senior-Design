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
    comp = n.empty([n.shape(prob)[0], n.shape(prob)[1], n.shape(prob)[2]], dtype = bool)                # preallocate the comparison array
    # fill the comp array
    for i in range(0,n.shape(prob)[0]):                     
        for j in range(0,n.shape(prob)[1]):
            for k in range(0,n.shape(prob)[2]):
                comp[i,j,k] = True
    wps = n.zeros([1,3])                                                                              # instantiate the wps array

    # ------
    # Engine
    # ------

    # perform the comparisons for each power level
    for i in range(0,n.shape(prob)[0]):                     # loop over the points
        for j in range(0,n.shape(prob)[1]):
            for k in range(0,n.shape(prob)[2]):
                for x in range(-1*power, power + 1):        # loop over the window
                    compx = i + x
                    if (compx >= 0) and (compx < n.shape(prob)[0]):
                        for y in range(-1*power, power + 1):
                            compy = j + y
                            if (compy >= 0) and (compy < n.shape(prob)[1]):
                                for z in range(-1*power, power + 1):
                                    compz = k + z
                                    if (compz >= 0) and (compz < n.shape(prob)[2]):
                                        if comp[i,j,k]:
                                            comp[i,j,k] = comp[i,j,k] & (prob[i,j,k] >= prob[compx, compy, compz])

    # find the coordinates of the maxima based on the indices of the comparison array
    for i in range(0,n.shape(prob)[0]):                             # loop over the coordinate indices
        for j in range(0, n.shape(prob)[1]):
            for k in range(0, n.shape(prob)[2]):
                if comp[i,j,k]:
                    if first:
                        first = False
                        wps = n.array([[i*xspacing, j*yspacing, k*zspacing]])
                    else:
                        wps = n.append(wps, [[i*xspacing, j*yspacing, k*zspacing]], axis=0)     

    return wps
