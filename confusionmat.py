import numpy as np 
from .concentrationmodel import LeakPresent
from scipy.optimize import minimize_scalar
import math

class ConfusionMatrix:

    def __init__(self, multiplier=1):
        self.multiplier = multiplier

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

        p_arr = self.compute_p_arr(Q_to_use, measurements, emission_source)
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
            p_arr = self.compute_p_arr(Q, measurements, source)
            return -p_arr[0]

        res = minimize_scalar(f)

        if res.success:
            return res.x
        else:
            raise Exception('Q was not optimized successfully')

    def compute_p_arr(self, Q, measurements, emission_source):
        # compares data to leak and baseline models to obtain probabilities for each
        z_leak = self.sample_leak_present(Q, measurements, emission_source)
        z_noleak = self.sample_no_leak(measurements)
        
        p_arr = z_scores_to_prob(z_leak, z_noleak)

        return p_arr

    def sample_leak_present(self, Q, measurements, source):
        leak_model = LeakPresent(Q, source[2]) # what are sigmay and sigmaz determined from?
        z_score_array = np.array([])
        for _, row in measurements.iterrows():
            pos = np.array([row['x'], row['y'], row['z']])
            conc = leak_model.predict_local_coors(pos, source, row['wind_speeds'], row['wind_directions']) 
            conc += self.mu
            z_score = (row['ch4_conc'] - conc) / (self.sigma * self.multiplier)
            z_score_array = np.append(z_score_array, z_score)

        return z_score_array

    def sample_no_leak(self, measurements):
        z_score_array = np.array([])
        for _, row in measurements.iterrows():
            z_score = (row['ch4_conc'] - self.mu) / self.sigma
            z_score_array = np.append(z_score_array, z_score)

        return z_score_array


def z_scores_to_prob(z_leak, z_noleak):
    """Intakes an array of z-scores and outputs the probabilities of them all occurring

    Parameters
    ----------
    z_score_array : np.array
        NumPy array containing the z-scores

    Returns
    ----------
    p_arr : np.array
        The probabilities of all the events occuring

    """

    squares1 = (z_leak ** 2) / 2
    squares2 = (z_noleak ** 2) / 2
    try:
        p_ratio = math.exp(np.sum(squares2) - np.sum(squares1)) # p1/p2
    except OverflowError:
        p_ratio = float('inf')
    if math.isinf(p_ratio):
        p1 = 1
        p2 = 0
    else:
        p1 = p_ratio/(1+p_ratio)
        p2 = 1 - p1

    p_arr = np.array([p1,p2])

    return p_arr

    '''
    p_arr = np.array([])
    for i in range(z_leak.shape[0]):
        z1 = z_leak[i]
        z2 = z_noleak[i]
        z_diff = ((z2**2) / 2) - ((z1**2) / 2)
        try:
            p_ratio = math.exp(z_diff) # p1/p2
        except OverflowError:
            p_ratio = float('inf')
        if math.isinf(p_ratio):
            p1 = 1
            p2 = 0
        else:
            p1 = p_ratio/(1+p_ratio)
            p2 = 1 - p1
        if i == 0:
            p_arr = np.array([p1, p2]).astype(float)
        else:
            p_arr[0] = p_arr[0] * p1
            p_arr[1] = p_arr[1] * p2
            norm = p_arr[0] + p_arr[1]
            print(norm)
            if math.isnan(norm):
                raise Exception('!!!!!!!!!!!!!!!!!!!!!')
            p_arr[0] = p_arr[0] / norm
            p_arr[1] = p_arr[1] / norm

    return p_arr
    '''