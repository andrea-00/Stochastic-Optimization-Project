# ATO Simulation and Optimization Framework

## Overview
This repository provides a simulation and optimization framework for a stochastic **Assemble-to-Order (ATO)** system. This study optimizes item pricing by incorporating price-demand dependencies, treating the ATO model as a black box that returns revenue given a set of item prices. The framework uses the **Surface Response Method** to identify the revenue-maximizing pricing strategy.

Key features include:
- **Stochastic demand modeling** for retail (e.g., fashion stores).
- **Surface Response Optimization** to enhance decision-making.
- **In-Sample Stability Monitoring** to ensure reliable simulation results.

The framework is designed to optimize product configurations, manufacturing processes, and pricing strategies.

---

## Methodology

The optimization process is based on three core components:

### 1. Assemble-to-Order (ATO) Model
The ATO system assembles products from components only after a customer places an order, reducing inventory costs. In our stochastic model, demand is influenced by price, and the objective is to find the pricing strategy that maximizes revenue based on simulated demand scenarios. The core optimization problem is formulated as:
$max_{x\in\mathbb{R}^{\prime},y(\omega)\in\mathbb{R}^{J}}-\sum_{i\in T}C_{i}x_{i}+\mathbb{E}[\sum_{j\in J}P_{j}y_{j}(\omega)]$

### 2. Surface Response Method
This technique is used to model and optimize the relationship between item prices and expected revenue. By fitting a polynomial regression metamodel to the revenue data obtained from simulations, we can efficiently navigate the price space to find the optimal configuration that maximizes revenue.

### 3. In-Sample Stability
To ensure the reliability of our revenue estimates, we perform an in-sample stability analysis. The number of demand scenarios is iteratively increased until the revenue estimates converge within a predefined confidence interval, balancing computational cost with statistical reliability. The stopping condition is met when the confidence interval for the stability measure contains zero.

---

## Key Results

The methodology was first applied to a two-product case to allow for visualization of the revenue response surface.

| ![3D Surface Plot](assets/surface_3d.png) | ![Contour Plot](assets/surface_contour.png) |
|:-------------------------------------------:|:------------------------------------------:|
| *Figure 1: 3D visualization of the revenue response surface.* | *Figure 2: Contour plot showing optimal price regions.* |

The impact of the number of scenarios on the stability of the results was evaluated. The table below summarizes the outcomes for the two-product case.

| Scenario | $R^{2}$ Score | Best Prices | Optimized Revenue |
|:--------:|:-------------:|:-----------:|:-----------------:|
| 100 | 0.9033 | [36, 47] | 80.