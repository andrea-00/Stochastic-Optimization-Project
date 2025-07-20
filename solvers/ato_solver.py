import numpy as np
import gurobipy as gp
from gurobipy import GRB
from instances.store import Store

class ATO:
    """Class for optimizing production and demand simulation with constraints."""
    def __init__(self, store: Store, n_scenarios: int = 100, verbose: bool = False):
        self.store = store
        self.N_SCENARIOS = n_scenarios
        self.PROBABILITY = 1 / self.N_SCENARIOS
        self.verbose = verbose

        if self.verbose:
            print(f"Initializing ATO model with {self.N_SCENARIOS} scenarios...")

        # Initialize optimization model
        self.model = gp.Model("ATO")
        self.model.setParam('OutputFlag', 0)  # Suppress Gurobi output

        # Decision variables
        self._add_base_variables()

        # Add constraints to the model
        self._add_base_constraints()

        # Dictionary to store registered objective functions
        self.objective_functions = {}

        # Register and set the default objective function
        self.register_objective("default", self._default_objective)
        self.current_objective = "default"

        if self.verbose:
            print("ATO model initialized successfully!")

    def _add_base_variables(self):
        """Add decision variables to the model."""
        self.x = self.add_new_variable(self.store.N_ITEMS, name="x", vtype=GRB.INTEGER, lb=0)
        self.y = self.add_new_variable((self.store.N_PRODUCTS, self.N_SCENARIOS), name="y", vtype=GRB.CONTINUOUS, lb=0)

    def _add_base_constraints(self):
        """Add all constraints to the optimization model."""
        self.add_constraint(
            (gp.quicksum(self.store.CONNECTION_MATRIX[j, i] * self.y[j, s] for j in range(self.store.N_PRODUCTS)) <= self.x[i]
                for i in range(self.store.N_ITEMS) for s in range(self.N_SCENARIOS)),
            name="constraint_on_amount_of_components"
        )

        self.add_constraint(
            (gp.quicksum(self.store.PROCESS_TIMES[m, i] * self.x[i] for i in range(self.store.N_ITEMS)) <= self.store.MACHINE_CAPACITY[m]
             for m in range(self.store.N_MACHINES)),
            name="production_capacity_constraint"
        )
    
    def _default_objective(self, prices: np.ndarray):
        """Default objective function: Minimize cost & maximize demand revenue."""
        return (
            - gp.quicksum(self.store.COSTS[i] * self.x[i] for i in range(self.store.N_ITEMS))
            + self.PROBABILITY * gp.quicksum(prices[j] * self.y[j, s] for j in range(self.store.N_PRODUCTS) for s in range(self.N_SCENARIOS))
        )

    def register_objective(self, name: str, objective_function, sense=GRB.MAXIMIZE):
        """Register a new objective function."""
        self.objective_functions[name] = (objective_function, sense)

    def set_objective(self, name: str, *args, **kwargs):
        """Set the active objective function."""
        if name not in self.objective_functions:
            raise ValueError(f"Objective '{name}' not found. Register it first.")
        
        self.current_objective = name
        objective_function, sense = self.objective_functions[name]
        self.model.setObjective(objective_function(*args, **kwargs), sense=sense)

        if self.verbose:
            print(f"Objective function set to: {name}")

    def add_new_variable(self, shape, name: str, vtype=GRB.CONTINUOUS, lb=0):
        """Add new decision variables with lower bound set by default."""
        if isinstance(shape, int):
            return self.model.addVars(shape, vtype=vtype, lb=lb, name=name)
        elif isinstance(shape, tuple):
            return self.model.addVars(*shape, vtype=vtype, lb=lb, name=name)
        else:
            raise ValueError("Parameter 'shape' must be an integer or a tuple of integers.")

    def add_constraint(self, constraint_expr, name: str):
        """Add constraints to the model."""
        if isinstance(constraint_expr, list) or hasattr(constraint_expr, '__iter__'):
            return self.model.addConstrs(constraint_expr, name=name)
        return self.model.addConstr(constraint_expr, name=name)

    def remove_constraint(self, constraint):
        """Safely remove a constraint if it exists in the model."""
        self.model.remove(constraint)

    def get_n_scenarios(self) -> int:
        """Returns the number of scenarios"""
        return self.N_SCENARIOS

    def set_n_scenarios(self, n_scenarios: int):
        """Update the number of scenarios dynamically."""
        if self.verbose:
            print(f"Setting n_scenarios: {self.N_SCENARIOS}->{n_scenarios}")

        self.N_SCENARIOS = n_scenarios
        self.PROBABILITY = 1 / self.N_SCENARIOS

        # Reinitialize the model
        self.model = gp.Model("ATO")
        self.model.setParam('OutputFlag', 0)

        # Re-add variables and constraints
        self._add_base_variables()
        self._add_base_constraints()

        if self.verbose:
            print("Model n_scenarios updated successfully!")

    def run_simulation(self, prices: np.ndarray, seed: int = None) -> float:
        """Run the optimization simulation for a given set of prices."""
        if self.verbose:
            print(f"Running simulation with {self.N_SCENARIOS} scenarios...")

        np.random.seed(seed)
        demand = self.store.get_demand_distribution()(prices)(self.N_SCENARIOS, seed)

        demand_constraints = self.add_constraint(
            (self.y[j, s] <= demand[j, s] for j in range(self.store.N_PRODUCTS) for s in range(self.N_SCENARIOS)),
            name="constraint_on_demand"
        )

        self.set_objective(self.current_objective, prices)

        if self.verbose:
            print("Optimizing the model...")

        self.model.optimize()

        if self.verbose:
            if self.model.status == GRB.OPTIMAL:
                print("Optimization successful!")
            elif self.model.status == GRB.INFEASIBLE:
                print("Warning: Model is infeasible. Consider relaxing constraints.")
            elif self.model.status == GRB.UNBOUNDED:
                print("Warning: Model is unbounded. Check for missing constraints.")
            else:
                print(f"Optimization ended with status {self.model.status}")

        self.remove_constraint(demand_constraints)

        if self.model.status == GRB.OPTIMAL:
            return self.model.ObjVal
        return np.nan
