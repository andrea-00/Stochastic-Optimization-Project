import numpy as np
from instances.fashion_store import FashionStore
from solvers.ato_solver import ATO
from solvers.surface_response import SurfaceResponseOptimizer
import json


file_path = './settings/small_fashion_solver.json'
try:
    with open(file_path, "r", encoding="utf-8") as file:
        params = json.load(file)
except FileNotFoundError:
    print(f"Error: file '{file_path}' not found.")
except json.JSONDecodeError:
    print(f"Error: file '{file_path}' does not contain valid JSON.")


fashion_store = FashionStore(params, 'gruppo4', 'casual', 'Turin')
ato = ATO(store=fashion_store, n_scenarios=100)
optimizer = SurfaceResponseOptimizer(ranges=[(25, 50), (35, 60)], n_reps=10)
best_x, max_y = optimizer.optimize(ato.run_simulation)
print(f'best prices: {best_x}, revenue: {max_y}')
optimizer.plot_response_surface()
print(f'calculated revenue: {ato.run_simulation(np.array(best_x))}', 337517)
print(f'calculated revenue: {ato.run_simulation(np.array(best_x), 343572)}')
