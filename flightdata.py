import numpy as np 
import pandas as pd
from fastkml import kml
import pymap3d as pm

class FlightData:

    def __init__(self):
        self.origin = None

    # imports wellpad data from .kml file
    def import_wellpad_components(self, filename):
        self.wellpad_components = np.array([])

        with open(filename, 'rt') as myfile:
            doc = myfile.read().encode('utf-8')

        k = kml.KML()
        k.from_string(doc)
        f1 = list(k.features())
        f2 = list(f1[0].features())
        f3 = list(f2[0].features())

        for placemark in f3:
            component, self.origin = placemark_to_component(placemark, self.origin)
            self.wellpad_components = np.append(self.wellpad_components, component)

    def test_func(self):
        print('hello')

    # imports flight run data
    def import_inflight_measurements(self, filename):
        print('running')
        csv = pd.read_csv(filename)
        col_renames = {
            'GPS_Time(s)' : 'time',
            'Wind_Velocity(m/s)' : 'wind_speeds',
            'Wind_Direction(deg)' : 'wind_directions',
            'CH4(vmr)' : 'ch4_conc',
            'Latitude(DD)' : 'lat',
            'Longitude(DD)' : 'lon',
            'LiDAR_Alt(m)' : 'alt'
        }
        
        csv = csv.rename(columns=col_renames)
        ecef_x, ecef_y, ecef_z = pm.geodetic2ecef(csv['lat'],csv['lon'],csv['alt'])
        if self.origin is None:
            self.origin = np.array([csv['lat'][0], csv['lon'][0], csv['alt'][0]])
        csv['x'], csv['y'], csv['z'] = pm.ecef2enu(ecef_x, ecef_y, ecef_z, self.origin[0], self.origin[1], self.origin[2])
        self.inflight_data = csv


class WellpadComponent:

    def __init__(self, pos, name):
        self.pos = pos
        self.name = name
        self.get_type()
        self.assign_leak_likelihood()
        self.leak_detected = False
        self.p_arr = None
        self.final_p_arr = None

    # calculate wellpad component type from description
    def get_type(self):
        pass

    # uses Dr. David Allen's statistics to quantify the likelihood of a leak
    # given the type of the wellpad
    def assign_leak_likelihood(self):
        return 1.0

    def update_p_arr(self, p=None):
        if p is None:
            p = self.p_arr[-1,:]
        if self.p_arr is None:
            self.p_arr = np.array([p])
        else:
            self.p_arr = np.vstack((self.p_arr, p))


def placemark_to_component(placemark, origin):
    point = placemark.geometry
    if origin is None:
        origin = np.array([point.y, point.x, point.z])
    ecef_x, ecef_y, ecef_z = pm.geodetic2ecef(point.y,point.x,point.z)
    x,y,z = pm.ecef2enu(ecef_x, ecef_y, ecef_z, origin[0], origin[1], origin[2])
    pos = np.array([x,y,z])
    name = placemark.description
    
    return WellpadComponent(pos, name), origin
