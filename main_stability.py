import numpy as np
from scipy.stats import norm
from instances.fashion_store import FashionStore
from solvers.ato_solver import ATO
from solvers.surface_response import SurfaceResponseOptimizer
import json

import numpy as np
from scipy.stats import norm


class StabilityMonitor:
    """
    A class to monitor the stability of a simulation-based model.
    The stopping condition is based on confidence intervals of the estimated stability measure.
    """
    def __init__(
        self,
        simulation_function,
        set_function,
        get_function,
        alpha: float = 0.01,
        initial_n_scenarios: int = 5,
        increment: int = 5,
        min_N: int = 30,
        verbose: bool = False,
    ):
        self.alpha = alpha
        self.initial_n_scenarios = initial_n_scenarios
        self.increment = increment
        self.min_N = min_N
        self.verbose = verbose
        self.phi = []

        self.simulation_function = simulation_function
        self.set_function = set_function
        self.get_function = get_function

    def _stopping_condition(self) -> bool:
        """
        Determines whether the stability condition is met.

        :return: True if the process should continue, False if stability is reached.
        """
        if len(self.phi) < self.min_N:
            return True  # Not enough data to evaluate stability

        mu = np.mean(self.phi)
        sigma = np.std(self.phi, ddof=1)  # Using Bessel's correction
        N = len(self.phi)
        z_alpha = norm.ppf(1 - self.alpha / 2)

        # Compute confidence interval
        lower_bound = mu - z_alpha * (sigma / np.sqrt(N))
        upper_bound = mu + z_alpha * (sigma / np.sqrt(N))

        return not (lower_bound <= 0 <= upper_bound)

    def in_sample_stability(self, *args):
        """
        Runs the stability test by iteratively increasing the number of scenarios.

        :param args: Arguments to be passed to the simulation function.
        """
        if self.verbose:
            print("Starting in-sample stability check...")

        # Retrieve the model's initial number of scenarios
        self.model_n_scenarios = self.get_function() or 0
        n_scenarios = self.initial_n_scenarios

        while self._stopping_condition():
            self.set_function(n_scenarios)
            self.phi.append(self.simulation_function(*args) - self.simulation_function(*args))
            n_scenarios += self.increment

        n_scenarios -= self.increment  # Adjust to last valid value

        if self.verbose:
            print(f"Initial number of scenarios: {self.model_n_scenarios}")
            print(f"Converged number of scenarios: {n_scenarios}")

        # Check if the model's original number of scenarios is sufficient
        if self.model_n_scenarios < n_scenarios:
            if self.verbose:
                print("Warning: The initial number of scenarios is insufficient for stability.")
        else:
            if self.verbose:
                print("The initial number of scenarios is sufficient for stability.")
            self.set_function(self.model_n_scenarios)  # Restore initial setting

        self.phi = []  # Reset data for future runs

        if self.verbose:
            print("Stability check completed.")


file_path = './settings/big_fashion_solver.json'
try:
    with open(file_path, "r", encoding="utf-8") as file:
        params = json.load(file)
except FileNotFoundError:
    print(f"Error: file '{file_path}' not found.")
except json.JSONDecodeError:
    print(f"Error: file '{file_path}' does not contain valid JSON.")

fashion_store = FashionStore(params, 'gruppo3', 'casual', 'Turin')
ato = ATO(store=fashion_store, n_scenarios=100)
stability_monitor = StabilityMonitor(ato.run_simulation, ato.set_n_scenarios, ato.get_n_scenarios)
optimizer = SurfaceResponseOptimizer(ranges=[(35, 45), (50, 60), (40, 50)], n_reps=10, stability_monitor=stability_monitor)
best_x, max_y = optimizer.optimize(ato.run_simulation)
print(f'best prices: {best_x}, revenew: {max_y}')
print(f'calculated revenew: {ato.run_simulation(np.array(best_x))}')
print(f'calculated revenew: {ato.run_simulation(np.array(best_x))}', 343572)