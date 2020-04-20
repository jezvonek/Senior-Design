import numpy as np 
import pandas as pd
from fastkml import kml

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
            'Latitude(DD)' : 'x',
            'Longitude(DD)' : 'y',
            'LiDAR_Alt(m)' : 'z'
        }
        csv = csv.rename(columns=col_renames)
        self.inflight_data = csv


class WellpadComponent:

    def __init__(self, pos, name):
        self.pos = pos
        self.name = name
        self.get_type()
        self.assign_leak_likelihood()

    # calculate wellpad component type from description
    def get_type(self):
        pass

    # uses Dr. David Allen's statistics to quantify the likelihood of a leak
    # given the type of the wellpad
    def assign_leak_likelihood(self):
        return 1.0


def placemark_to_component(placemark):
    point = placemark.geometry
    pos = np.array([point.x, point.y, point.z])
    name = placemark.description
    
    return WellpadComponent(pos, name)
