from tsp_solver.greedy import solve_tsp
import matplotlib.pyplot as plt
import matplotlib.patches as ptch
import math
import numpy as np
from scipy import interpolate
from mathutils.geometry import intersect_point_line


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
     def AvoidanceDistance(self, p1, p2):
          path = [] 
          x1 = p1[0:2]
          x2 = p2[0:2]
          # Only two shapes: cylinder and rectangular prism
          if(self.shape == 'tank'):
               # Buffer distance
               r = self.bounds + 3
               center = self.location[0:2]

               # Calculate the distance from the path to the center of the cylinder
               nearest_point = intersect_point_line(center,x1,x2)
               # Test if nearest point is on the line segment
               if(nearest_point[1] < 0 or nearest_point[1] > 1):
                    return 0

               nearest_point_vector = np.array(nearest_point[0][:] - center)

               dist_to_center = np.linalg.norm(nearest_point_vector)
               theta = math.atan2(nearest_point_vector[1], nearest_point_vector[0])

               
               # Line does not intersect cylinder
               if(dist_to_center > r):
                    return 0
               # Return arc path
               else:
                    P = x2 - x1
                    Q = center - x1
                    phi = np.dot(P,Q)/(np.linalg.norm(P)*np.linalg.norm(Q))
                    
                    arc = math.acos(dist_to_center/r)
                    if(phi < 0):
                         angles = np.arange(theta - arc, theta + arc,.1)
                    else:
                         angles = np.arange(theta + arc, theta - arc,-.1)
                    for angle in angles:
                         path.append([r*math.cos(angle), r*math.sin(angle)] + center)
                    return path

          ## At the moment, this returns the distance around the perimeter the quad would go, not the path
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

               # If no points of intersection are found, the path doesn't intersect the object
               if points.size > 2:
                    # The distance along the perimeter will be used to calculate the avoidance distance
                    perimeter = 2*(np.linalg.norm(o2 - [o1[0], o2[1]]) + np.linalg.norm(o2 - [o2[0], o1[1]]))

                    diag_rect = np.linalg.norm([o2 - o1])
                    diag_points = np.linalg.norm([points[1] - points[0]])

                    return (diag_points/diag_rect)*perimeter

               return 0

def GeneratePath(x, WellpadComponents, WindDir):
     """
     Insert code to either read stored data on the wellpad components or load
     data from kml files. This depends on how we want to structure our code.
     """
     
     equipment = []
     for component in WellpadComponents:
          """
          if component.get_type() == 'tank':
               obj = Object(component.size, component.get_type(), component.location)
          else:
               obj = Object(np.asarray([component.location - component.size/2, \
                    component.location + component.size/2], \
                    component.get_type(), component.location))
          """
          
          obj = Object(.1, 'tank', component.pos)
          equipment.append(obj)
     
     for point in x:
          point[0] += 4*math.cos(WindDir*math.pi/180)
          point[1] += 4*math.sin(WindDir*math.pi/180) 
     """
     # Test Waypoints
     x = 40*np.random.rand(5,2)
     
     # Test Objects
     equipment = []
     for e in range(0,5):
          
          o = Object(2*np.random.rand(), 'tank', 40*np.random.rand(2))
          
          equipment.append(o)
     """     

     # Stores the distances between waypoints
     Distance_Matrix = []
     # Stores whether or not a path is blocked by an object
     Avoidance_Matrix = []
     # Stores paths around objects
     Path_Matrix = []

     for i in range(0,x[:,0].size):
          # Stores the distance from one waypoint to all other waypoints
          edge_dist = []
          # Stores booleans of whether or not an object blocks the path between waypoints.
          objects_in_path = []
          # Stores a path around any interfering objects
          Avoiding_Path = []

          for j in range(0,i):
               # Total distance around objects in path
               dist = 0
               path_around_obj = []
               for obj in equipment:
                    path_1 = obj.AvoidanceDistance(x[i], x[j])
                    if path_1 != 0:
                         for d in path_1:
                              path_around_obj.append(d)
                         for p in range(1,len(path_1)):
                              dist += np.linalg.norm(path_1[p] - path_1[p-1])
               
               edge_dist.append(dist)
               objects_in_path.append(dist > 0)
               Avoiding_Path.append(path_around_obj)
          
          Path_Matrix.append(Avoiding_Path)
          Distance_Matrix.append(edge_dist)
          Avoidance_Matrix.append(objects_in_path)

     Path_Matrix = np.asarray(Path_Matrix)
     path = solve_tsp(Distance_Matrix)
     x_ = [x[path[0]][0]]
     y_ = [x[path[0]][1]]
     for i in range(1,len(path)):
          if(path[i] < path[i-1]):
               path1 = path[i-1]
               path2 = path[i]
          else:
               path1 = path[i]
               path2 = path[i-1]

          if Avoidance_Matrix[path1][path2]:
               path_to_add = np.asarray(Path_Matrix[path1][path2])
               # Flip the array if the path order is opposite to the append direction
               if (np.linalg.norm(path_to_add[len(path_to_add) - 1] - [x_[-1], y_[-1]] < \
                    np.linalg.norm(path_to_add[0] - [x_[-1], y_[-1]]))):
                    path_to_add = np.flipud(path_to_add)

               for point in path_to_add:
                    x_.append(point[0])
                    y_.append(point[1])

          x_.append(x[path[i]][0])
          y_.append(x[path[i]][1])


     # Waypoints of the new path
     if(path[0] < path[-1]):
               path1 = path[-1]
               path2 = path[0]
     else:
          path1 = path[0]
          path2 = path[-1]

     if Avoidance_Matrix[path1][path2]:
          path_to_add = np.asarray(Path_Matrix[path1][path2])
          # Flip the array if the path order is opposite to the append direction
          if (np.linalg.norm(path_to_add[len(path_to_add) - 1] - [x_[-1], y_[-1]] < \
               np.linalg.norm(path_to_add[0] - [x_[-1], y_[-1]]))):
               path_to_add = np.flipud(path_to_add)

          for point in path_to_add:
               x_.append(point[0])
               y_.append(point[1])
               
     x_.append(x[path[0]][0])
     y_.append(x[path[0]][1])
     np.append(x,x[0])
     #Path Plotting with Objects
     plt.plot(x_,y_,'-o')
     #for i in path:
          #plt.plot(x[i][0],x[i][1],'o',ms=8)
     plt.plot(x_[0],y_[0],'o',ms=10)
     plt.plot(x[:,0],x[:,1],'o',ms=8)

     ax = plt.gca()

     for obj in equipment:
          if obj.shape == 'tank':
               ax.add_patch(ptch.Circle(obj.location, obj.bounds))
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


     plt.tight_layout()
     plt.show()

     return np.array([x_, y_])