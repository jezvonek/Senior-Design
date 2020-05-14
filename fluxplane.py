import math as m
import numpy as n

"""
Closest Object
find the coords of the potential leak source closest to the current position of the drone
inputs      x           - the current x position of the drone (m)
            y           - the current y position of the drone (m)
            z           - the current z position of the drone (m)
            objs        - 2D array containing the coordinates of the objects on the wellpad (m) ([i,j] i = object ID, j = coordinate (x=0,y=1,z=2))
outputs     cObj        - 1D array of the coordinates of the closest object (m) (x=0,y=1,z=2)
"""

def getClosestObject(x, y, z, objs):

    # ----------------------
    # Variable Instantiation
    # ----------------------

    cObj = n.zeros([3])                                 # preallocate the cObj array
    shortest = float('inf')                             # the current shortest distance
    closestObj = 0                                      # the index (ID) of the closest object to the drone

    # ------------
    # Computations
    # ------------
    
    for i in range(0,n.shape(objs)[0]):                 # loop over all the objects
        dis = m.sqrt((objs[i,0] - x)**2 + (objs[i,1] - y)**2 + (objs[i,2] - z)**2)             # find the distance between the drone and the current object
        if dis < shortest:                                                                  # if the object is the current closest, save the distance in shortest and ID in closestObj
            shortest = dis
            closestObj = i

    for i in range(0,3):                                # loop over the coordinate directions
        cObj[i] = objs[closestObj, i]
            
    return cObj

"""
Find the Pasquill Stability Class for the current well-pad conditions assuming that it is daytime
based on:   “Table 2.2.” Workbook of Atmospheric Dispersion Estimates, An Introduction to Dispersion Modeling with Floppy Diskette, by DB Turner, Lewis Publishers, 2000, pp. 2.7.
inputs      v           -   the surface windspeed on the wellpad (m/s)
            temp        -   the outside temperature (F)
            overcast    -   if the conditions outside would be overcast (<= 50%  cloud cover), this is TRUE (assumed to be FALSE)
outputs     stab        -   the stability class for the given conditions (either A,B,C, or D)
"""

def getStab(v, temp, overcast):

    # ---------------------------------------
    # Find the Class Based on the Above Table
    # ---------------------------------------

    if overcast:                                        # if the wellpad is overcast, set the condition to D and move on
        stab = 'D'
        
    else:                                               # otherwise, use the following if statements to find the corresponding class
        if v < 2.0:
            if temp < 35.0:
                stab = 'B'
            elif temp > 65.0:
                stab = 'A'
            else:
                stab = 'B'
                
        elif v < 3.0:
            if temp < 35.0:
                stab = 'C'
            elif temp > 65.0:
                stab = 'B'
            else:
                stab = 'B'
                
        elif v < 5.0:
            if temp < 35.0:
                stab = 'D'
            elif temp > 65.0:
                stab = 'B'
            else:
                stab = 'C'
                
        elif v < 6.0:
            if temp < 35.0:
                stab = 'D'
            elif temp > 65.0:
                stab = 'C'
            else:
                stab = 'D'
                
        else:
            if temp < 35.0:
                stab = 'D'
            elif temp > 65.0:
                stab = 'C'
            else:
                stab = 'D'

    return stab

"""
Flux Plane Bounds
find the flux plane bounds as the Pasquill-Gifford dispersion coefficients in the forms outlined by DB Turner
based on:   “Table 2.3.” Workbook of Atmospheric Dispersion Estimates, An Introduction to Dispersion Modeling with Floppy Diskette, by DB Turner, Lewis Publishers, 2000, pp. 2.8.
    and     “Table 2.3.” Workbook of Atmospheric Dispersion Estimates, An Introduction to Dispersion Modeling with Floppy Diskette, by DB Turner, Lewis Publishers, 2000, pp. 2.11.
inputs      stability   -   the stability class for the given conditions (either A,B,C, or D)
            xbar        -   the distance from the drone to the closest source object (m)
outputs     sigma       -   1D array containing the dispersion coefficients (m)
"""

def dispersion(stability, xbar):

    # ----------------------
    # Variable Instantiation
    # ----------------------

    sigma = n.zeros([2])
    xbar = xbar / 1000.0            # convert xbar from m to km

    # ---------------
    # Finding sigma_y
    # ---------------

    # first, find T based off of the stability condition
    if stability == 'A':
        T = 24.167 - 2.5334*m.log(xbar)
    elif stability == 'B':
        T = 18.333 - 1.8096*m.log(xbar)
    elif stability == 'C':
        T = 12.5 - 1.0857*m.log(xbar)
    else:
        T = 8.3333 - 0.72382*m.log(xbar)

    # compute sigma_y
    sigma[0] = 1000 * xbar * m.tan(T*m.pi/180.0)/2.15

    # ---------------
    # Finding sigma_z
    # ---------------

    # first, find a and b based off of the stability condition
    "NOTE: this approach assumes a distance of <= 100m to the closest potential source"
    if stability == 'A':
        a = 122.8
        b = 0.9447
    elif stability == 'B':
        a = 90.673
        b = 0.93198
    elif stability == 'C':
        a = 61.141
        b = 0.91465
    else:
        a = 34.459
        b = 0.86974

    # compute sigma_z
    sigma[1] = a*(xbar**b)

    return sigma

