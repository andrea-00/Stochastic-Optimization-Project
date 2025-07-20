import numpy as np
from instances.store import Store

# Classe specifica per negozi di moda
class FashionStore(Store):
    def __init__(self, params: dict, brand_name: str, brand_focus: str, location: str):
        """
        Initializes the FashionStore instance with brand details and location.
        Registers and sets the default demand distribution.
        """
        super().__init__(params)
        self.brand_name = brand_name
        self.brand_focus = brand_focus
        self.location = location
        
        # Register and set the default demand distribution
        self.register_demand_distribution("default", self._default_demand_distribution)
        self.set_demand_distribution("default")
    
    def get_features(self) -> dict:
        """Returns key characteristics of the fashion store."""
        return {
            "type": "fashion store",
            "name": self.brand_name,
            "brand_focus": self.brand_focus,
            "location": self.location,
            "items": self.ITEMS,
            "products": self.PRODUCTS
        }
    
    def set_params(self, params: dict):
        """
        Sets the store parameters including items, products, machines, and costs.
        Also computes demand parameters to avoid redundant calculations.
        """
        self.ITEMS = params['items']
        self.PRODUCTS = params['products']
        self.MACHINES = params['machines']
        self.COSTS = np.array(params['costs'])
        self.MACHINE_CAPACITY = np.array(params['machine_capacities'])
        self.PROCESS_TIMES = np.array(params['process_times'])
        self.CONNECTION_MATRIX = np.array(params['connection_matrix'])

        # Simulation parameters
        self.N_ITEMS = len(self.ITEMS)
        self.N_PRODUCTS = len(self.PRODUCTS)
        self.N_MACHINES = len(self.MACHINES)

        # Compute demand parameters once
        self.MAX_DEMAND = 10
        self.DEMAND_SCALING = 0.45
        self.DEMAND_PARAMETERS = (
            self.MAX_DEMAND + self.DEMAND_SCALING * (self.CONNECTION_MATRIX @ self.COSTS.T).reshape(-1, 1)
        )

    def _default_demand_distribution(self, prices: np.ndarray):
        """
        Returns a function that simulates demand based on given prices.
        """
        prices = np.array(prices).reshape(-1, 1)

        if not hasattr(self, "DEMAND_PARAMETERS"):
            self.MAX_DEMAND = 10
            self.DISTRIBUTION_MEAN = 0
            self.DISTRIBUTION_STD = 1
            self.DEMAND_SCALING = np.array(0.45)

            # Compute demand parameters once
            self.DEMAND_PARAMETERS = self.MAX_DEMAND + self.DEMAND_SCALING * (self.CONNECTION_MATRIX @ self.COSTS.T).reshape(-1, 1)

        def simulate(n_scenarios: int, seed: int = None) -> np.ndarray:
            """Simulates the demand given the number of scenarios and seed."""
            np.random.seed(seed)
            demand_perturbation = np.random.normal(loc=0, scale=1, size=(self.N_PRODUCTS, n_scenarios))
            demand = self.DEMAND_PARAMETERS - self.DEMAND_SCALING * prices + demand_perturbation
            return np.round(np.clip(demand, a_min=0, a_max=np.inf))
        
        return simulate
    
    def register_demand_distribution(self, name: str, demand_function: callable):
        """Registers a new demand distribution function."""
        self.demand_distributions[name] = demand_function

    def set_demand_distribution(self, name: str):
        """Sets the active demand distribution."""
        if name not in self.demand_distributions:
            raise ValueError(f"Distribution '{name}' not found. Available: {list(self.demand_distributions.keys())}")
        self.current_demand_distribution = self.demand_distributions[name]

    def get_demand_distribution(self):
        """Returns the currently active demand distribution function."""
        return self.current_demand_distribution
    
    def simulate_demand(self, prices: np.ndarray, n_scenarios: int, seed: int = None) -> np.ndarray:
        """
        Simulates demand using the currently active demand distribution.
        """
        if len(prices) != self.N_PRODUCTS:
            raise ValueError(f"Incorrect number of prices. Expected {self.N_PRODUCTS}, got {len(prices)}.")
        
        demand_function = self.get_demand_distribution()(prices)
        return demand_function(n_scenarios, seed)