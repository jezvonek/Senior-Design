import numpy as np 
import pandas as pd
from fastkml import kml
import pymap3d as pm

class FlightData:

    def __init__(self):
        pass

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
            component = placemark_to_component(placemark)
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
        csv['x'], csv['y'], csv['z'] = pm.geodetic2ecef(csv['lat'],csv['lon'],csv['alt'])
        self.inflight_data = csv


class WellpadComponent:

    def __init__(self, pos, name):
        x,y,z = pm.geodetic2ecef(pos[0], pos[1], pos[2])
        self.pos = np.array([x,y,z])
        self.name = name
        self.get_type()
        self.assign_leak_likelihood()
        self.p_arr = None

    # calculate wellpad component type from description
    def get_type(self):
        pass

    # uses Dr. David Allen's statistics to quantify the likelihood of a leak
    # given the type of the wellpad
    def assign_leak_likelihood(self):
        return 1.0

    def update_p_arr(self, p):
        if self.p_arr is None:
            self.p_arr = p
        else:
            self.p_arr = np.vstack((self.p_arr, p))


def placemark_to_component(placemark):
    point = placemark.geometry
    # switch bc kml file reverses latitude and longitude
    # should fix later because this is highly bug prone
    pos = np.array([point.y, point.x, point.z])
    name = placemark.description
    
    return WellpadComponent(pos, name)
