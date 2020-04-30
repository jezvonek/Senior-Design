import numpy as np 
from concentrationmodel import LeakPresent
import scipy
import math

class ConfusionMatrix:

    def __init__(self):
        pass

    def set_baseline_model_parameters(self, mu, sigma, Q_min):
        """Establishes model parametes

        Parameters
        ----------
        mu : float
            Baseline methane concentration reading mean
        sigma : float
            Baseline methane concentration reading standard deviation
        Q_min : float
            Minimum methane concentration to test for

        """

        self.mu = mu
        self.sigma = sigma
        self.Q_min = Q_min

    def test_measurements(self, measurements, emission_source):
        """Creates a confusion matrix comparing a set of measurements to an
        emission source. Left side of table assumes conclusion that leak is present.
        Right side assumes conclusion that leak is not present. This function will return
        either the left half of the table or the right half of the table

                | True Pos.  | False Neg. |
                | False Pos. | True Neg.  |

        Parameters
        ----------
        measurements : np.array
            NumPy array of shape (n,6). n is the number of measurements. Each
            row contains the (x,y,z) position of the measurement followed by the
            measurement value
        emission_source : np.array
            NumPy array of length 3 representing the (x,y,z) location of an emission point

        Returns
        ----------
        p_arr : np.array
            NumPy array of shape (2) containing either the left half or the right half
            of the confusion matrix

        """

        # assuming an emission is present, optimizes Q using a <insert here> method
        Q_optim = self.optimize_Q(measurements, emission_source)

        # if Q_optim is larger than the minimum we're testing for, we can safely conclude
        # a leak is present. If so, we can compare data points against model with optimized
        # Q value. If not, we compare data points to model with minimized Q value
        if Q_optim > self.Q_min:
                Q_to_use = Q_optim
        else:
                Q_to_use = self.Q_min

        # compares data to leak and baseline models to obtain probabilities for each
        p_leak = self.compare_to_leak(Q_to_use, measurements, emission_source)
        p_noleak = self.compare_to_baseline(measurements)

        # normalizes probabilities
        norm = p_leak + p_noleak
        p_leak = p_leak / norm
        p_noleak = p_noleak / norm

        # organizes into matrix for return
        p_arr = np.array([p_leak, p_noleak])
        return p_arr

    def optimize_Q(self, measurements, source):
        """Optimizes Q using the maximum a posteriori estimate

        Parameters
        ----------
        measurements : pd.dataframe
            Measurements dataframe with columns determined by FlightData.import_inflight_measurements
            function
        source : np.array
            NumPy array containing the (x,y,z) coordinates of the emission source in question

        Returns
        ----------
        float
            Value for Q that fit the measurements most accurately

        """

        def f(Q):
            p, _ = self.compare_to_leak(Q, measurements, source)
            return -p

        #Q = self.Q_min
        res = scipy.optimize.minimize_scalar(f)

        if res.success:
            return res.x
        else:
            raise Exception('Q was not optimized successfully')

    def compare_to_leak(self, Q, measurements, source):
        z_score_array = self.sample_leak_present(Q, measurements, source)
        p = z_scores_to_prob(z_score_array)

        return p

    def compare_to_baseline(self, measurements):
        z_score_array = self.sample_no_leak(measurements)
        p = z_scores_to_prob(z_score_array)

        return p

    def sample_leak_present(self, Q, measurements, source):
        leak_model = LeakPresent(Q, self.sigmay, self.sigmaz, source[2]) # what are sigmay and sigmaz determined from?
        z_score_array = np.array([])
        for index, row in measurements.iterrows():
            pos = np.array([row['x'], row['y'], row['z']])
            conc = leak_model.predict_local_coors(pos, source, row['wind_speeds'], row['wind_directions']) - self.mu
            z_score = (row['ch4_conc'] - conc) / self.sigma
            z_score_array = np.append(z_score_array, z_score)

        return z_score_array

    def sample_no_leak(self, measurements):
        z_score_array = np.array([])
        for index, row in measurements.iterrows():
            z_score = (row['ch4_conc'] - self.mu) / self.sigma
            z_score_array = np.append(z_score_array, z_score)

        return z_score_array


def z_scores_to_prob(z_score_array):
    """Intakes an array of z-scores and outputs the probability of them all occurring

    Parameters
    ----------
    z_score_array : np.array
        NumPy array containing the z-scores

    Returns
    ----------
    prob : np.array
        The total probability

    """

    prob = 1
    for z_score in z_score_array:
        indiv_prob = 1/math.sqrt(2 * math.pi) * math.exp(-(z_score**2) / 2)
        prob = prob * indiv_prob

    return prob