"""
Outline of the Flux Plane
creates all of the final waypoints used in the creation of the flux plane
NOTE: this section is fully independent of the rest of the code. as long as you create a method for traversing the rectangular flux plane based on the 4 given waypoints, you are good to do whatever in here this is only a sample method
inputs      bounds      -   2D array that contains the coordinates of each bound of the flux plane ([i,j] i is the waypoint ID (looking at source bottom left = 0, top left = 1, bottom right = 2, top right = 3)
                            and j is the coordinate direction (x=0,y=1,z=2))
            res         -   the vertical resolution of the flux plane
outputs     wps         -   2D array containing the coordinates of fully developed flux plane ([i,j] i is the waypoint ID and j is the coordinate direction (x=0,y=1,z=2))
"""

def outline(bounds, res):

    # ------------------------
    # Filling in the wps Array
    # ------------------------

    wps = n.zeros([2*m.ceil((bounds[1,2] - bounds[0,2])/res+1), 3])                    # preallocate wps

    for i in range(0, int((n.shape(wps)[0]-2)/2)):                                      # loop over the waypoints in pairs of left and right save the last pair
        for j in range(0,2):                                                            # loop over the x and y coordinates
            wps[2*i,j] = bounds[1 + (i%2),j]
            wps[2*i+1,j] = bounds[1 + ((i+1)%2),j]

        wps[2*i,2] = bounds[1,2] - res*i                                                # fill in the z coordinate
        wps[2*i+1,2] = bounds[1,2] - res*i

    wps[n.shape(wps)[0]-2, 0] = wps[n.shape(wps)[0]-3, 0]                               # fill in the last rows
    wps[n.shape(wps)[0]-2, 1] = wps[n.shape(wps)[0]-3, 1]
    wps[n.shape(wps)[0]-2, 2] = bounds[0, 2]
    wps[n.shape(wps)[0]-1, 0] = wps[n.shape(wps)[0]-4, 0]
    wps[n.shape(wps)[0]-1, 1] = wps[n.shape(wps)[0]-4, 1]
    wps[n.shape(wps)[0]-1, 2] = bounds[0, 2]

    return wps

"""
Flux Plane Waypoints
basically just the glue through which all the above functions interact
finds all of the requisite waypoints for the flux plane and returns a 2D array containing the x, y, and z coordinates of each waypoint ([i,j] i = waypoint number, j = coordinate (x=0,y=1,z=2))
inputs      x           -   the current x position of the drone (m)
            y           -   the current y position of the drone (m)
            z           -   the current x position of the drone (m)
            objs        -   2D array containing the coordinates of the objects on the wellpad ([i,j] i = object ID, j = coordinate (x=0,y=1,z=2))
            v           -   the surface windspeed on the wellpad (m/s)
            theta       -   the wind direction represented as the angle in the range [0, 2pi] with 0 pointing directly east (radians)
            temp        -   the outside temperature (F)
            overcast    -   if the conditions outside would be overcast (<= 50%  cloud cover), this is TRUE (assumed to be FALSE)

            NOTE: the following parameters are used ONLY for the specific method of defining the flux plane and can be freely changed, along with the outline(...) function, to change the way in which the flux plane is fully outlined
                    without changing the fundamental theory behind the method used to define the bounds of flux plane generation, simply overwrite the outline(...) function with your method of choice and add the requisite variables
            res         -   the vertical resolution for the flux plane (m)

outputs     wps         -   2D array containing the (x,y,z) for each waypoint in the flux plane
"""

def fluxPlane(x, y, z, objs, v, theta, temp, res, overcast=False):
    
    # -----------------------------------
    # Finding the Dispersion Coefficients
    # -----------------------------------
    
    closeObj = getClosestObject(x,y,z,objs)             # find the coordinates of the closest potential leak source
    xbar = m.sqrt((closeObj[0] - x)**2 + (closeObj[1] - y)**2 + (closeObj[2] - z)**2)          # the distance between the drone and the closest potential leak source
    stability = getStab(v, temp, overcast)              # find the Pasquill Stability Class
    sigma = dispersion(stability, xbar)                 # find the y and z dispersion coefficients, which are the bounds of the flux plane
    print(closeObj)
    # ------------------------------------
    # Finding the Bounds of the Flux Plane
    # ------------------------------------

    # rotate the flux plane to be perpindicular to the wind direction
    xhat1 = x + sigma[0]*m.sin((360-theta)*m.pi/180)                   # the x and y coordinates of the flux plane bounds
    yhat1 = y + sigma[0]*m.cos((360-theta)*m.pi/180)
    xhat2 = x - sigma[0]*m.sin((360-theta)*m.pi/180)
    yhat2 = y - sigma[0]*m.cos((360-theta)*m.pi/180)
    
    # z coordinates for the flux plane bounds
    if z - sigma[1] < 0.0: 
        zhat1 = 0.0
    else:
        zhat1 = z - sigma[1]

    zhat2 = z + sigma[1]
    # filling in the bounds array
    bounds = n.array([[xhat1, yhat1, zhat1], [xhat1, yhat1, zhat2], [xhat2, yhat2, zhat1], [xhat2, yhat2, zhat2]])

    # -----------------
    # Filling wps Array
    # -----------------

    wps = outline(bounds, res)                          # finds the wps array using the outline method
    
    return wps
