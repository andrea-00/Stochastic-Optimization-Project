import numpy as np
from sklearn.preprocessing import MinMaxScaler, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from scipy.optimize import minimize
import matplotlib.pyplot as plt

class SurfaceResponseOptimizer:
    def __init__(self, ranges, n_reps, degree=2, model=None, scaler=None, stability_monitor = None, verbose: bool = True):
        self.ranges = ranges
        self.n_products = len(ranges)
        self.n_reps = n_reps
        self.degree = degree
        self.dict_response = self._initialize_dict_response()
        self.model = model if model else LinearRegression()
        self.scaler = scaler if scaler else MinMaxScaler(feature_range=(-1, 1))
        self.poly = PolynomialFeatures(degree=self.degree)
        self.stability_monitor = stability_monitor
        self.response_function = None
        self.verbose = verbose

        if self.verbose:
            print(f"SurfaceResponseOptimizer initialized with {self.n_products} variables and {self.n_reps} repetitions.")

    def _initialize_dict_response(self):
        """ Initializes the dictionary to store the simulation results. """
        ranges = [range(int(self.ranges[i][0]), int(self.ranges[i][1]) + 1) for i in range(self.n_products)]
        return {tuple(comb): {} for comb in np.array(np.meshgrid(*ranges)).T.reshape(-1, self.n_products)}

    def _run_simulations(self, simulation_function):
        """ Runs simulations for all combinations of inputs. """
        if self.verbose:
            print("Running simulations...")

        for key in self.dict_response.keys():
            if self.stability_monitor:
                self.stability_monitor.in_sample_stability(list(key), None)
            tmp = np.array([simulation_function(list(key), seed=None) for _ in range(self.n_reps)])
            self.dict_response[key] = np.mean(tmp)
        
        if self.verbose:
            print("Simulations completed.")
        

    def _create_metamodel_dataset(self):
        """ Creates the dataset for the metamodel. """
        X, y = zip(*self.dict_response.items())
        X = np.array(X)
        y = np.array(y)
        X_scaled = self.scaler.fit_transform(X)  # Normalize the inputs
        X_poly = self.poly.fit_transform(X_scaled)
        return X_poly, y

    def _create_response_function(self):
        """ Creates the response function from the trained model. """
        if self.model is None:
            raise ValueError("The model has not been trained.")
        
        def response_function(*args):
            input_values = np.array([args]).reshape(1, -1)
            input_scaled = self.scaler.transform(input_values)
            poly_features = self.poly.transform(input_scaled)
            return self.model.predict(poly_features)[0]
        
        return response_function

    def optimize(self, simulation_function):
        """ Runs simulations, trains the model, and optimizes. """
        self._run_simulations(simulation_function)

        if self.verbose:
            print("Training the metamodel...")

        X, y = self._create_metamodel_dataset()
        self.model.fit(X, y)
        r2_score = self.model.score(X, y)

        if self.verbose:
            print(f"R² Score of the model: {r2_score:.4f}")

        self.response_function = self._create_response_function()

        if self.verbose:
            print("Optimizing the response function...")

        def objective_function(x):
            return -self.response_function(*x)

        bounds = self.ranges
        initial_guess = [(b[0] + b[1]) / 2 for b in bounds]
        result = minimize(objective_function, initial_guess, bounds=bounds, method='L-BFGS-B')

        if not result.success:
            print(f"Warning: Optimization failed ({result.message}). Returning the best point found.")

        optimal_point = np.clip(np.round(result.x), [b[0] for b in bounds], [b[1] for b in bounds]).astype(int)
        optimal_value = -result.fun

        return optimal_point, optimal_value

    def plot_response_surface(self):
        """ Displays the response surface (only for 2 variables). """
        if self.n_products != 2:
            raise ValueError("Visualization is supported only for 2 variables.")
        
        x1_vals = np.linspace(self.ranges[0][0], self.ranges[0][1], 100)
        x2_vals = np.linspace(self.ranges[1][0], self.ranges[1][1], 100)
        x1_grid, x2_grid = np.meshgrid(x1_vals, x2_vals)
        z_vals = np.array([[self.response_function(x1, x2) for x1 in x1_vals] for x2 in x2_vals])

        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(x1_grid, x2_grid, z_vals, cmap='viridis', edgecolor='none')
        ax.set_title("Response Surface")
        ax.set_xlabel("x1")
        ax.set_ylabel("x2")
        ax.set_zlabel("Response f(x1, x2)")
        plt.show()

        plt.figure(figsize=(8, 6))
        contour = plt.contourf(x1_grid, x2_grid, z_vals, cmap='viridis', levels=50)
        plt.colorbar(contour)
        plt.title("Contour Plot of the Response Surface")
        plt.xlabel("x1")
        plt.ylabel("x2")
        plt.show()
