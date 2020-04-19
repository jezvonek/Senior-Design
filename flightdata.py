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

    # imports flight run data
    def import_inflight_measurements(self, filename):
        csv = pd.read_csv(filename)
        self.times = csv['GPS_Time(s)'].to_numpy()
        self.windspeeds = csv['Wind_Velocity(m/s)'].to_numpy()
        self.winddirections = csv['Wind_Direction(deg)'].to_numpy()
        self.methane_concentrations = csv['CH4(vmr)'].to_numpy()

        x = csv['Latitude(DD)'].to_numpy()
        y = csv['Longitude(DD)'].to_numpy()
        z = csv['LiDAR_Alt(m)'].to_numpy()
        self.coordinates = np.transpose(np.vstack((x,y,z)))


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
