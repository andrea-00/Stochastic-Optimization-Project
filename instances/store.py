from abc import ABC, abstractmethod
import numpy as np

# Classe astratta per un generico negozio
class Store(ABC):
    def __init__(self, params: dict):
        """
        Abstract base class for a store.
        """

        # base parameters for the store
        self.ITEMS = params['items']
        self.PRODUCTS = params['products']
        self.MACHINES = params['machines']
        self.COSTS = np.array(params['costs'])
        self.MACHINE_CAPACITY = np.array(params['machine_capacities'])
        self.PROCESS_TIMES = np.array(params['process_times'])
        self.CONNECTION_MATRIX = np.array(params['connection_matrix'])

        # simulation parameters
        self.N_ITEMS = len(self.ITEMS)
        self.N_PRODUCTS = len(self.PRODUCTS)
        self.N_MACHINES = len(self.MACHINES)

        # Demand distribution setup
        self.demand_distributions = {}
        self.current_demand_distribution = None
    
    @abstractmethod
    def get_features(self) -> dict:
        """
        Returns store features as a dictionary.

        Returns:
            dict: A dictionary containing store attributes.
        """
        pass

    @abstractmethod
    def set_params(self, params: dict):
        """
        Sets new parameters for the store.

        Args:
            params (dict): Dictionary containing updated store parameters.
        """
        pass

    @abstractmethod
    def get_demand_distribution(self):
        """
        Retrieves the active demand distribution.

        Returns:
            callable: Function that generates demand distribution.
        """
        pass