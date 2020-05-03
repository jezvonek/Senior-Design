from tsp_solver.greedy import solve_tsp
import matplotlib.pyplot as plt
import matplotlib.patches as ptch
import math
import numpy as np
from scipy import interpolate


# Contains details about a wellpad component used for path generation
class Object:
     def __init__(self, bounds, shape, location):
          # Bounds for a cylinder is the radius of the cylinder
          # Bounds for a prism are two opposite corners of the prism
          ## Bounds must always be defined in order for a prism: 
               ## point 1 < point 2 for x and y
          self.bounds = bounds
          self.shape = shape
          self.location = location

     # Find the distance of a path around an object between two waypoints
     ## This function only uses the 2D coordinates of the object and path
     def AvoidanceDistance(self, x1, x2): 
          # Only two shapes: cylinder and rectangular prism
          if(self.shape == 'tank'):
               r = self.bounds + 4
               center = self.location[::1]

               # Calculate the distance from the path to the center of the cylinder
               dist_to_center = abs(center[0]*(x2[0] - x1[0]) + center[1]*(x1[1] - x2[1]) \
                    + x1[0]*(x2[1] - x1[1]) + x1[0]*(x2[0] - x1[0]))/math.sqrt(abs((x2[0] - x1[0])**2 + (x2[1] - x1[1]**2)))

               
               # Line does not intersect cylinder
               if(dist_to_center > r):
                    return 0
               # Return arc length
               else:
                    return 2*r*math.acos(dist_to_center/r)

          else:
               # Expand the bounds by 4m
               ## This will not work if the bounds coordinates are not ordered correclty
               o1 = np.array(self.bounds[0] - 4*np.sign(self.bounds[0]))
               o2 = np.array(self.bounds[1] + 4*np.sign(self.bounds[1]))

               # Create a rectangle of line segments
               rect = np.array([
                              [o1, np.array([o2[0], o1[1]]) ], 
                              [ np.array([o2[0], o1[1]]), o2 ], 
                              [ np.array([o1[0], o2[1]]), o2 ], 
                              [ o1, np.array([o1[0], o2[1]]) ]
                              ])

               # Find the points at which the path intersects the prism 
               points = []
               s = x2 - x1
               for segment in rect:
                    r = segment[1] - segment[0]

                    # Calculate location of point at which the lines intersect
                    u = np.cross(s,r)
                    if u == 0:
                         continue
                    p = x1 + s*np.cross((segment[0] - x1), r/u)
                    
                    # Test if the point lies on the segment
                    if (all(p >= segment[0]) and all(p <= segment[1])):
                         points.append(p)
                         if len(points) == 2:
                              break
               
               points = np.asarray(points)

               # If no points of intersection is found, the path doesn't intersect the object
               if points.size > 2:
                    # The distance along the perimeter will be used to calculate the avoidance distance
                    perimeter = 2*(np.linalg.norm(o2 - [o1[0], o2[1]]) + np.linalg.norm(o2 - [o2[0], o1[1]]))

                    diag_rect = np.linalg.norm([o2 - o1])
                    diag_points = np.linalg.norm([points[1] - points[0]])

                    return (diag_points/diag_rect)*perimeter


               return 0

def GeneratePath(x):
     """
     Insert code to either read stored data on the wellpad components or load
     data from kml files. This depends on how we want to structure our code.
     equipment = np.array([])
     for i in wellpad_components:
          component = Object(i.bounds, i.shape, i.location)

     Insert code to read waypoints
     x = waypoints
     """
     # Test Waypoints
     x = 40*np.random.rand(5,2)
     # Test Objects
     equipment = []
     object_types = ['tank', 'other']
     for e in range(0,5):
          if(np.random.rand() < .5):
               o = Object(2*np.random.rand(), 'tank', 40*np.random.rand(2))
          else:
               loc = 40*np.random.rand(2)
               o = Object(np.asarray([loc - 1, loc + 1]), 'other', loc)
          equipment.append(o)


     # Stores the distances between waypoints
     Distance_Matrix = []
     # Stores whether or not a path is blocked by an object
     Avoidance_Matrix = []

     for i in range(0,x[:,0].size):
          # Stores the distance from one waypoint to all other waypoints
          edge_dist = []
          # Stores booleans of whether or not an object blocks the path between waypoints.
          objects_in_path = []

          for j in range(0,i):
               # Total distance around objects in path
               dist = 0

               for obj in equipment:
                    dist = obj.AvoidanceDistance(x[i], x[j])
               
               edge_dist.append(np.linalg.norm(x[i] - x[j]) + dist)
               objects_in_path.append(dist > 0)
          
          Distance_Matrix.append(edge_dist)
          Avoidance_Matrix.append(objects_in_path)

     path = solve_tsp(Distance_Matrix)

     x_ = []
     y_ = []
     for i in path:
          x_.append(x[i][0])
          y_.append(x[i][1])

     # Waypoints of the new path
     x_.append(x[path[0]][0])
     y_.append(x[path[0]][1])

     return np.array([x_, y_])
"""
Path Plotting with Objects

plt.plot(x_,y_,'-o')
plt.plot(x_[0],y_[0],'o',ms=10)

ax = plt.gca()

for obj in equipment:
     if obj.shape == 'tank':
          ax.add_patch(ptch.Circle(obj.location, obj.bounds + 4))
     else:
          ax.add_patch(ptch.Rectangle(obj.bounds[0] - 4*np.sign(obj.bounds[0]),\
               4*(obj.bounds[1][0] - obj.bounds[0][0]), \
               4*(obj.bounds[1][1] - obj.bounds[0][1])))


# Originally used for splines. Unnecessary
#tck,u=interpolate.splprep([x_,y_],s=0)
#x_i,y_i= interpolate.splev(np.linspace(0,1,100),tck)
#plt.plot(x_i, y_i, color='green')

#print(x_i[0])
#print(y_i)

#with open('TSP.txt', 'w') as tsp:
#     for i in range(0,len(x_i)):
#          tsp.write("%d, %d\n" %(x_i[i], y_i[i]))



plt.show()
"""