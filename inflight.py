import pandas as pd
import numpy as np
from .confusionmat import ConfusionMatrix

class InFlight:

    def __init__(self, wellpad_components, Q_min=3, window_size=10):
        self.wellpad_components = wellpad_components
        self.baseline = None
        self.measurements = None
        self.Q_min = Q_min
        self.window_size = window_size


    # load measurements to the baseline measurement category
    def load_baseline_measurement(self, measurement):
        if self.baseline is None:
            self.baseline = measurement
        else:
            self.baseline = pd.concat([self.baseline, measurement])

    # call when all baseline measurements have been taken
    def complete_baseline_measurements(self):
        self.baseline_mean = np.mean(self.baseline['ch4_conc'])
        self.baseline_std = np.std(self.baseline['ch4_conc'])
        self.create_confusion_mat()

    # loads a measurement at a single time point
    # calculates confusion matrix wrt to all wellpad components
    def load_measurement(self, measurement):
        if self.measurements is None:
            self.measurements = measurement
        else:
            self.measurements = pd.concat([self.measurements, measurement])

        self.update_confusion_mat()

    def trigger_flux_plane(self):
        pass

    # creates confusion matrices
    def create_confusion_mat(self):
        self.confusion_mat = ConfusionMatrix()
        self.confusion_mat.set_baseline_model_parameters(self.baseline_mean, self.baseline_std, self.Q_min)

    # computes confusion matrix values using sliding window
    def update_confusion_mat(self):
        size = self.measurements.shape[0]
        idx = max(size - self.window_size,0)
        indices = np.arange(idx,size)
        measurements = self.measurements.iloc[indices]
        for component in self.wellpad_components:
            p_arr = self.confusion_mat.test_measurements(measurements, component.pos)
            component.update_p_arr(p_arr)

    # to be called once flight has completed or to evaluate whether
    # to finish the flight. This can be used to determine
    def finish_flight(self):
        pass