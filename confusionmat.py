import numpy as np 

class ConfusionMatrix:

    def __init__(self):
        pass

    def set_baseline_model_parameters(self, mu, sigma, u, Q_min):
        self.mu = mu
        self.sigma = sigma
        self.u = u
        self.Q_min

    def test_measurements(self, measurements, emission_source):
        """Creates a confusion matrix comparing a set of measurements to an
        emission source. Left side of table assumes conclusion that leak is present.
        Right side assumes conclusion that leak is not present

                | True Pos.  | False Neg. |
                | False Pos. | True Neg.  |

        Parameters
        ----------
        measurements : np.array
            NumPy array of shape (n,4). n is the number of measurements. Each
            row contains the (x,y,z) position of the measurement followed by the
            measurement value
        emission_source : np.array
            NumPy array of length 3 representing the (x,y,z) location of an emission point

        Returns
        ----------
        mat : np.array
            NumPy array of shape (2,2) containing probabilities in form:

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
        p_true_pos, p_false_pos = self.compare_to_leak(measurements, emission_source, Q_to_use)
        p_true_neg, p_false_neg = self.compare_to_baseline(measurements)

        # organizes into matrix for return
        mat = np.array([[p_true_pos, p_false_neg], [p_false_pos, p_true_neg]])
        return mat

    def optimize_Q(self, measurements, emission_source):
        pass

    def compare_to_leak(self, measurements, emission_source, Q):
        pass

    def compare_to_baseline(self, measurements):
        pass